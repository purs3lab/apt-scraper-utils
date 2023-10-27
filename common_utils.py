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

FILTERED_CATEGORIES = ["text", "python", "php", "kernel", 
                       "javascript", "ruby", "perl", 
                       "tex", "vcs", "fonts", "golang", "php", 
                       "editors", "java", "metapackages", "translations",
                       "shells", "debian-installer", "doc"]
PKG_FILTERS = ["glibc"]
IGNORE_PKG_PREFIXES = ["llvm", "linux-", "live"]

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

def is_pkg_name_ignored(pkg_name: str) -> bool:
    if pkg_name in PKG_FILTERS:
        return True
    for curr_prefix in IGNORE_PKG_PREFIXES:
        if pkg_name.startswith(curr_prefix):
            return True
    return False

def is_pkg_ignored(pkg: PkgEntry) -> None:
    if pkg.category in FILTERED_CATEGORIES:
        return True
    return is_pkg_name_ignored(pkg.pkg_name)

def is_an_interesting_project(curr_pkg: DebianPackage) -> bool:
    """
    Check if the current package is interesting.
    """
    if is_pkg_name_ignored(curr_pkg.name):
        return False
    return curr_pkg.has_src and is_c_or_cpp(curr_pkg.language.language)
