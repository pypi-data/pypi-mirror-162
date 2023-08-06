import os
import sys
from typing import Optional


def set_project_root_path(current_file_path: str, root_folder_name: str) -> Optional[str]:
    """
    Searching absolute path named `root_folder_name` at `current_file_path`'s super path,
    and add the result path to `sys.path` for further import.
    You can import local files after calling this.

    :param current_file_path pass __file__ at this var.

    :param root_folder_name Root project folder name, e.g. your_awesome_proj.
    
    :return Searched project root path.
    """
    SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(current_file_path))))
    PROJECT_DIR = SCRIPT_DIR
    while not PROJECT_DIR.endswith('/' + root_folder_name):
        if PROJECT_DIR == '/':
            PROJECT_DIR = None
            break
        PROJECT_DIR = os.path.normpath(os.path.join(PROJECT_DIR, '..'))
    if PROJECT_DIR is not None:
        sys.path.append(PROJECT_DIR)
    else:
        print('Project root path not found for name:', root_folder_name)
    return PROJECT_DIR
