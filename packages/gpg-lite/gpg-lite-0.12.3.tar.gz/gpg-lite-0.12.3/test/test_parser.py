import unittest
from typing import Dict

from gpg_lite import parser


class TestParser(unittest.TestCase):
    def test_expand_token_sequence(self) -> None:
        seq: parser.FoldTokenStream[int] = (1, 2, 3)
        self.assertEqual([seq], list(parser.expand_token_sequence(seq)))
        seq = ((1, 2), 2, 3)
        self.assertEqual({(1, 2, 3), (2, 2, 3)}, set(parser.expand_token_sequence(seq)))
        seq = (1, (2, 3), (2, 3, 4))
        self.assertEqual(
            {(1, i, j) for i in (2, 3) for j in (2, 3, 4)},
            set(parser.expand_token_sequence(seq)),
        )

    def test_expand_token_sequences(self) -> None:
        seqs: Dict[parser.FoldTokenStream[int], int] = {
            (0, 2, 3): 1,
            (1, (2, 3), (2, 3, 4)): 2,
        }
        ref_seqs = {(1, i, j): 2 for i in (2, 3) for j in (2, 3, 4)}
        ref_seqs[(0, 2, 3)] = 1
        self.assertEqual(parser.expand_token_sequences(seqs), ref_seqs)
