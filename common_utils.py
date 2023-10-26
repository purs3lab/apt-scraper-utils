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

# Is the language C or C++?
def is_c_or_cpp(lang: str) -> bool:
    if lang is not None and \
    (lang.lower() == "c" or lang.lower() == "c++"):
        return True
    return False

def is_an_interesting_project(curr_pkg: DebianPackage) -> bool:
    """
    Check if the current package is interesting.
    """
    return curr_pkg.has_src and is_c_or_cpp(curr_pkg.language.language)
