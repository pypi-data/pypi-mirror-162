"""
Bump Module
"""
import os

import semantic_version
from semantic_version import Version

from pythemantic import bcolors


def get_current_version():
    """
    Get current version from setup.py

    Returns:
        current_version: The current version of the repo
    """
    with open("version", encoding="utf-8") as f:
        version = f.read().strip()
        current_version = semantic_version.Version(version)
        return current_version


def bump_version(release_type: str, current_version: Version):
    """
    Get current version from setup.py

    Returns:
        new_version: The bumped version

    """
    if release_type == "1":
        new_version = current_version.next_patch()
        # print( new_version.major)
        # print( new_version.minor)
        # print( new_version.patch)
    elif release_type == "2":
        new_version = current_version.next_minor()
    elif release_type == "3":
        new_version = current_version.next_major()
    else:
        print(bcolors.FAIL + "** Invalid selection **" + bcolors.ENDC)
        return None

    return new_version


def update_history(new_version: str, change_summary: str, change_details: str):
    """
    Update change_log.md or history.md file contents

    Args:
        new_version: The new version
        change_summary: A summary of all the changes in the new version

    """
    history_file_path = os.path.join(os.getcwd(), "History.md")

    with open(history_file_path, encoding="utf-8", mode="r+") as history_file:
        current_content = history_file.read()

        change_message = (
            "## %s" % new_version + " - " + change_summary + "\n" + change_details
        )
        history_file.write(f"{change_message}\n{current_content}")


def update_version_file(new_version: Version):
    # update version file
    version_file_path = os.path.join(os.getcwd(), "version")
    with open(version_file_path, encoding="utf-8", mode="r+") as version_file:
        # print("****")
        # print(str(new_version.major) + '.' + str(new_version.minor) + '.' + str(new_version.patch))
        version_file.write(
            f"{str(new_version.major)}.{str(new_version.minor)}.{str(new_version.patch)}"
        )
