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
from stats_helper import get_project_sloc, get_project_source_language

SOURCES_FILE_PATH = "/home/machiry/Downloads/debiancodeql/Sources"
DOWNLOAD_PKG_DIR = "/home/machiry/Downloads/debiancodeql/downloaded_pkgs"
SRC_URL = "http://mirror.math.ucdavis.edu/ubuntu/"
FILTERED_CATEGORIES = ["text", "python", "php", "kernel", 
                       "javascript", "ruby", "perl", 
                       "tex", "vcs", "fonts", "golang", "php", 
                       "editors", "java", "metapackages", "translations",
                       "shells", "debian-installer", "doc"]
PKG_FILTERS = ["glibc"]
SETUP = True

def path_to_folder(currd: str):
    # get path to only folder in this directory
    for cf in os.listdir(currd):
        if os.path.isdir(os.path.join(currd, cf)):
            return os.path.join(currd, cf)
    return None

def create_folder(dirn: str):
    # create folder if not exists
    if not os.path.isdir(dirn):
        os.makedirs(dirn)

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

def extract_pkg(p: PackageManager, pkg: PkgEntry) -> Any:
    print("[+] Extracting package: {}".format(pkg.pkg_name))
    pkg_folder = os.path.join(DOWNLOAD_PKG_DIR, pkg.pkg_name)
    create_folder(pkg_folder)
    p.download_package_source(pkg.pkg_name, pkg_folder)
    for cu_file in os.listdir(pkg_folder):
        if ".orig.tar" in cu_file:
            #extract the archive
            print("[+] Extracting " + cu_file + "...")
            cmd = "(" + "cd " + pkg_folder + " && " + "tar -xf " + str(cu_file) + ")"
            ret = subprocess.call(cmd, shell=True)
            if ret != 0:
                print("[-] Failed to extract: " + cu_file)
            else:
                return path_to_folder(pkg_folder)
    return None


def add_pkg_to_database(p: PackageManager, pkg: PkgEntry) -> None:
    if not is_pkg_ignored(pkg):
        print("[+] Adding package: {}".format(pkg.pkg_name))
        src_url = None
        deb_url = None
        dsc_url = None
        for curr_src_url in pkg.source_urls:
            if ".orig.tar" in curr_src_url:
                src_url = curr_src_url
            elif curr_src_url.endswith(".dsc"):
                dsc_url = curr_src_url
            elif curr_src_url.endswith(".debian.tar.xz"):
                deb_url = curr_src_url
        pkg_lang = "UNKNOWN"
        pkg_sloc = 0.0
        if src_url is not None:
            extracted_dir = extract_pkg(p, pkg)
            if extracted_dir is not None:
                pkg_lang = get_project_source_language(extracted_dir)
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
        vcs_type = get_vcs_type(pkg.vcs_info)
        VCSInfo.get_or_create(pkg=pkg_entry, 
                              vcs_url=pkg.vcs_info, 
                              vcs_type=vcs_type)
        # Add developers
        for curr_dev in pkg.contacts:
            dev_contact = get_developer_contact(curr_dev)
            PkgDevelopers.get_or_create(pkg=pkg_entry, developer=dev_contact[0])
        
        pkg_entry.save()

        database.commit()
    else:
        print("[-] Ignoring package: {}".format(pkg.pkg_name))

def update_database_with_pkgs(src_url: str, sources_file: str) -> bool:
    if DebianPackage.select().count() > 1:
        print("[+] Database already has packages, not updating")
        return False
    print("[+] Updating database with packages")
    p = PackageManager(sources_file, src_url)
    p.build_pkg_entries()
    i = 0
    for curr_pkg in p.all_pkg_entries.values():
        if i > 4:
            break
        add_pkg_to_database(p, curr_pkg)
        i += 1
    return True

def main():
    setup_database()
    update_database_with_pkgs(SRC_URL, SOURCES_FILE_PATH)

if __name__ == "__main__":
    main()
