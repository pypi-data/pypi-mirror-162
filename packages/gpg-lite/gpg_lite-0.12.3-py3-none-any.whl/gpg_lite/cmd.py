import io
import subprocess  # nosec
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from shutil import copyfileobj
from typing import (
    Optional,
    Tuple,
    Sequence,
    IO,
    Union,
    Any,
    Callable,
    Generator,
)

# Here bandit warns about:
# B404:blacklist import_subprocess
# B603:subprocess_without_shell_equals_true
# 1. We do not use shell=True in this package
# 2. All calls to subprocess start with gpg, so possibly unsanitized input would
#    only result in a gpg error message

ISource = Union[bytes, IO[bytes], Callable[[IO[bytes]], None]]
OSource = Union[int, IO[bytes], Callable[[IO[bytes]], None]]
# TODO: unquote the "subprocess.Popen[bytes]" type hint once we enforce python 3.9 (multiple occurrences)

if sys.platform == "win32":

    def startupinfo():
        _startupinfo = subprocess.STARTUPINFO()
        _startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        _startupinfo.wShowWindow = subprocess.SW_HIDE
        return _startupinfo

else:

    def startupinfo() -> bool:  # Literal[None] not supported by mypy
        return False


class GPGError(Exception):
    """Error class that forwards errors returned by calls to GnuPG."""


def raise_if_not_none(e: Optional[BaseException]) -> None:
    if e is not None:
        raise e


def cmd_devnull(
    command: Tuple[str, ...],
    src: Optional[ISource] = None,
    stdout: OSource = subprocess.DEVNULL,
    **kwargs: Any,
) -> None:
    with cmd_pipe(command, src=src, stdout=stdout, **kwargs):
        pass


@contextmanager
def cmd_pipe_stdout(*args: Any, **kwargs: Any) -> Generator[IO[bytes], None, None]:
    with cmd_pipe(*args, **kwargs) as proc:
        yield assert_io(proc.stdout)


@contextmanager
def cmd_pipe(
    command: Tuple[str, ...],
    src: Optional[ISource] = None,
    stdout: OSource = subprocess.PIPE,
    passphrase: Optional[str] = None,
    **kwargs: Any,
) -> Generator["subprocess.Popen[bytes]", None, None]:
    feed = None
    if src is not None:
        if has_fileno(src) and passphrase is None:
            kwargs["stdin"] = src
        else:
            kwargs["stdin"] = subprocess.PIPE
            feed = feed_from_any(src)
    sink = None
    if callable(stdout):
        sink = stdout
        stdout = subprocess.PIPE

    # For the bandit vulnerability suppressed here (nosec):
    # see info close the subprocess import
    with subprocess.Popen(  # nosec
        command,
        stderr=subprocess.PIPE,
        stdout=stdout,
        startupinfo=startupinfo() or None,
        **kwargs,
    ) as proc:
        if proc.stdin is not None:
            if passphrase is not None:
                proc.stdin.write(passphrase.encode() + b"\n")
                proc.stdin.flush()

            if feed is not None:
                if sink is not None and proc.stdout is not None:
                    with ThreadPoolExecutor(max_workers=2) as executor:
                        future_feed = executor.submit(feed, proc.stdin)
                        future_sink = executor.submit(sink, proc.stdout)
                        future_feed.add_done_callback(
                            lambda _: proc.stdin and proc.stdin.close()
                        )
                        raise_if_not_none(future_feed.exception())
                        raise_if_not_none(future_sink.exception())
                else:
                    feed(proc.stdin)
                    proc.stdin.close()

            elif sink is not None and proc.stdout is not None:
                sink(proc.stdout)

        yield proc
        err = proc.stderr.read() if proc.stderr is not None else b""
    if proc.returncode != 0:
        raise GPGError(err.decode("utf-8", "replace"))


def stderr_lookahead(proc: "subprocess.Popen[bytes]") -> bytes:
    if proc.stderr is not None:
        out: bytes = proc.stderr.read()
        proc.stderr.close()
        proc.stderr = io.BytesIO(out)
    else:
        out = b""
    return out


class ExpectProc:
    def __init__(self, proc: "subprocess.Popen[bytes]"):
        self.proc = proc
        self.source = assert_io(proc.stderr, name="stderr")
        self.dest = assert_io(proc.stdin, name="stdin")
        self.stdout = proc.stdout

    def expect(self, expected: bytes, prefix: bytes = b"[GNUPG:] GET_") -> None:
        actual = b""
        while not actual.startswith(prefix):
            actual = self.source.read(len(prefix))
            c = b"1"
            while c and c != b"\n":
                c = self.source.read(1)
                if c != b"\r":  # Skip '\r' (windows)
                    actual += c
            if not actual:
                raise ValueError("Unexpected end of source")
        if actual != expected:
            raise ValueError(
                f"Unexpected prompt from gpg:\n{expected.decode()}\n{actual.decode()}"
            )

    def put(self, msg: bytes) -> None:
        self.dest.write(msg)
        self.dest.flush()


@contextmanager
def expect(command: Sequence[str], **kwargs: Any) -> Generator[ExpectProc, None, None]:
    # For the bandit vulnerability suppressed here (nosec):
    # see info close the subprocess import
    with subprocess.Popen(  # nosec
        command,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        **kwargs,
    ) as proc:
        yield ExpectProc(proc)


def feed_from_any(src: ISource) -> Callable[[IO[bytes]], None]:
    if isinstance(src, bytes):
        return feed_from_str(src)
    if callable(src):
        return feed_from_callable(src)
    return feed_from_stream(src)


def feed_from_str(src: bytes) -> Callable[[IO[bytes]], None]:
    def feed(stdin: IO[bytes]) -> None:
        stdin.write(src)

    return feed


def feed_from_stream(src: IO[bytes]) -> Callable[[IO[bytes]], None]:
    def feed(stdin: IO[bytes]) -> None:
        copyfileobj(src, stdin)

    return feed


def feed_from_callable(src: Callable[[IO[bytes]], None]) -> Callable[[IO[bytes]], None]:
    def feed(stdin: IO[bytes]) -> None:
        src(stdin)

    return feed


def has_fileno(s: Any) -> bool:
    if hasattr(s, "fileno"):
        try:
            s.fileno()
        except Exception:  # pylint: disable=broad-except
            return False
        return True
    return False


def assert_io(stream: Optional[IO[bytes]], name: str = "stdout") -> IO[bytes]:
    if stream is None:
        raise ValueError(f"Unexpected {name} of type NoneType.")
    return stream
