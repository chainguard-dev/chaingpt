# Standard lib
from typing import List

# 3rd Party
from langchain.tools import StructuredTool

# Local
from chaingpt.api.workspace import Workspace
from chaingpt.api.wolfi import WolfiClient
from chaingpt.api.system import SystemEnvironment


def _error(msg: str) -> str:
    return f"Error: {msg}"


def get_tool_file_qa(workspace: Workspace) -> StructuredTool:
    def file_qa(question: str, file_path: str) -> str:
        """
        Input a question and a filename. File paths are relative to the top-level
        of the GitHub repository. The function scans the file with an LLM and
        provides the answer.
        """
        try:
            return workspace.fileqa(question, file_path)
        except FileNotFoundError as e:
            return _error(str(e))
    
    return StructuredTool.from_function(file_qa)


def get_tool_search_path(workspace: Workspace) -> StructuredTool:
    def search_path(path: str) -> str:
        """
        Efficiently search for files and directories using this tool,
        which allows you to specify a path and employ glob patterns
        for advanced queries. Searches begin at the top-level of the
        cloned repository. For example, to get all of the files in the top-level
        directory, pass * to path.
        """
        dirs, files = workspace.search(path)
        return "Directories: [" + ", ".join(dirs) + "]\nFiles: [" + ", ".join(files) + "]"

    return StructuredTool.from_function(search_path)


def get_tool_run_script(callback: any) -> StructuredTool:
    def run_script(script: str, deps: str) -> str:
        """
        Executes the provided script in an isolated Wolfi environment.

        Scripts should take the form of one-liner shell scripts. Use && to chain
        together multiple commands.

        The results of stdout and stdin are returned. Any changes the script makes
        to the environment are not persisted. You will have to specify dependencies via the 
        deps argument, a comma separated list of Wolfi packages the script depends on.
        For example, a script requiring git and python 3.10 would pass "python-3.10, git" for deps. All deps
        are specific to Wolfi. Use the search_wolfi tool to lookup the names of these dependencies.

        The environment does not have the repository preinstalled. If you wish to use the environment to test
        interactions with the repository, be sure to clone the repo first in the commands passed to this tool.

        Do not use docker within the environment.
        """
        deps_list = deps.split(",")
        deps_list = [d.strip(" \n") for d in deps_list]

        env = SystemEnvironment()

        response = ""
        for output in env.run(script, deps=deps_list):
            callback(output)
            response += output
        
        return response[-1000:]

    return StructuredTool.from_function(run_script)


def get_tool_wolfi_search(client: WolfiClient) -> StructuredTool:
    def search_wolfi(keyword: str) -> str:
        """
        Searches Wolfi for packages that match the provided keyword.
        Useful for determining which package names to pass to the deps argument
        of the run_script tool. Search results are returned in [name]: [description] format.
        For example, the results of searching for python might return:

        python-3.10: The Python 3.10 software library
        python-3.11: The Python 3.11 software library
        python-3.12: The Python 3.12 software library

        If the script depends on Python 3.10, you would pass "python-3.10" to deps, along with
        any other packages you wish to include.
        """
        results = client.search(keyword)
        results_str = ""
        for r in results:
            results_str += f"{r.name}: {r.description}\n"
        return results_str

    return StructuredTool.from_function(search_wolfi)


def get_tools(url: str, callback: any) -> List[StructuredTool]:
    wk = Workspace(url)
    return [
        get_tool_file_qa(wk),
        get_tool_search_path(wk),
        get_tool_run_script(callback),
        get_tool_wolfi_search(WolfiClient())
    ]
