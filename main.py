from pkg_manager import PackageManager
from data_access import database
from data_access.pkg import DebianPackage, VCSInfo, PkgDevelopers
from data_access.pkg_language import SourceLanguage
from data_access.pkg_category import PkgCategory
from data_access.pkg_developer import DeveloperContact, ContactType, \
                                      setup_contact_types, get_developer_contact
from data_access.vcs_type import VCSType, setup_vcs_types, get_vcs_type
from data_access.analysis_info import CodeQLInfo
from pkg_manager import PackageManager, PkgEntry
import os
import subprocess
from typing import Any
import tarfile
from stats_helper import get_project_sloc, get_project_source_language
from .common_utils import path_to_folder, create_folder, is_an_interesting_project

SOURCES_FILE_PATH = "/home/machiry/projects/apt-scraper-utils/data_files/jammydebsource"
DOWNLOAD_PKG_DIR = "/media/machiry/PurS3Disk/debiancodeql/pkgs/"
SRC_URL = "http://mirror.math.ucdavis.edu/ubuntu/"
FILTERED_CATEGORIES = ["text", "python", "php", "kernel", 
                       "javascript", "ruby", "perl", 
                       "tex", "vcs", "fonts", "golang", "php", 
                       "editors", "java", "metapackages", "translations",
                       "shells", "debian-installer", "doc"]
PKG_FILTERS = ["glibc"]
SECURITY_EXTENDED_QLS = "/home/machiry/tools/codeqlrepo/codeql/cpp/ql/src/codeql-suites/cpp-security-extended.qls"
SETUP = True
CODEQL_ANALYSIS = False
# This needs to be modified.
LOCAL_SUDO_PASSWORD = "machiry_1337"

def setup_database() -> None:
    database.connect()
    # Create tables if they don't exist
    database.create_tables([DebianPackage, VCSInfo, PkgDevelopers, 
                            SourceLanguage, PkgCategory, DeveloperContact, 
                            ContactType, VCSType, CodeQLInfo], safe=True)
    setup_vcs_types()
    setup_contact_types()

def is_pkg_ignored(pkg: PkgEntry) -> None:
    if pkg.pkg_name in PKG_FILTERS:
        return True
    if pkg.category in FILTERED_CATEGORIES:
        return True
    return False

def extract_pkg(p: PackageManager, pkg_name: str) -> Any:
    print("[+] Extracting package: {}".format(pkg_name))
    pkg_folder = os.path.join(DOWNLOAD_PKG_DIR, pkg_name)
    create_folder(pkg_folder)
    p.download_package_source(pkg_name, pkg_folder)
    for cu_file in os.listdir(pkg_folder):
        if ".orig.tar" in cu_file and not cu_file.endswith(".asc"):
            #extract the archive
            print("[+] Extracting " + cu_file + "...")
            f = tarfile.open(os.path.join(pkg_folder, cu_file))
            f.extractall(pkg_folder)
            f.close()
            return path_to_folder(pkg_folder)
    return None


def add_pkg_to_database(p: PackageManager, pkg: PkgEntry) -> None:
    if not is_pkg_ignored(pkg):
        # Check if package exists in the database.
        res = DebianPackage.select().where(DebianPackage.name == pkg.pkg_name)
        if res.exists():
            print("[-] Package already exists: {}".format(pkg.pkg_name))
            return
        print("[+] Adding package: {}".format(pkg.pkg_name))
        src_url = None
        deb_url = None
        dsc_url = None
        for curr_src_url in pkg.source_urls:
            if ".orig.tar" in curr_src_url and not curr_src_url.endswith(".asc"):
                src_url = curr_src_url
            elif curr_src_url.endswith(".dsc"):
                dsc_url = curr_src_url
            elif curr_src_url.endswith(".debian.tar.xz"):
                deb_url = curr_src_url
        pkg_lang = "UNKNOWN"
        pkg_sloc = 0.0
        extracted_dir = None
        if src_url is not None:
            extracted_dir = extract_pkg(p, pkg.pkg_name)
            if extracted_dir is not None:
                tmp_pkg_lang = get_project_source_language(extracted_dir)
                if tmp_pkg_lang is not None:
                    pkg_lang = tmp_pkg_lang
                    pkg_sloc = get_project_sloc(pkg_lang, extracted_dir) * 1.0
        
        # Add language
        lang = SourceLanguage.get_or_create(language=pkg_lang)[0]
        # Add category
        cat = PkgCategory.get_or_create(category_name=pkg.category)[0]
        # Add package
        pkg_entry = DebianPackage.get_or_create(name=pkg.pkg_name, 
                                                language=lang, 
                                                category=cat)[0]
        pkg_entry.size_sloc = pkg_sloc
        pkg_entry.has_src = src_url is not None
        pkg_entry.src_download_url = src_url
        pkg_entry.deb_download_url = deb_url
        pkg_entry.dsc_download_url = dsc_url
        pkg_entry.src_extracted_dir = extracted_dir

        # Compute dependencies.
        dependency_list = p.dependency_map[pkg.pkg_name]
        all_dependencies = []
        for dependencies in dependency_list:
            all_dependencies.append(dependencies)
        
        pkg_entry.dependency_list = " ".join(all_dependencies)

        vcs_type = get_vcs_type(pkg.vcs_info)
        VCSInfo.get_or_create(pkg=pkg_entry, 
                              vcs_url=pkg.vcs_info, 
                              vcs_type=vcs_type)
        # Add developers
        for curr_dev in pkg.contacts:
            dev_contact = get_developer_contact(curr_dev)
            PkgDevelopers.get_or_create(pkg=pkg_entry, developer=dev_contact[0])
        
        pkg_entry.save()
        CodeQLInfo.get_or_create(pkg=pkg_entry)[0].save()

        database.commit()
    else:
        print("[-] Ignoring package: {}".format(pkg.pkg_name))

