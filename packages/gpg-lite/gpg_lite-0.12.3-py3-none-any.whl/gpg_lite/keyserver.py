import json
import re
import urllib.request
from dataclasses import dataclass
from enum import Enum
from http.client import HTTPResponse
from typing import Dict, Optional, Sequence, Union, Tuple, Iterator, IO, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, quote, urljoin

from .deserialize import deserialize
from .model import KeyInfo, Uid

DEFAULT_URL_OPENER = urllib.request.build_opener(
    urllib.request.HTTPSHandler(debuglevel=0)
).open
UrlOpener = Callable[[Union[str, urllib.request.Request]], HTTPResponse]


class KeyserverError(Exception):
    """Error class that displays an error message when the keyserver cannot
    be reached.

    :param action: either "download", "upload", "search".
    :param keyserver: URL of keyserver.
    """

    def __init__(self, action: str, keyserver: str):
        super().__init__(
            f"Key {action} failed because the specified keyserver "
            f"[{keyserver}] could not be reached. The keyserver might be "
            "temporarily unavailable or a wrong URL was provided. "
            "Try connecting to the keyserver using your web browser to "
            "confirm whether the keyserver is available or not."
        )


class KeyserverKeyNotFoundError(Exception):
    """Error class that displays an error message when a given key cannot be
    found on a keyserver.

    :param keyserver: URL of keyserver.
    :param fingerprint: fingerprint of PGP key that could not be found.
    """

    def __init__(self, keyserver: str, fingerprint: str):
        super().__init__(
            f"Key [{fingerprint}] was not found on the keyserver [{keyserver}]."
        )


class KeyserverOtherError(Exception):
    """Keyserver errors not covered by the more specific variants."""


def parse_search_keyserver(source: IO[bytes]) -> Iterator[KeyInfo]:
    """Extract key information (fingerprint, user ID) from the string returned
    by a search request made via the OpenPGP HTTP Keyserver Protocol. See
    https://tools.ietf.org/html/draft-shaw-openpgp-hkp-00 for details.

    Example of keyserver response to key index search:
    info:1:1
    pub:AA1020B5F0F873830B9AF245AA2BB155CF133521:1:4096:1593675716::
    uid:Alice Smith <alice.smith@example.com>:1593675716::
    """
    try:
        b_line = next(source).rstrip(b"\r\n")
    except StopIteration:
        return
    if not b_line.startswith(b"info:"):
        raise ValueError(
            "Unknown response format from gpg, starting with\n"
            + b_line.decode("utf-8", "replace")
        )
    for b_line in source:
        line = b_line.decode("utf-8", "replace").rstrip("\r\n")
        if not line:
            continue
        try:
            (
                hdr_key,
                fingerprint,
                algorithm,
                key_length,
                creation_date,
                expiration_date,
                _,
            ) = line.split(":")
        except ValueError as e:
            raise ValueError(f"Wrong format for search_key: {line}") from e
        try:
            hdr_uid, uid_str, _, _, _ = (
                next(source).decode("utf-8", "replace").rstrip("\n").split(":")
            )
        except StopIteration as e:
            raise ValueError("Unexpected end of source. Expected 'uid:' line") from e
        if hdr_key != "pub":
            raise ValueError(
                f"Unknown response format from gpg: "
                f"expected 'pub:', got '{hdr_key}'"
            )
        if hdr_uid != "uid":
            raise ValueError(
                f"Unknown response format from gpg: "
                f"expected 'uid:', got '{hdr_uid}'"
            )
        uid = Uid.from_str(unquote(uid_str))
        if uid is None:
            raise ValueError("Could not determine uid from gpg response.")
        yield KeyInfo(
            uid=uid,
            fingerprint=fingerprint,
            key_algorithm=int(algorithm),
            creation_date=creation_date,
            expiration_date=expiration_date or None,
            key_length=int(key_length),
        )


def _validate_hex(s: str) -> None:
    try:
        int(s, 16)
    except ValueError as e:
        raise ValueError("Invalid characters found (allowed: 0-9A-Fa-f)") from e


