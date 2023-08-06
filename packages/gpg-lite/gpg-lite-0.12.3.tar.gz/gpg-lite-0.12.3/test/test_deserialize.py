import unittest
from typing import Tuple, Dict, Optional, cast
import sys
from dataclasses import dataclass

from gpg_lite import deserialize

# deserialize is shadowed by deserialize.deserialize:
deserialize = sys.modules["gpg_lite.deserialize"]


class TestDeserialize(unittest.TestCase):
    def test_dict_type(self) -> None:
        self.assertEqual(deserialize.dict_type(Dict[int, str]), (int, str))
        self.assertEqual(deserialize.dict_type(int), None)

    def test_deserialize(self) -> None:
        @dataclass
        class Y:
            x: int
            y: Tuple[bool, ...]

        @dataclass
        class X:
            a: int
            pack: Y

        data = {"a": 1, "pack": {"x": 1, "y": [True, False]}}
        x = deserialize.deserialize(X)(data)

        self.assertEqual(x, X(a=1, pack=Y(x=1, y=(True, False))))

        # typing.Dict
        @dataclass
        class Z:
            a: int
            dct: Dict[int, str]

        inner = {1: "x", 2: "y"}
        data = {"a": 1, "dct": inner}
        z = deserialize.deserialize(Z)(data)

        self.assertEqual(z, Z(a=1, dct=inner))

        # typing.Optional
        self.assertEqual(deserialize.deserialize(cast(type, Optional[int]))(None), None)
        self.assertEqual(deserialize.deserialize(cast(type, Optional[int]))(1), 1)
