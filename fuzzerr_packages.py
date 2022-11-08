#! /usr/bin/env python
from pkg_manager import PackageManager
import os
import sys
import IPython
import pprint

SOURCES_FILE = "/home/shank/code/research/apt-scraper-utils/Sources_Main"
MIRROR_URL = "http://mirror.math.ucdavis.edu/ubuntu/"


def build_pkg_entries() -> PackageManager:
    # build the package intries from the sources file
    p = PackageManager(SOURCES_FILE, MIRROR_URL)
    p.build_pkg_entries()
    return p


def get_libs_with_rdep_cnt(p: PackageManager) -> dict:
    # get the libraries with the number of reverse dependencies
    libs = {}
    for (pkg, rdeps) in p.reverse_dependency_map.items():
        if pkg.startswith("lib"):
            libs[pkg] = len(rdeps)
    return libs


def sort_libs_by_rdep_cnt(libs: dict) -> list:
    # sort the libraries by the number of reverse dependencies
    return sorted(libs.items(), key=lambda x: x[1], reverse=True)


def rdep_containing(pkg_mgr: PackageManager, s: str) -> None:
    # get the reverse dependencies that contain a string
    for (pkg, rdeps) in pkg_mgr.reverse_dependency_map.items():
        if s in pkg:
            print("=====================================")
            pprint.pprint(pkg)
            pprint.pprint(rdeps)
            print("=====================================")


if __name__ == "__main__":
    if len(sys.argv) != 2 or (len(sys.argv) == 2 and sys.argv[1] == "--help"):
        print("Usage: One of the following:")
        print("fuzzerr_packages.py <pkg_pickle_file>")
        print("fuzzerr_packages.py --build-pkg-entries")
        sys.exit(0)

    pkg_mgr = None
    if sys.argv[1] == "--build-pkg-entries":
        print("[+] Building package entries")
        pkg_mgr = build_pkg_entries()
        print("[+] Done building package entries")

        pickled_pkg_entries_fn = os.path.basename(
            SOURCES_FILE).lower() + ".pickled.json"
        print("[+] Saving package entries to {}".format(pickled_pkg_entries_fn))
        pkg_mgr.dump_to_pickled_json(pickled_pkg_entries_fn)
        print("[+] Done saving package entries")

    else:
        print("[+] Loading package entries from %s" % sys.argv[1])
        pkg_mgr = PackageManager.from_picked_json(sys.argv[1])
        print("[+] Done loading package entries")

    IPython.embed()
