"""
Module to manage user interactions on terminal
"""
release_types = {
    "patch": "Patch: Bug fixes, recommended for all (default)",
    "minor": "Minor: New features, but backwards compatible",
    "major": "Major: Breaking changes",
}


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class UserInteractions:
    def show_initial_menu(self):
        """
        Display release options to the user

        Returns:
            release_type: The type of release
        """
        prompt = "> "
        print(bcolors.OKBLUE + "Enter the type of change" + bcolors.ENDC)
        print(bcolors.OKGREEN + "1. %s" % release_types["patch"] + bcolors.ENDC)
        print(bcolors.OKGREEN + "2. %s" % release_types["minor"] + bcolors.ENDC)
        print(bcolors.OKGREEN + "3. %s" % release_types["major"] + bcolors.ENDC)

        release_type = input(prompt)
        return release_type

    def get_change_details(self):
        """
        Display prompt for summary of changes

        Returns:
            change_summary: A summary of the change
        """
        print("Enter the changes")
        changes = ""
        user_input = " *"
        while user_input:
            user_input = input(" * ")
            changes += "\n" + "* " + user_input
        return changes[: changes.rfind("\n")]

    def get_change_summary(self):
        """
        Allow user to enter the tag message

        Returns:
            tag_message: A summary of the change
        """
        tag_message = input(" Enter tag message heading : ")
        return tag_message
