# Standard lib
import os
import shutil

# 3rd party
import pytest

# Local
from chaingpt.api import workspace


@pytest.fixture
def setup_grype_workspace(monkeypatch):
    """
    Fixture that sets up a workspace containing the grype
    repository. Copies a large and small test file into the
    top-level directory.
    """
    wk = workspace.Workspace("https://github.com/anchore/grype.git")
    
    big_path = os.path.join(wk.repo_dir, "big.txt")
    with open(big_path, "w") as f:
        f.write("A"*30000)
    
    small_path = os.path.join(wk.repo_dir, "small.txt")
    with open(small_path, "w") as f:
        f.write("B"*100)
    
    yield wk
    shutil.rmtree(wk.parent_dir)


@pytest.fixture
def cleanup_leftover_workspaces():
    """
    Used in test cases that should fail to create a workspace. Cleans up workspace
    """
    yield
    dirs = os.listdir("/tmp")
    for d in dirs:
        if d.startswith("chaingpt"):
            path = os.path.join("/tmp", d)
            shutil.rmtree(path)