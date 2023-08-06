import os

from git import Repo, exc


class GitUtils:
    """
    A thin wrapper around GitPython methods
    """

    def init_repository(self):
        """
        Get current version from setup.py

        Returns:
            new_version: The bumped version

        """
        repo = Repo.init(os.getcwd())
        return repo

    def on_master_branch(self, repository):
        """
        Check the current branch

        Returns:
            True if branch is master or main, False otherwise

        """
        branch = repository.active_branch.name
        return bool(branch == "master" or branch == "main")

    def update_tags(
        self, repo: Repo, current_version: str, new_version: str, tag_message: str
    ):
        """
        Tags and commits changes
        """
        try:
            repo.create_tag(new_version, repo.active_branch.name, message=tag_message)
            repo.remotes.origin.push(new_version)
        except exc.GitCommandError as excpt:
            print("Ooops.. An error occured creating the tag")
            raise ValueError("Ooops.. An error occured creating the tag") from excpt

        repo.git.add("History.md")
        repo.index.commit(
            "Version successfully bumped from %s to %s" % (current_version, new_version)
        )