def normalize_fingerprint(fp: str) -> str:
    valid_len = (8, 16, 32, 40)
    s = re.sub(r"^0[xX]", "", re.sub(r"\s", "", fp))
    if len(s) not in valid_len:
        raise ValueError(f"Invalid fingerprint length. Allowed lengths {valid_len}")
    _validate_hex(s)
    return f"0x{s}"


def search_keyserver(
    search_term: str, keyserver: str, url_opener: UrlOpener = urllib.request.urlopen
) -> Iterator[KeyInfo]:
    """Search for a key on a keyserver supporting the OpenPGP HTTP Keyserver
    Protocol, e.g. an SKS keyserver.

    :param search_term: search term. This can be either a key fingerprint,
        key ID or part of the key user ID (e.g. email address).
    :param keyserver: URL of keyserver where to search for keys.
    :param url_opener: function/wrapper through which to make the http request.
    :return: key information summary.
    :raises KeyserverError: error raised if the keyserver does not respond
        (e.g. wrong URL) or does not accept the request for any other reason.
    """
    try:
        queries = {normalize_fingerprint(search_term), search_term}
    except ValueError:
        queries = {search_term}

    for query in queries:
        try:
            with query_keyserver(
                keyserver=keyserver, query=query, op="index", url_opener=url_opener
            ) as response:
                yield from parse_search_keyserver(response)

        except HTTPError as e:
            if e.code != 404:
                raise KeyserverError(action="search", keyserver=keyserver) from e

        except URLError as e:
            raise KeyserverError(action="search", keyserver=keyserver) from e


def download_key(
    fingerprint: str,
    keyserver: str,
    url_opener: UrlOpener = urllib.request.urlopen,
    **kwargs: str,
) -> HTTPResponse:
    """Download key from keyserver to a user's local keyring.

    Keys can only be retrieved via their fingerprint, or key ID. It is
    recommended to use full fingerprints (40 chars hexadecimal string) to
    avoid key collisions.

    :param fingerprint: fingerprint (40 chars) or key ID (8, 16 or 32 chars) of
        the key to download.
    :param keyserver: URL of keyserver from where to download keys.
    :param kwargs:
    :return: urlopen context manager containing the downloaded PGP key.
    :raises KeyserverError: error raised if the keyserver does not respond
        (e.g. wrong URL) or does not accept the request for any other reason.
    :raises KeyserverKeyNotFoundError: error raised if no key matching the
        specified fingerprint is present on the keyserver.
    """
    try:
        return query_keyserver(
            keyserver=keyserver,
            query=normalize_fingerprint(fingerprint),
            op="get",
            exact="on",
            url_opener=url_opener,
            **kwargs,
        )

    except HTTPError as e:
        if e.code == 404:
            raise KeyserverKeyNotFoundError(keyserver, fingerprint) from None
        raise KeyserverError(action="download", keyserver=keyserver) from e

    except URLError as e:
        raise KeyserverError(action="download", keyserver=keyserver) from e


def query_keyserver(
    keyserver: str,
    query: str,
    op: str,
    url_opener: UrlOpener = urllib.request.urlopen,
    **parameters: str,
) -> HTTPResponse:
    """Send a request to a keyserver supporting the OpenPGP HTTP Keyserver
    Protocol, e.g. to download a key or retrieve information about a key.

    :param keyserver: URL of keyserver to query.
    :param query: search/query term, e.g. a normalized fingerprint or email
        address.
    :param op: operation type to perform, e.g. "index" to list keys or "get"
        to download keys.
    :param url_opener: function/wrapper through which to make the http request.
    :param parameters: optional arguments to pass to the request.
    :return: urlopen context manager containing the data returned by the query
        made to the keyserver.
    :raises ValueError: error is raised if keyserver URL is incorrect.
    """
    url = build_host(keyserver)
    query_url = f"{url}/pks/lookup?search={quote(query)}&op={op}&options=mr" + "".join(
        f"?{key}={val}" for key, val in parameters.items()
    )
    return url_opener(query_url)


