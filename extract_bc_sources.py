##########################################################################
#
# This script will download all the C/C++ package tar sources to a local 
# folder -> extract, build and install the tar sources -> extract the .bc 
# files from the installed archives using wllvm
# 
# invoke this script with sudo, so that packages can be installed
#
##########################################################################
from pkg_manager import PackageManager
from ctypes.util import find_library
from debian_pkg_stats import DebianPkgStats
import os
import subprocess
import sys
import json
import re

source_file_to_read_packages_from = "/home/machiry/Downloads/debiancodeql/Sources"
mirror_url = "http://mirror.math.ucdavis.edu/ubuntu/"
local_download_folder_for_sources = "/home/machiry/Downloads/debiancodeql/downloadsources"
extracted_tar_sources = '/home/machiry/Downloads/debiancodeql/extracted_tar_sources'

def create_folder(dirn: str):
    # create folder if not exists
    if not os.path.isdir(dirn):
        os.makedirs(dirn)

def path_to_folder(currd: str):
    # get path to only folder in this directory
    for cf in os.listdir(currd):
        if os.path.isdir(os.path.join(currd, cf)):
            return os.path.join(currd, cf)
    return None

if not os.path.isdir(local_download_folder_for_sources):
    cmd = "(" + "mkdir " + local_download_folder_for_sources + ")"
    subprocess.call(cmd, shell=True)

#if not os.path.isdir(afl_fuzzing_sources):
#    cmd = "(" + "mkdir " + afl_fuzzing_sources + ")"
#    subprocess.call(cmd, shell=True)

if not os.path.isdir(extracted_tar_sources):
    cmd = "(" + "mkdir " + extracted_tar_sources + ")"
    subprocess.call(cmd, shell=True)


p = PackageManager(source_file_to_read_packages_from, mirror_url)
p.build_pkg_entries()

p.dump_to_pickled_json("dummp.picked.json")
p2 = PackageManager.from_picked_json("dummp.picked.json")


packages_available = p.all_pkg_entries

#for making package installation noninterative
cmd = "(" + "export DEBIAN_FRONTEND=noninteractive" + ")"
subprocess.call(cmd, shell=True)

all_pkg_status = {}

num = 0
max_num_pkgs = 1
for pkgs in packages_available:
    if num >= max_num_pkgs:
        break
    num = num + 1
    all_pkg_status[pkgs] = DebianPkgStats(pkgs)
    cstatus = all_pkg_status[pkgs]
    reverse_dependencies = []
    dependency_list = p.dependency_map[pkgs]
    all_dependencies = []
    for dependencies in dependency_list:
        all_dependencies.append(dependencies)
        # install all reverse dependencies might be too slow (not necessary), uncomment if needed
        #for reverse_deps in p.reverse_dependency_map[dependencies]:
        #    subprocess.call(['sudo apt -yq install', str(reverse_deps)], shell=True)        
        #subprocess.call(['echo machiry_1337 | sudo -S apt -yq install', str(dependencies)], shell=True)
        reverse_dependencies.extend(p.reverse_dependency_map[dependencies])
    ret = subprocess.call(['echo machiry_1337 | sudo -S apt -yq install', " ".join(all_dependencies)], shell=True)
    if ret != 0:
        cstatus.add_dependency_status("FAILED")
    else:
        cstatus.add_dependency_status("SUCCESS")
    print()
    print("...")
    print("DOWNLOADING "+ str(pkgs) + "from the mirror...")
    print("...")
    pkg_folder = os.path.join(local_download_folder_for_sources, pkgs)
    p.download_package_source(pkgs, pkg_folder)
    cstatus.add_download_status("SUCCESS")


for curr_dir in os.listdir(local_download_folder_for_sources):
    cdir_fullpath = os.path.join(local_download_folder_for_sources, curr_dir)
    cstatus = all_pkg_status[curr_dir]
    if os.path.isdir(cdir_fullpath):
        for tfi in os.listdir(cdir_fullpath):
            if tfi.endswith(".orig.tar.gz"):
                #extract the archive
                print("Extracting " + tfi + "...")
                cmd = "(" + "cd " + cdir_fullpath + " && " + "tar -xf " + str(tfi) + ")"
                ret = subprocess.call(cmd, shell=True)
                if ret != 0:
                    cstatus.add_extract_status("FAILED")
                else:
                    cstatus.add_extract_status("SUCCESS")
                extract_dir_name = path_to_folder(cdir_fullpath)
                if extract_dir_name is not None:
                    configure_path = extract_dir_name + "/" + "configure"
            
                    #check if a configure script exists in the directory
                    if( os.path.exists(configure_path) == True ):
                        #now cd into the archive
                        cmd = "(" + "cd " + extract_dir_name + " && ./configure" +  " && " + "make" + ")"
                        ret = subprocess.call(cmd, shell=True)
                        if ret != 0:
                            cstatus.add_build_status("FAILED")
                        else:
                            cstatus.add_build_status("SUCCESS")
                    else:
                        cstatus.add_build_status("FAILED")

fp = open("all_pkg_status.json", "w")
json_strs = {}
for p in all_pkg_status:
    json_strs[p] = all_pkg_status[p].toJson()
fp.write(json.dumps(json_strs))
fp.close()