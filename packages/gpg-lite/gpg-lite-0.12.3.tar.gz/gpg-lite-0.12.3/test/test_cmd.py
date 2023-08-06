import unittest

from gpg_lite import cmd


class TestGPG(unittest.TestCase):
    def test_cmd_pipe(self) -> None:
        with self.assertRaises(FileNotFoundError):
            with cmd.cmd_pipe(("non-existing-bin",)) as proc:
                cmd.assert_io(proc.stdout).read()

        with self.assertRaises((cmd.GPGError, FileNotFoundError)):
            with cmd.cmd_pipe(("python3", "--non-existing-option")) as proc:
                cmd.assert_io(proc.stdout).read()
