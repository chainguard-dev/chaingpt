# Standard lib
from typing import List, Iterator
from dataclasses import dataclass

# 3rd party
import docker

# Local
from chaingpt.utils import config


IMAGE_NAME = config.config["docker_shell_environment"]["image"]


@dataclass
class RunResult():
    return_code: str
    stdout: str
    stderr: str


class SystemEnvironment():
    def run(self, script: str, deps: List[str]=None) -> Iterator[str]:
        """
        Runs `script` in an isolated shell. The `deps` `List` contains any
        Wolfi dependencies that should be installed before executing the script.

        Args:
            script (str): The shell script to run. (For now this should be written as a shell one-liner with `&&`).
            deps (List[str]): A list of Wolfi dependencies to install prior to script execution.

        
        Returns:
            An `Iterator` over stdout and stderr.
        
        Raises:
            TypeError: If argument types are invalid.
        """
        # TODO add better management of the underlying image. Does it exist?
        # TODO validate if the provided dependency is valid
        client = docker.from_env()
        
        install_deps = f"apk add {' '.join(deps)}"
        cmd = f"sh -c '{install_deps} && {script}'"
        container = client.containers.run(IMAGE_NAME, command=cmd,
                                          stdout=True, stderr=True, tty=True, detach=True)
        try:
            for line in container.logs(stream=True):
                yield line.decode('utf-8')
        finally:
            container.remove()
