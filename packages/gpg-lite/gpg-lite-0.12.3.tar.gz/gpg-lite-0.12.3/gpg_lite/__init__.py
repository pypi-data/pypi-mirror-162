import base64
import io
from contextlib import contextmanager
from typing import Optional, Iterator, IO

from .cmd import GPGError
from .model import (
    CompressAlgo,
    Key,
    KeyCapability,
    KeyInfo,
    KeyType,
    RevocationSignature,
    Signature,
    SignatureValidity,
    SubKey,
    TrustModel,
    Uid,
    Validity,
)
from .store import GPGStore, get_default_gnupg_home_dir
from .keyserver import (
    search_keyserver,
    KeyserverError,
    KeyserverKeyNotFoundError,
    KeyserverOtherError,
)
from .version import __version__

__all__ = [
    "CompressAlgo",
    "GPGError",
    "GPGStore",
    "Key",
    "KeyCapability",
    "KeyInfo",
    "KeyType",
    "RevocationSignature",
    "Signature",
    "SignatureValidity",
    "SubKey",
    "TrustModel",
    "Uid",
    "Validity",
    "extract_key_id",
    "extract_key_id_from_sig",
    "get_default_gnupg_home_dir",
    "public_key_encrypted_session_key_packet",
    "search_keyserver",
    "signature_packet",
    "KeyserverError",
    "KeyserverKeyNotFoundError",
    "KeyserverOtherError",
]


def extract_key_id(src: IO[bytes]) -> Iterator[str]:
    """Extract the public key_id from an encrypted message"""
    try:
        with preserve_pos(src):
            while True:
                fpr = extract_key_id_once(src)
                if fpr is None:
                    break
                yield fpr
    except ValueError as e:
        marker = b"-----BEGIN "
        src.seek(0)
        msg_start = src.read(len(marker))
        if msg_start == marker:
            raise GPGError("ASCII armored encrypted data is not supported") from e
        raise GPGError(f"Corrupted encrypted message: {e}") from e


def public_key_encrypted_session_key_packet(src: IO[bytes]) -> bytes:
    """type 1: Public-Key Encrypted Session Key Packet"""
    _version = src.read(1)
    return src.read(8)


def signature_packet(src: IO[bytes]) -> bytes:
    """Type 2: Signature Packet"""
    (version,) = src.read(1)
    if version == 3:
        (length,) = src.read(1)
        if length != 5:
            raise ValueError(f"Invalid length: {length}. Should be 5")
        _sigtype = src.read(1)
        _creationtime = src.read(4)
        return src.read(8)

    if version == 4:
        # fpr starts at octet 12
        _sigtype = src.read(1)
        _pubkeyalgorithm = src.read(1)
        _hashalgorithm = src.read(1)
        # Version 4 Signature Packet Format contains two blocks of subpackets.
        # Try extracting a fingerprint from the hashed subpackets block.
        # If the fingerprint subpacket is missing, extract a key id from
        # the unhashed subpackets block.
        for _ in range(2):
            octet_count = int.from_bytes(src.read(2), "big")
            subpackets_end = src.tell() + octet_count
            while src.tell() < subpackets_end:
                key_id = read_subpacket(src)
                if key_id:
                    return key_id
        _signedhash = src.read(2)
        raise ValueError(
            "No issuer fingerprint/key_id subpacket found in signature packet"
        )

    raise ValueError(f"Invalid version: {version}. Only 3 and 4 are supported")


def read_subpacket(src: IO[bytes]) -> Optional[bytes]:
    l = read_new_packet_len(src)
    if l is None:
        return None
    (pkg_type,) = src.read(1)
    body = src.read(l - 1)
    if pkg_type == 33:  # type 33: Issuer Fingerprint (rfc4880bis)
        # The first octet is key version number
        return body[1:]
    if pkg_type == 16:  # type 16: Issuer
        return body
    return None


PACKET_HANDLERS = {1: public_key_encrypted_session_key_packet, 2: signature_packet}


def read_new_packet_len(src: IO[bytes]) -> Optional[int]:
    (l,) = src.read(1)
    if l < 192:  # 1 octet length
        return l
    if l <= 223:  # 2 octet length
        (l2,) = src.read(1)
        return ((l - 192) << 8) + l2 + 192
    # 224 <= l < 255: Partial Body Lengths (=> header has length 1)
    if l < 255:
        return None
    if l == 255:  # 5 octet length
        l2, l3, l4, l5 = src.read(4)
        return (l2 << 24) | (l3 << 16) | (l4 << 8) | l5
    raise ValueError(f"Invalid length: {l}")


def extract_key_id_from_sig(src: bytes) -> Optional[str]:
    """Extract key id from a signature packet. Either ascii armored or binary"""
    if src[0] == b"-"[0]:
        src = ascii_armored_to_binary(src)
    try:
        return extract_key_id_once(io.BytesIO(src))
    except ValueError as e:
        raise GPGError(
            "Found an invalid pgp signature while trying to extract a key id"
        ) from e


def extract_key_id_once(src: IO[bytes]) -> Optional[str]:
    """Reads one packet from src.

    According to https://www.ietf.org/rfc/rfc4880.txt and rfc4880bis
    """
    try:
        (packet_hdr,) = src.read(1)
    except ValueError:
        return None
    # 1st bit must be 1
    if not packet_hdr & 0x80:
        raise ValueError("Not a valid packet tag")
    # 2nd bit is packet version (new / old)
    new_version = packet_hdr & 0x40
    packet_type = packet_hdr & 0b00111111
    if not new_version:
        packet_type >>= 2
    pkg_handler = PACKET_HANDLERS.get(packet_type)
    if pkg_handler is None:
        return None
    if not new_version:
        packet_length_type = packet_hdr & 0b11
        body_offs_by_len_type = {0: 2, 1: 3, 2: 5, 3: 1}
        try:
            packet_len_size = body_offs_by_len_type[packet_length_type] - 1
        except KeyError as e:
            raise ValueError(f"Invalid packet length type: {packet_length_type}") from e
        if packet_length_type == 3:  # The packet is of indeterminate length
            packet_len = None
        else:
            packet_len = int.from_bytes(src.read(packet_len_size), "big")
    else:
        packet_len = read_new_packet_len(src)
    if packet_len is not None and packet_len < 10:
        raise ValueError(f"Unexpected packet length of {packet_len}")
    body_start = src.tell()
    pub_key_id = pkg_handler(src)
    if packet_len:
        src.seek(body_start + packet_len)
    else:
        src.seek(0, 2)
    return pub_key_id.hex().upper()


@contextmanager
def preserve_pos(src: IO[bytes]) -> Iterator[IO[bytes]]:
    pos = src.tell()
    yield src
    src.seek(pos)


def ascii_armored_to_binary(src: bytes) -> bytes:
    header, _, *lines, footer = src.splitlines()
    # If the last line is empty, continue to the last not empty line:
    while not footer:
        footer = lines.pop()
    if header != b"-----BEGIN PGP SIGNATURE-----":
        raise ValueError(f"Invalid ascii armored signature header: '{header.decode()}'")
    if footer != b"-----END PGP SIGNATURE-----":
        raise ValueError(f"Invalid ascii armored signature footer: '{footer.decode()}'")
    return base64.decodebytes(b"".join(l for l in lines if l))