def split_host(url: str) -> Tuple[Optional[str], str, Optional[str]]:
    match = re.fullmatch(r"(https?://|hkp://)?([^:]+)(:[0-9]+)?", url)
    if not match:
        raise ValueError(f"Invalid URL: {url}")
    scheme, host, port = match.groups()
    return scheme, host, port


def build_host(url: str) -> str:
    scheme, host, port = split_host(url)
    if scheme not in {"http://", "https://"}:
        if port in {":80", ":8080", ":11371"}:
            scheme = "http://"
        else:
            scheme = "https://"
    if port is None:
        if scheme == "https://":
            port = ":443"
        else:
            port = ":80"
    return scheme + host + port


def upload_keys(
    keys_as_ascii_armor: bytes,
    keyserver: str,
    url_opener: UrlOpener = DEFAULT_URL_OPENER,
) -> None:
    """Upload one or more keys to a SKS keyserver.

    Following https://tools.ietf.org/html/draft-shaw-openpgp-hkp-00#page-6,
    Section 4

    :param keys_as_ascii_armor: ascii representation of a PGP key.
    :param keyserver: URL of keyserver to upload keys to.
    :param url_opener: function/wrapper through which to make the http request.
    :raises KeyserverError: error raised if the keyserver does not respond or
        is otherwise unreachable (e.g. wrong URL).
    """
    try:
        post(
            url=build_host(keyserver) + "/pks/add",
            data=b"keytext=" + quote(keys_as_ascii_armor).encode(),
            url_opener=url_opener,
        )
    except URLError as e:
        raise KeyserverError(action="upload", keyserver=keyserver) from e


