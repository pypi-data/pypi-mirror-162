#!/usr/bin/python
"""
Pythemantic Module
"""
import sys

from pythemantic import bcolors, bump, interactions
from pythemantic.git_utils import GitUtils


class Pythemantic:
    def __init__(self):
        self.user_interactions = interactions.UserInteractions()
        self.git_utils = GitUtils()

    def bump_version(self):
        """
        Bump the version of current repository
        """
        repo = self.git_utils.init_repository()

        while True:
            if not self.git_utils.on_master_branch(repo):
                try:
                    release_type = self.user_interactions.show_initial_menu()
                    break
                except ValueError:
                    print("Sorry, I didn't understand that.")
                    continue
            else:
                print(
                    f"{bcolors.FAIL}***** You are not on master ***** \nIt is not recommended to create releases from a branch unless they're maintenance releases\nExiting ...{bcolors.ENDC}"
                )
                sys.exit()

        current_version = bump.get_current_version()
        new_version = bump.bump_version(release_type, current_version)

        # add new version details
        change_summary = self.user_interactions.get_change_summary()
        change_details = self.user_interactions.get_change_details()

        # update history file
        bump.update_history(
            new_version=new_version,
            change_details=change_details,
            change_summary=change_summary,
        )

        # update version file
        bump.update_version_file(new_version=new_version)

        # push the tags to remote repository
        self.git_utils.update_tags(repo, current_version, new_version, change_summary)
        print(
            "Repo successfully bumped from %s to %s " % (current_version, new_version)
        )


if __name__ == "__main__":
    sys.exit((Pythemantic().bump_version()))
