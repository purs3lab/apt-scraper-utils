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
import json
from stats_helper import get_project_sloc, get_project_source_language
from common_utils import path_to_folder, create_folder, is_an_interesting_project

SOURCES_FILE_PATH = "/home/machiry/projects/apt-scraper-utils/data_files/jammydebsource"
SRC_URL = "http://mirror.math.ucdavis.edu/ubuntu/"
DEBAIN_PKG_SARIF_FILE = "debian_sarif_files.csv"

def is_sarif_empty(sarif_path: str) -> bool:
    sarif_data = None
    sarif_path = sarif_path.replace("/home/machiry/Downloads/debianpkgs", "/media/machiry/PurS3Disk/debianresults/debianpkgs/")
    with open(sarif_path, "r") as fp:
        sarif_data = json.load(fp)
    if sarif_data is None:
        return True
    if "runs" not in sarif_data:
        return True
    if len(sarif_data["runs"]) == 0:
        return True
    if "results" not in sarif_data["runs"][0]:
        return True
    if len(sarif_data["runs"][0]["results"]) == 0:
        return True
    return False

def main():
    fp = open(DEBAIN_PKG_SARIF_FILE, "w")
    for curr_pkg in DebianPackage.select():
        codeql_result = curr_pkg.codeqlresult
        if len(codeql_result) > 0:
            codeql_result = codeql_result[0]
            if codeql_result is not None and codeql_result.sarif_path is not None:
                if not is_sarif_empty(codeql_result.sarif_path):
                    fp.write("{}, {}, {}\n".format(curr_pkg.name, curr_pkg.src_download_url, codeql_result.sarif_path))
                else:
                    print("[-] Empty sarif file: {}".format(codeql_result.sarif_path))
    fp.close()
    print("[+] Finished writing to file {}.".format(DEBAIN_PKG_SARIF_FILE))

if __name__ == "__main__":
    database.connect()
    main()