def post(url: str, data: bytes, url_opener: UrlOpener = DEFAULT_URL_OPENER) -> bytes:
    """Send a POST request containing "data" to the specified "url".

    :param url: URL where to send the POST request.
    :param data: data (bytes) to send in the POST request.
    :param url_opener: function/wrapper through which to make the http request.
    """
    request = urllib.request.Request(
        url,
        data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    # Make the request using the specified URL opener and return the text
    # contained in the response from the server.
    with url_opener(request) as response:
        return response.read()


class VksEmailStatus(Enum):
    UNPUBLISHED = "unpublished"
    PUBLISHED = "published"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass
class VksUploadResponse:
    key_fpr: str
    status: Dict[str, VksEmailStatus]
    token: str


def _vks_into_hex(value: str, size: int) -> str:
    """Remove `0x` prefix, white spaces, and make the string uppercase."""
    s = re.sub(r"^0[xX]", "", re.sub(r"\s", "", value)).upper()
    if len(s) != size:
        raise ValueError(
            f"Invalid fingerprint/key ID length (expected: {size}, given: {len(s)})"
        )
    _validate_hex(s)
    return s


def _vks_get(
    fetch_by: str,
    query: str,
    keyserver: str,
    url_opener: UrlOpener = DEFAULT_URL_OPENER,
) -> HTTPResponse:
    """Base function to download a PGP key from a VKS keyserver.

    Queries the specified VKS keyserver for a PGP key based on either email,
    fingerprint (40 chars) of long key ID (16 chars). Only works with Verifying
    Keyservers (VKS).

    :param fetch_by: type of key identifier passed in the `query` argument.
        One of "fingerprint", "email" or "keyid".
    :param query: key identifier of PGP key to download.
    :param keyserver: URL of keyserver.
    :param url_opener: optional, custom URL opener function (e.g. when using a
        proxy).
    :return: response of keyserver.
    :raises KeyserverError, KeyserverKeyNotFoundError, KeyserverOtherError:
    """
    keyserver_base = build_host(keyserver)
    try:
        return url_opener(urljoin(keyserver_base, f"/vks/v1/by-{fetch_by}/{query}"))
    except HTTPError as e:
        msg = e.read().decode().strip()
        if e.code == 404:
            raise KeyserverKeyNotFoundError(keyserver, unquote(query)) from None
        if e.code == 429:
            raise KeyserverOtherError(
                f"Keyserver query limit has been reached ({msg})"
            ) from e
        raise KeyserverOtherError(f"{e} ({msg})") from e
    except URLError as e:
        raise KeyserverError(action="download", keyserver=keyserver) from e


def vks_get_key_by_fingerprint(
    keyserver: str, fingerprint: str, url_opener: UrlOpener = DEFAULT_URL_OPENER
) -> HTTPResponse:
    """Download a key from a Verifying Keyserver by fingerprint.

    The Fingerprint may refer to the primary key, or any subkey.
    """
    return _vks_get(
        fetch_by="fingerprint",
        query=_vks_into_hex(fingerprint, 40),
        keyserver=keyserver,
        url_opener=url_opener,
    )


def vks_get_key_by_keyid(
    keyserver: str, keyid: str, url_opener: UrlOpener = DEFAULT_URL_OPENER
) -> HTTPResponse:
    """Download a key from a Verifying Keyserver by key ID.

    The key ID may refer to the primary key, or any subkey.
    """
    return _vks_get(
        fetch_by="keyid",
        query=_vks_into_hex(keyid, 16),
        keyserver=keyserver,
        url_opener=url_opener,
    )


def vks_get_key_by_email(
    keyserver: str, email: str, url_opener: UrlOpener = DEFAULT_URL_OPENER
) -> HTTPResponse:
    """Download a key from a Verifying Keyserver by email.

    The email address may refer to the primary key, or any subkey.
    """
    return _vks_get(
        fetch_by="email",
        query=quote(email),
        keyserver=keyserver,
        url_opener=url_opener,
    )


def vks_get_key_by_any_identifier(
    keyserver: str, identifier: str, url_opener: UrlOpener = DEFAULT_URL_OPENER
) -> HTTPResponse:
    """Download a key from a Verifying Keyserver by Fingerprint, key ID, or email."""
    # Case 1: the identifier is an email address.
    if "@" in identifier:
        return vks_get_key_by_email(
            keyserver=keyserver, email=identifier, url_opener=url_opener
        )

    # Case 2: the identified is a fingerprint (40 chars).
    try:
        return vks_get_key_by_fingerprint(
            keyserver=keyserver, fingerprint=identifier, url_opener=url_opener
        )
    except ValueError:
        pass

    # Case 3: the identified is a long key ID (16 chars)
    try:
        return vks_get_key_by_keyid(
            keyserver=keyserver, keyid=identifier, url_opener=url_opener
        )
    except ValueError:
        pass
    raise ValueError("Provided identifier is not a fingerprint, key ID, or email")


def _vks_post(
    data: bytes, path: str, keyserver: str, url_opener: UrlOpener
) -> VksUploadResponse:
    """Base function for making POST request to a verifying keyserver (VKS)."""
    keyserver_base = build_host(keyserver)
    request = urllib.request.Request(
        url=urljoin(keyserver_base, path),
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with url_opener(request) as r:
            return deserialize(VksUploadResponse)(json.loads(r.read()))
    except HTTPError as e:
        msg = json.loads(e.read())["error"]
        raise KeyserverOtherError(f"{e} ({msg})") from e
    except URLError as e:
        raise KeyserverError(action="post", keyserver=keyserver) from e


def vks_upload_key(
    key: str, keyserver: str, url_opener: UrlOpener = DEFAULT_URL_OPENER
) -> VksUploadResponse:
    """Upload a key to a Verifying Keyserver."""
    return _vks_post(
        data=json.dumps({"keytext": key}).encode(),
        path="/vks/v1/upload",
        keyserver=keyserver,
        url_opener=url_opener,
    )


def vks_request_verify(
    token: str,
    addresses: Sequence[str],
    keyserver: str,
    url_opener: UrlOpener = DEFAULT_URL_OPENER,
) -> VksUploadResponse:
    """Request verification for one or more email addresses.

    A Verifying Keyserver sends verification emails to in order to establish
    a proof of ownership of an email address associated with a given key.
    Verified keys are discoverable by email on the keyserver. Non-verified keys
    are only discoverable by their fingerprint.
    """
    return _vks_post(
        data=json.dumps({"token": token, "addresses": addresses}).encode(),
        path="/vks/v1/request-verify",
        keyserver=keyserver,
        url_opener=url_opener,
    )
