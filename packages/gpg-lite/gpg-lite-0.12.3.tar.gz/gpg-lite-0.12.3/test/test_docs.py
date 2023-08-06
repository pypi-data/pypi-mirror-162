import unittest
from pathlib import Path

from test.test_gpg import ENV_WITH_GPG


@unittest.skipUnless(ENV_WITH_GPG, "Integration tests")
class TestDocs(unittest.TestCase):
    @staticmethod
    def test_gen_key() -> None:
        """Read the python code snippets from README and exec"""
        read = False
        code = ""
        with open(Path(__file__).parent.parent / "README.md", encoding="utf-8") as doc:
            for line in doc:
                if line == "```python\n":
                    read = True
                    continue
                if line == "```\n":
                    read = False
                    continue
                if read:
                    code += line

        exec(code)  # pylint: disable=exec-used
