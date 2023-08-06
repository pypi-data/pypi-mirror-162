from typing import (
    Optional,
    Union,
    Callable,
    Iterator,
    Tuple,
    List,
    Iterable,
    Dict,
    TypeVar,
    Type,
    cast,
)

T = TypeVar("T")
V = TypeVar("V")
FT = TypeVar("FT")

TokenStream = Tuple[T, ...]
FoldTokenStream = Tuple[Union[T, TokenStream[T]], ...]
Rule = Callable[..., List[T]]

Grammar = Dict[FoldTokenStream[Type[T]], Rule[T]]


def compile_grammar(
    grammar: Grammar[T], final_token: Type[FT]
) -> Callable[[List[T]], FT]:
    """Return a token parser that transforms an initial sequence of tokens
    by consecutively applying a set of rules to the sequence.

    A rule consists of a pattern of token types and a transforming function.
    When the initial sequence reduces to the final token (identified
    by its "final_token" type), the processing of tokens is stopped.

    :param grammar: dict of the form "pattern": "rule", where each pattern is a
        tuple of tokens that correspond to two consecutive lines of output of
        the gpg command.
    :param final_token: object that has a different type than any other "token"
        in the list of "tokens" passed to the "process" function returned
        by compile_grammar. Typically the final token is a list.
    :return: function that applies rules to a list of tokens.
    """
    unfold_grammar: Dict[TokenStream[Type[T]], Rule[T]] = expand_token_sequences(
        grammar
    )
    intermediate_token_sequences = frozenset(
        {s[:i] for s in unfold_grammar for i in range(1, len(s))} | {()}
    ) - frozenset(unfold_grammar)

    def scan_pattern_at_start(
        tokens: Iterator[T],
    ) -> Tuple[Optional[Rule[T]], Optional[int]]:
        """Look at the beginning of the tokens sequence. If the beginning
        matches a pattern associated to a rule in the grammar, then this rule
        is returned.

        :param tokens: generator of tokens.
        :return: rule (function) to be applied to the matched token subsequence.
        """
        token_pattern: Tuple[type, ...] = ()
        while token_pattern in intermediate_token_sequences:
            try:
                token_pattern += (type(next(tokens)),)
            except StopIteration:
                return None, None
        rule = unfold_grammar.get(token_pattern)
        if rule is not None:
            return rule, len(token_pattern)
        return None, None

    def scan_pattern(tokens: List[T]) -> Optional[Tuple[Rule[T], slice]]:
        """General form of :scan_pattern_at_start:. Also matches in the interior
        of the token sequence.
        """
        for pos in range(len(tokens)):
            rule, L = scan_pattern_at_start(iter(tokens[pos:]))
            if rule is not None and L is not None:
                return rule, slice(pos, pos + L)
        return None

    def process(tokens: List[T]) -> FT:
        """Process tokens in the tokens sequence until there is only one token
        left whose type matches the type of final token.
        """
        while [type(token) for token in tokens] != [final_token]:
            match = scan_pattern(tokens)
            if match is None:
                raise ValueError(
                    "Unexpected sequence of tokens:", [type(token) for token in tokens]
                )
            rule, slc = match
            # Apply the rule to the matched subsequence
            subs = rule(*tokens[slc])

            tokens = (
                tokens[: slc.start] + subs + tokens[slc.stop :]
            )  # pylint: disable=invalid-slice-index
        return cast(FT, tokens[0])

    return process


def expand_token_sequences(
    grammar: Dict[FoldTokenStream[T], V]
) -> Dict[TokenStream[T], V]:
    return {
        key: val for keys, val in grammar.items() for key in expand_token_sequence(keys)
    }


def expand_token_sequence(
    seq: FoldTokenStream[T],
) -> Iterable[TokenStream[T]]:
    distinction_found = False
    for i, t in enumerate(seq):
        if isinstance(t, tuple):
            distinction_found = True
            for sub_t in t:
                yield from expand_token_sequence(seq[:i] + (sub_t,) + seq[i + 1 :])
    if not distinction_found:
        yield cast(TokenStream[T], seq)
