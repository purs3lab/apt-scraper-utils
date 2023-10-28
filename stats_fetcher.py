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

def get_min_mean_median_max(all_nums: List[float]) -> Tuple[float, float, float, float]:
    min_num = min(all_nums)
    max_num = max(all_nums)
    median_num = statistics.median(all_nums)
    mean_num = statistics.mean(all_nums)

    return (min_num, mean_num, median_num, max_num)
    

def main():
    all_cats = get_all_categories()
    print("[+] Got all categories: {}".format(str(len(all_cats))))
    print("[+] Debian Pkg Stats:")
    all_src_pkgs = []
    for curr_cat in all_cats:
        cat_name = curr_cat.category_name
        all_pkgs = get_pkgs_of_category(curr_cat)
        src_pkgs = []
        # Get all interesting projects in this category.
        for p in all_pkgs:
            if is_an_interesting_project(p):
                src_pkgs.append(p)
        # Ignore empty categories
        if len(src_pkgs) == 0:
            continue
        all_sizes = []
        all_src_pkgs.extend(src_pkgs)
        for p in src_pkgs:
            all_sizes.append(p.size_sloc)
        min_num, mean_num, median_num, max_num = get_min_mean_median_max(all_sizes)
        print("{}, {} ({}\\%)/{}, {}, {}, {}, {}".format(cat_name, len(src_pkgs), (len(src_pkgs) * 100.0) / len(all_pkgs), 
              len(all_pkgs), min_num, mean_num, median_num, max_num))
    
    print()
    print("[+] VCS Stats:")
    vcs_map = {}
    for curr_pkg in all_src_pkgs:
        all_vcs = curr_pkg.vcs
        curr_vcs = None
        if len(all_vcs) > 0:
            curr_vcs = all_vcs[0]
        else:
            continue
        type_name = curr_vcs.vcs_type.type_name
        if type_name not in vcs_map:
            vcs_map[type_name] = 0
        vcs_map[type_name] += 1
    for tn in vcs_map:
        print("{}, {} ({}\\%)".format(tn, vcs_map[tn], (vcs_map[tn]*100.0)/len(all_src_pkgs)))

if __name__ == "__main__":
    database.connect()
    main()