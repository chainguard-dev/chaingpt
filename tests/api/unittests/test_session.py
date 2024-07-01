# Standard lib

# 3rd party
import pytest

# Local
from chaingpt.api import session, workspace
from tests.api.unittests.utils import cleanup_leftover_workspaces


def test__new_session__valid_url():
    """
    Checks that a session id is returned when a valid
    GitHub URL is provided.
    """
    id = session.new_session("https://github.com/anchore/grype.git")
    assert isinstance(id, str)


def test__new_session__invalid_url():
    """
    Checks that a `ValueError` is thrown when an invalid
    GitHub URL is provided.
    """
    with pytest.raises(ValueError):
        session.new_session("invalid.url/dne")


def test__get_workspace__valid_id(cleanup_leftover_workspaces):
    """
    Checks that a `Workspace` is returned when a valid
    `session_id` is provided.
    """
    id = session.new_session("https://github.com/anchore/grype.git")
    wk = session.get_workspace(id)
    assert wk.url == "https://github.com/anchore/grype.git"


def test__get_workspace__invalid_id():
    """
    Checks that a `ValueError` is raised when an invalid
    `session_id` is provided.
    """
    with pytest.raises(ValueError):
        wk = session.get_workspace("id-1234")
