# Standard lib
import os

# 3rd party
import pytest

# Local
from chaingpt.api.wolfi import WolfiClient


class TestWolfiClient:
    def test__search__match(self):
        """
        Checks that the correct packages are returned for
        a matching `keyword`.
        """
        client = WolfiClient()
        results = client.search("python")
        names = [r.name for r in results]
        assert "python-3.10" in names
        assert "python-3.11" in names
        assert "python-3.12" in names


    def test__search__no_matches(self):
        """
        Checks that no packages are returned for a `keyword`
        not matching any packages.
        """
        client = WolfiClient()
        results = client.search("nothing")
        assert results == []


    def test__search__keyword_is_not_str(self):
        """
        Checks that a `TypeError` is raised if `keyword`
        is not a `str`.
        """
        with pytest.raises(TypeError):
            WolfiClient().search(123)
