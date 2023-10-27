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
SRC_URL = "http://mirror.math.ucdavis.edu/ubuntu/"

def main():
    all_interesting_pkgs = []
    for curr_pkg in DebianPackage.select():
        if is_an_interesting_project(curr_pkg):
            all_interesting_pkgs.append(curr_pkg)
    
    deb_type = ContactType.get_or_create(typename='debian')[0]
    custom_type = ContactType.get_or_create(typename='custom')[0]

    p = PackageManager(SOURCES_FILE_PATH, SRC_URL)
    p.build_pkg_entries()

    for curr_pkg in all_interesting_pkgs:
        all_devs = curr_pkg.developers
        if len(all_devs) > 0:
            codeql_result = codeql_result[0]


if __name__ == "__main__":
    main()