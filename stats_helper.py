import ghlinguist as ghl
from sh import git
import os
from glob import glob
from pygount import ProjectSummary, SourceAnalysis
from typing import Any

def get_project_source_language(source_dir: str) -> Any:
    """
    Get the source language for the given project.
    :param source_dir: Local file path to the project.
    :return: Language of the project.
    """
    try:
        if os.path.isdir(source_dir):
            # Initialze a git repo in source_dir
            curr_dur = os.getcwd()
            os.chdir(source_dir)
            git.init(".")
            # Add all files in source_dir
            git.add("--all")
            # Commit all files in source_dir
            git.commit("-m Adding")
            # Go back to the current directory
            os.chdir(curr_dur)
            
            # Now, we can run ghlinguist on the source_dir
            langs = ghl.linguist(source_dir)
            if len(langs) > 0:
                return langs[0][0]
            else:
                print("[-] Unable to find language for project: " + source_dir)
    except Exception as e:
        print("[-] Unable to find language for project: " + source_dir)
        print("[-] Exception: " + str(e))
    return None

def get_project_sloc(language: str, source_dir: str) -> int:
    """
    Get the number of lines of code for the given project.
    :param language: Language of the project.source_paths = glob(source_dir + "/**/*.*")
    ps = ProjectSummary()
    :param source_dir: Local file path to the project.
    :return: Number of lines of code for the given project.
    """
    # Add all files in source_dir
    source_paths = glob(source_dir + "/**/*.*", recursive=True)
    ps = ProjectSummary()
    for sp in source_paths:
        sa = SourceAnalysis.from_file(sp, os.path.basename(source_dir))
        ps.add(sa)
    # Count the number of lines of code for the given language
    total_count = 0
    for ls in ps.language_to_language_summary_map:
        if str(ls).lower() == language.lower():
            total_count += ps.language_to_language_summary_map[ls].code_count
    
    return total_count
    