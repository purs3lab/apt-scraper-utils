#!/usr/bin/env python3
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
import os
import subprocess
import magic

source_file_to_read_packages_from = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Sources")
mirror_url = "http://mirror.math.ucdavis.edu/ubuntu/"
local_download_folder_for_sources = os.path.join(os.path.dirname(os.path.realpath(__file__)), "downloaded_sources")
extracted_tar_sources = os.path.join(os.path.dirname(os.path.realpath(__file__)), "extracted_tar_sources")
bc_sources = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bc_sources")



def is_linux_64_executable(path):
    try:
        with open(path, 'rb') as f:
            file_type = magic.from_file(path)

        exec = '64-bit' in file_type and 'executable' in file_type
        return exec

    except Exception as e:
        #print(f"Error while checking if {path} is a linux 64 executable...")
        return False

def exists_with_prefix(prefix, directory='.'):
    for name in os.listdir(directory):
        if name.startswith(prefix):
            return True
    return False


def get_dir_with_prefix(prefix, directory='.'):
    for name in os.listdir(directory):
        if name.startswith(prefix):
            # Return name if it is a directory
            if(os.path.isdir(os.path.join(directory, name))):
                return name
    return None


def get_all_packages(packages_available):

    #for making package installation noninterative
    cmd = "(" + "export DEBIAN_FRONTEND=noninteractive" + ")"
    subprocess.run(cmd, shell=True)

    for i,pkgs in enumerate(packages_available):

        if(i == 2000):
            break
        
    
        if(exists_with_prefix(pkgs, local_download_folder_for_sources)):
            print(f"Skipping {pkgs} as it is already downloaded...")
            continue
        
        # Build all dependencies with apt build-dep <pkg_name>
        print(f"Bulding dependencies for {pkgs}...")
        cmd = "(" + "sudo apt build-dep " + pkgs + " -y" + ")"
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"DOWNLOADING and BUILDING {pkgs}...")
        # Download and build the pkg with apt source -b <pkg_name> in the local_download_folder_for_sources
        cmd = "(" + "cd " + local_download_folder_for_sources + " && " + "apt source -b " + pkgs + " -y" + ")"
        try:
            process = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,timeout=300)
            stdout, stderr = process.stdout, process.stderr
            if(stderr):
                print(f"Error while downloading {pkgs}...")
                print(stderr)
        # except the subprocess timeout
        except subprocess.TimeoutExpired:
            print(f"Timeout while downloading {pkgs}...")
            continue

        # Parse all files in the pkgs directory and extract-bc all the files which are executables
        # the pkg directory will have version number, so we need to os.walk into pkgs* directory
        dir_name = get_dir_with_prefix(pkgs, local_download_folder_for_sources)

        if(dir_name):
            for root, dirs, files in os.walk(os.path.join(local_download_folder_for_sources, dir_name)):
                for file in files:
                    if(is_linux_64_executable(os.path.join(root, file))):
                        # Check if the .bc file is already extracted
                        if(os.path.isfile(os.path.join(bc_sources, file + ".bc"))):
                            print(f"Skipping {os.path.join(root, file)} as it is already extracted...")
                            continue

                        # Extract the .bc files from the executables
                        print(f"Extracting .bc files from {os.path.join(root, file)}...")
                        cmd = "(" + "extract-bc " + os.path.join(root, file) + ")"
                        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        print(f"Moving {os.path.join(root, file)}.bc to {bc_sources}...")
                        # Move the .bc files to the bc_sources directory
                        cmd = "(" + "mv " + os.path.join(root, file) + ".bc " + bc_sources + ")"
                        #print(f"Executing {cmd}...")
                        try:
                            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        except Exception as e:
                            print(f"Error while moving {os.path.join(root, file)}.bc to {bc_sources}...")
                            print(e)
                            continue
        
        print("\n")


def main():

    if not os.path.isdir(local_download_folder_for_sources):
        cmd = "(" + "mkdir " + local_download_folder_for_sources + ")"
        subprocess.run(cmd, shell=True)

    if not os.path.isdir(bc_sources):
        cmd = "(" + "mkdir " + bc_sources + ")"
        subprocess.run(cmd, shell=True)

    if not os.path.isdir(extracted_tar_sources):
        cmd = "(" + "mkdir " + extracted_tar_sources + ")"
        subprocess.run(cmd, shell=True)

    p = PackageManager(source_file_to_read_packages_from, mirror_url)
    p.build_pkg_entries()

    p.dump_to_pickled_json("dummp.picked.json")
    packages_available = p.all_pkg_entries 

    get_all_packages(packages_available)


if __name__ == "__main__":
    # Set export LLVM_COMPILER=clang and CC=wllvm
    os.environ["LLVM_COMPILER"] = "clang"
    os.environ["CC"] = "wllvm"
    main()

