"""
TODO: This file was used to mange sessions back when we thought we
were going to host ChainGPT on Chainguard servers. This is no longer
the plan and we should remove this file.
"""


# Standard lib
import uuid

# 3rd party

# Local
from chaingpt.api.workspace import Workspace


# TODO: Temp implementation of workspace management.
workspace_cache = {}


def new_session(url: str) -> str:
    """
    Creates a new workspace with `url` and returns
    and session id that is used to look it up in future
    requests.

    Args:
        url (string): The GitHub URL.
    
    Returns:
        The session id used to reference the workspace in later requests.
    
    Raises:
        ValueError: If the URL is not valid.
    """
    workspace = Workspace(url)
    id = str(uuid.uuid4())
    workspace_cache[id] = workspace
    return id


def get_workspace(session_id: str) -> Workspace:
    """
    Returns the workspace associated with `session_id`.

    Args:
        session_id (str): The session id to lookup.
    
    Returns:
        The `Workspace` object associated with `session_id`.
    
    Raises:
        ValueError: If no workspace is found for `session_id`.
    """
    if session_id not in workspace_cache.keys():
        raise ValueError(f"{session_id} is not a valid session id")
    return workspace_cache[session_id]
