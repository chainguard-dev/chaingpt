# Standard lib
import os
import shutil

# 3rd party
import pytest

# Local
from chaingpt.api import workspace
from tests.api.unittests.utils import setup_grype_workspace, cleanup_leftover_workspaces


def test___random_parent_dir__prefix_provided():
    """
    Checks that the provided `prefix` is prepended to the result.
    """
    dir = workspace._random_parent_dir(prefix="/prefix")
    assert dir.split("/")[1] == "prefix"


def test___random_parent_dir__prefix_is_none():
    """
    Checks that the default `prefix` is prepended to the result.
    """
    dir = workspace._random_parent_dir()
    assert dir.split("/")[1] == "tmp"


def test___validate_path_name__is_proper():
    """
    Checks that a properly formed path name does not raise an exception.
    """
    # TODO
    pass


def test___validate_path_name__is_improper():
    """
    Checks that improperly formatted or malicious path names raise an exception.
    """
    # TODO
    pass


def test___validate_git_url__is_proper():
    """
    Checks that a properly formed GitHub URL does not raise an exception.
    """
    # TODO
    pass


def test___validate_git_url__is_improper():
    """
    Checks that improperly formatted GitHub URLs raise an exception.
    """
    # TODO
    pass


def test___repo_name__no_suffix():
    """
    Checks that the correct name is extracted without the .git
    suffix in the URL.
    """
    repo = workspace._repo_name("https://github.com/user/project")
    assert repo == "project"


def test___repo_name__with_suffix():
    """
    Checks that the correct name is extracted with the .git
    suffix in the URL.
    """
    repo = workspace._repo_name("https://github.com/user/project.git")
    assert repo == "project"


class TestWorkspace:
    def test__clone__grype(self, setup_grype_workspace):
        """
        Checks that grype is successfully cloned by checking
        if the README exists.
        """
        wk = setup_grype_workspace
        readme_path = os.path.join(wk.repo_dir, "README.md")
        assert os.path.exists(readme_path)


    def test___clone__invalid_url(self, cleanup_leftover_workspaces):
        """
        Checks that a URL that does not lead to a GitHub
        repository raises a `ValueError`.
        """
        with pytest.raises(ValueError):
            workspace.Workspace("invalid.url/dne")


    def test___read_n__file_size_gt_n(self, setup_grype_workspace):
        """
        Checks that the correct number of characters
        is read when the file size is larger than `n`.
        """
        wk = setup_grype_workspace
        chars = wk._read_n(10, "small.txt")
        assert chars == "B" * 10


    def test___read_n__file_size_lt_n(self, setup_grype_workspace):
        """
        Checks that the correct number of characters
        is read when the file size is less than `n`.
        """
        wk = setup_grype_workspace
        chars = wk._read_n(200, "small.txt")
        assert chars == "B" * 100


    def test___read_n__file_size_eq_n(self, setup_grype_workspace):
        """
        Checks that the correct number of characters
        is read when the file size is equal to `n`.
        """
        wk = setup_grype_workspace
        chars = wk._read_n(100, "small.txt")
        assert chars == "B" * 100


    def test___fileqa__question_is_not_str(self, setup_grype_workspace):
        """
        Checks that a `TypeError` is raised if `question` is not
        a string.
        """
        wk = setup_grype_workspace
        with pytest.raises(TypeError):
            wk.fileqa(999, "README.md")


    def test__fileqa__file_path_is_not_str(self, setup_grype_workspace):
        """
        Checks that a `TypeError` is raised if `file_path` is not
        a string.
        """
        wk = setup_grype_workspace
        with pytest.raises(TypeError):
            wk.fileqa("What is the name of the project?", 999)


    def test__fileqa__file_path_dne(self, setup_grype_workspace):
        """
        Checks that a `FileNotFoundError` is raised if
        `file_path` does not exist in the repository.
        """
        wk = setup_grype_workspace
        with pytest.raises(FileNotFoundError):
            wk.fileqa("What is the name of the project?", "dne.txt")
    

    def test__search__no_wildcards_dir(self, setup_grype_workspace):
        """
        Checks retrieval of a directory with no wildcards.
        """
        wk = setup_grype_workspace
        dirs, files = wk.search("grype")
        assert "grype" in dirs
        assert files == []


    def test__search__no_wildcards_file(self, setup_grype_workspace):
        """
        Checks retrieval of a file with no wildcards.
        """
        wk = setup_grype_workspace
        dirs, files = wk.search("grype/lib.go")
        assert dirs == []
        assert "grype/lib.go" in files
        

    def test__seach__wildcards(self, setup_grype_workspace):
        """
        Checks retrieval of files and directories using wildcards.
        """
        wk = setup_grype_workspace
        dirs, files = wk.search("grype/*")
        assert "grype/db" in dirs
        assert "grype/lib.go" in files
        

    def test__search__no_results(self, setup_grype_workspace):
        """
        Checks that empty list are returned for searches
        with no results.
        """
        wk = setup_grype_workspace
        dirs, files = wk.search("internal/non_existent")
        assert dirs == []
        assert files == []


    def test__search__path_is_not_str(self, setup_grype_workspace):
        """
        Checks that a `TypeError` is raised if `path`
        is not a `str`.
        """
        wk = setup_grype_workspace
        with pytest.raises(TypeError):
            wk.search(123)


    def test__search__traversal_attack(self):
        """
        Checks that attempts to navigate outside of the
        repository fail.
        """
        # TODO
        pass