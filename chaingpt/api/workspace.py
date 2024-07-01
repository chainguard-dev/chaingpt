# Standard lib
from typing import List, Tuple
import uuid
import os
import glob

# 3rd party
from sh import git, ErrorReturnCode_128

# Local
from chaingpt.api.llm import text_qa, text_qa_map_reduce, LLMResponse
from chaingpt.utils import config


MAX_FILE_SZ = config.config["llm"]["max_file_sz"]
MAP_REDUCE_CHUNK_SZ = config.config["llm"]["map_reduce"]["chunk_sz"]
MAP_REDUCE_CHUNK_OVERLAP = config.config["llm"]["map_reduce"]["chunk_overlap"]


def _random_parent_dir(prefix: str="/tmp") -> str:
    """
    Generate a random parent directory for a workspace.
    """
    dir = "chaingpt-" + str(uuid.uuid4())
    return os.path.join(prefix, dir)


def _validate_path_name(path: str):
    """
    Ensures `path` is properly formed and does
    not contain `..` or other attempts at directory
    traversal. 
    """
    # TODO
    

def _validate_git_url(url: str):
    """
    Ensures `url` is a properly formed GitHub repository URL.
    """
    # TODO
    pass


def _repo_name(url: str) -> str:
    """
    Returns the repo name.
    """
    repo = os.path.basename(url)
    if repo.endswith(".git"):
        repo = repo[:-4]
    return repo


class Workspace():
    def __init__(self, url: str):
        self.url = url
        self.parent_dir = _random_parent_dir()
        os.makedirs(self.parent_dir, exist_ok=False)
        self._clone(url)

    def _clone(self, url: str):
        """
        Clone the repository into the workspace parent directory.
        Sets `self.repo_dir`.
        """
        _validate_git_url(url)
        self.repo_dir = os.path.join(self.parent_dir, _repo_name(url))
        try:
            git.clone(url, self.repo_dir)
        except ErrorReturnCode_128:
            raise ValueError(f"Error cloning {url}. Is the URL valid?")

    def _read_n(self, n: int, file_path: str) -> str:
        """
        Reads `n` characters from `file_path`. The `file_path`
        is relative to the top-level directory of the repository.
        """
        full_path = os.path.join(self.repo_dir, file_path)
        with open(full_path, encoding="utf-8") as f:
            return f.read(n)

    def fileqa(self, question: str, file_path: str) -> LLMResponse:
        """
        Analyzes the contents of `file_path` to answer the `question` using an LLM.
        Files larger than `MAP_REDUCE_CHUNK_SIZE` characters are split into chunks and analyzed
        via a refine method. Files larger than `MAX_FILE_SZ` are truncated to only the
        first `MAX_FILE_SZ` characters.

        Args:
            question (str): The question to ask.
            file_path (str): The file to analyze. The path is relative to the
                             top-level directory of the repository.
        
        Returns:
            An `LLMResponse` containing the output from the LLM's analysis.
        
        Raises:
            TypeError: If `question` or `file_path` are not strings.
            FileNotFoundError: If the file does not exist.
        """
        # TODO: Add a feature that returns if the file was truncated.
        if not isinstance(question, str):
            raise TypeError("`question` must be a string")
        if not isinstance(file_path, str):
            raise TypeError("`file_path` must be a string")
        
        _validate_path_name(file_path)
        text = self._read_n(MAX_FILE_SZ, file_path)
        if len(text) > MAP_REDUCE_CHUNK_SZ:
            return text_qa_map_reduce(question, text, file_path=file_path,
                                      chunk_size=MAP_REDUCE_CHUNK_SZ,
                                      chunk_overlap=MAP_REDUCE_CHUNK_OVERLAP)
        return text_qa(question, text, file_path=file_path)


    def search(self, path: str) -> Tuple[List[str], List[str]]:
        """
        Searches the repository for files and directories matching `path`, which
        may include wildcard characters. All paths are interpreted as relative to
        the top-level directory of the repository.

        Args:
            path (str): The path to search.

        Returns:
            A Tuple of two `List` objects. The first `List` contains the directory names.
            The second `List` contains the file names.
        
        Raises:
            TypeError: If `path` is not a string.
        """
        if not isinstance(path, str):
            raise TypeError("`path` must be a string")
        _validate_path_name(path)
        abs_path = os.path.join(self.repo_dir, path)
        results = glob.glob(abs_path, recursive=True)
        files = []
        dirs = []
        for r in results:
            if os.path.isdir(r):
                dirs.append(os.path.relpath(r, self.repo_dir))
            else:
                files.append(os.path.relpath(r, self.repo_dir))
        return dirs, files
