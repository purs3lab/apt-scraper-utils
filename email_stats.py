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
from common_utils import path_to_folder, create_folder, is_an_interesting_project

SOURCES_FILE_PATH = "/home/machiry/projects/apt-scraper-utils/data_files/jammydebsource"
SRC_URL = "http://mirror.math.ucdavis.edu/ubuntu/"
DEV_EMAIL_FILE = "debian_emails.csv"

def main():
    all_interesting_pkgs = []
    for curr_pkg in DebianPackage.select():
        if is_an_interesting_project(curr_pkg):
            all_interesting_pkgs.append(curr_pkg)
    
    deb_type = ContactType.get_or_create(typename='debian')[0]
    custom_type = ContactType.get_or_create(typename='custom')[0]

    p = PackageManager(SOURCES_FILE_PATH, SRC_URL)
    p.build_pkg_entries()
    print("[+] Writing to file: {}".format(DEV_EMAIL_FILE))
    fp = open(DEV_EMAIL_FILE, "w")
    fp.write("Package, Developer Name, Developer Email\n")
    # print("Package, Developer Name, Developer Email")
    for curr_pkg in all_interesting_pkgs:
        all_devs = curr_pkg.developers
        pkg_entry = p.all_pkg_entries[curr_pkg.name]
        if len(all_devs) > 0:
            for curr_dev in all_devs:
                curr_type = curr_dev.developer.type
                dev_name = None
                if curr_dev.developer.email in pkg_entry.contact_email_map:
                    dev_name = pkg_entry.contact_email_map[curr_dev.developer.email]
                if dev_name is not None:
                    if curr_type == deb_type or curr_type == custom_type:
                        # print("{}, {}, {}".format(curr_pkg.name, dev_name, curr_dev.developer.email))
                        fp.write("{}, {}, {}\n".format(curr_pkg.name, dev_name, curr_dev.developer.email))

    fp.close()
    print("[+] Finished writing to file {}.".format(DEV_EMAIL_FILE))

if __name__ == "__main__":
    database.connect()
    main()