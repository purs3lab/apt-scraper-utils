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
from typing import Any, List, Optional, Tuple
import statistics
from common_utils import path_to_folder, create_folder, is_an_interesting_project

def get_pkgs_of_category(category: PkgCategory) -> Optional[List[Any]]:
    """
    Returns a list of all packages of a given category.

    """
    to_ret = []
    qry = DebianPackage.select().where(DebianPackage.category == category)
    for curr_pkg in qry:
        to_ret.append(curr_pkg)
    return to_ret

def get_all_categories() -> List[PkgCategory]:
    """
    Returns a list of all categories.

    """
    to_ret = []
    qry = PkgCategory.select()
    for curr_category in qry:
        to_ret.append(curr_category)
    return to_ret
    

def main():
    all_cats = get_all_categories()
    print("[+] Got all categories: {}".format(str(len(all_cats))))
    print("[+] Debian Pkg Stats:")
    fp = open("class_pkgs.csv", "w")
    for curr_cat in all_cats:
        cat_name = curr_cat.category_name
        if cat_name == "libs":
            print("DSDSDS")
        all_pkgs = get_pkgs_of_category(curr_cat)
        src_pkgs = []
        # Get all interesting projects in this category.
        for p in all_pkgs:
            if is_an_interesting_project(p):
                src_pkgs.append(p)
        # Ignore empty categories
        if len(src_pkgs) < 5:
            continue
        for p in src_pkgs:
            fp.write("{}, {}, {}\n".format(p.name, p.category.category_name, p.src_download_url))
    fp.close()

if __name__ == "__main__":
    database.connect()
    main()