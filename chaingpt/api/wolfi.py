# Standard lib
from typing import List
import os
import shutil
from dataclasses import dataclass

# 3rd party
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
from whoosh.query import Or
from sh import git
import yaml
import tqdm

# Local
from chaingpt.utils import config


GIT_TOKEN = config.config["secrets"]["github_personal_access_token"]
OS_DIR = config.config["wolfi_database"]["os_dir"]
OS_NAME = "wolfi-os"

INDEX_DIR = config.config["wolfi_database"]["index_dir"]
INDEX_NAME = "wolfi-index"

REBUILD_AT_START = config.config["wolfi_database"]["rebuild_at_start"]


@dataclass
class WolfiPackageResult:
    name: str
    description: str


class WolfiClient:
    def __init__(self):
        self.os_path = os.path.join(OS_DIR, OS_NAME)
        self.index_path = os.path.join(INDEX_DIR, INDEX_NAME)
        
        if REBUILD_AT_START \
                or (not os.path.exists(self.os_path)) \
                or (not os.path.exists(self.index_path)):
            self._init_index()
        else:
            self.index = open_dir(self.index_path)
    
    def _init_index(self):
        """
        Initialize the whoosh index with all of Wolfi.
        """
        # TODO: Extract clone and index functionality and write tests

        # Clone Wolfi
        if os.path.exists(self.os_path):
            shutil.rmtree(self.os_path)
        git.clone("https://github.com/wolfi-dev/os.git", self.os_path)
        
        # Build index
        if os.path.exists(self.index_path):
            shutil.rmtree(self.index_path)
        os.makedirs(self.index_path)

        schema = Schema(package_name=TEXT(stored=True), package_desc=TEXT(stored=True))

        self.index = create_in(self.index_path, schema)
        writer = self.index.writer()

        # Loop through all Wolfi files and add them to the index
        # TODO: Ugly code. Take out default use of tqdm
        file_names = os.listdir(self.os_path)
        for name in tqdm.tqdm(file_names, desc="Building local Wolfi package index"):
            if name.endswith(".yaml"):
                file_path = os.path.join(self.os_path, name)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                    # TODO: Why do some YAMLs not have a package section ?!
                    if "package" not in data.keys():
                        continue
                    
                    # TODO: Gracefully handle missing fields
                    try:
                        package_name = data["package"]["name"]
                        package_desc = data["package"]["description"]
                    except KeyError:
                        continue

                    writer.add_document(package_name=package_name, package_desc=package_desc)
        writer.commit()

    def search(self, keyword) -> List[WolfiPackageResult]:
        """
        Searches Wolfi for package names matching `keyword`.

        Args:
            keyword: The keyword to search package names for.
        
            Returns: A `List` of `WolfiPackageResult` objects.
        
        Raises:
            TypeError: If keyword is not a `str`.


        1) Clone wolfi
        2) Index search files
        3) perform the search
        """
        if not isinstance(keyword, str):
            raise TypeError("`keyword` must be a `str`.")
        
        with self.index.searcher() as searcher:
            name_query = QueryParser("package_name", self.index.schema).parse(keyword)
            desc_query = QueryParser("package_desc", self.index.schema).parse(keyword)
            combined_query = Or([name_query, desc_query])

            # Perform the search
            results = searcher.search(combined_query)
            
            output = []
            for r in results:
                name = r["package_name"]
                # TODO: Why aren't these keys guaranteed to be present in the result?
                if "package_desc" in r.keys():
                    desc = r["package_desc"]
                else:
                    desc = ""
                output.append(WolfiPackageResult(name, desc))
            return output