def perform_codeql_analysis(p: PackageManager) -> None:
    for curr_pkg in DebianPackage.select():
        if is_an_interesting_project(curr_pkg):
            codeql_result = curr_pkg.codeqlresult
            if len(codeql_result) > 0:
                codeql_result = codeql_result[0]
            if codeql_result is not None:
                if codeql_result.sarif_path is not None and os.path.exists(codeql_result.sarif_path):
                    print("[+] CodeQL analysis already done for package: {}".format(curr_pkg.pkg_name))
                    continue
                if codeql_result.failed_reason is not None:
                    print("[-] CodeQL analysis previously tried but failed for package: {}".format(curr_pkg.pkg_name))
                    continue
                if codeql_result.is_manually_analyzed is not None and codeql_result.is_manually_analyzed is True:
                    print("[-] CodeQL results have been already analyzed for the package: {}".format(curr_pkg.pkg_name))
                    continue
            print("[+] Analyzing package: {}".format(curr_pkg.name))
            if os.path.exists(curr_pkg.src_extracted_dir):
                print("[+] Pakage is already extracted at: {}".format(curr_pkg.src_extracted_dir))
            else:
                print("[+] Package is not extracted, Extracting.")
                extracted_dir = extract_pkg(p, curr_pkg.name)
                if extracted_dir is None:
                    print("[-] Failed to extract package: {}".format(curr_pkg.name))
                    continue
                else:
                    print("[+] Extracted package at: {}".format(extracted_dir))
                # update the extracted dir
                curr_pkg.src_extracted_dir = extracted_dir
                curr_pkg.save()
            # First install dependencies
            dependency_list = curr_pkg.dependency_list
            ret = subprocess.call(['echo ' + LOCAL_SUDO_PASSWORD + ' | sudo -S apt -yq install', dependency_list], shell=True)
            failed_reason = ""
            if ret != 0:
                failed_reason = "Dependency installation failed"

            # Now perform the analysis
            codeql_folder = os.path.join(os.path.dirname(extracted_dir), "codeqldb")
            create_folder(codeql_folder)
            cmd = "(" + "cd " + extracted_dir + " && codeql database create " + codeql_folder + " --overwrite --language=cpp)"
            ret = subprocess.call(cmd, shell=True)
            if ret != 0:
                codeql_result.failed_reason = failed_reason + "\n Failed to create codeql database"
                codeql_result.save()
                print("[-] Failed to create codeql database for package: {}".format(curr_pkg.name))
                continue
            codeql_result.codeql_db_path = codeql_folder
            codeql_result.save()
            cmd = "(" + "cd " + extracted_dir + " && codeql database analyze " + \
                   codeql_folder + " --format=sarif-latest --output=codeqlresults.sarif " + SECURITY_EXTENDED_QLS + ")"
            ret = subprocess.call(cmd, shell=True)
            if ret != 0:
                codeql_result.failed_reason = failed_reason + "\n Failed to analyze codeql database"
                codeql_result.save()
                print("[-] Failed to analyze codeql database for package: {}".format(curr_pkg.name))
                continue
            else:
                codeql_result.sarif_path = os.path.join(extracted_dir, "codeqlresults.sarif")
                codeql_result.save()
                print("[+] CodeQL analysis done for package: {}".format(curr_pkg.name))



def update_database_with_pkgs(src_url: str, sources_file: str) -> bool:
    print("[+] Updating database with packages")
    p = PackageManager(sources_file, src_url)
    p.build_pkg_entries()
    for curr_pkg in p.all_pkg_entries.values():
        add_pkg_to_database(p, curr_pkg)
    return True

def main():
    if SETUP:
        setup_database()
        update_database_with_pkgs(SRC_URL, SOURCES_FILE_PATH)
    if CODEQL_ANALYSIS:
        print("[+] Performing CodeQL analysis")
        p = PackageManager(SOURCES_FILE_PATH, SRC_URL)
        perform_codeql_analysis(p)

if __name__ == "__main__":
    main()

