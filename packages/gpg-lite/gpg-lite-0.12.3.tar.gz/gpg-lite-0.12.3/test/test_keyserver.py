import functools
import io
import json
import os
import tempfile
import unittest
from dataclasses import dataclass
from email.message import Message
from test.test_gpg import (
    CN_FINGERPRINT,
    CN_PUB_KEY,
    CN_UID,
    ENV_WITH_GPG,
    KEY_SERVER,
    SGT_HARTMANN_PUB_KEY,
    UMLAUTS_FINGERPRINT,
    UMLAUTS_PUB_KEY,
    UMLAUTS_UID,
    IntegrationTest,
)
from typing import Any, Dict, Optional, IO
from unittest import mock
from urllib.error import HTTPError, URLError

import pytest

import gpg_lite as gpg
from gpg_lite import keyserver
from gpg_lite.deserialize import deserialize

ENV_KEY_SERVER = os.environ.get("KEY_SERVER", None)
KEY_SERVER = "http://hagrid.hogwarts.org:11371"


@dataclass
class MockHTTPError(HTTPError):  # pylint: disable=too-many-ancestors

    url: str = KEY_SERVER
    code: int = 400
    msg: str = "bad request"
    hdrs: Message = Message()
    fp: IO[bytes] = io.BytesIO(b"")

    def read(self, *args: Any) -> bytes:  # pylint: disable=unused-argument
        return b"This server is no longer under human control."


# Variables holding different types of errors to simulate non-responding
# keyserver or bad response from keyserver.
_URLError = URLError("timeout")
HTTPError_401 = MockHTTPError(code=401, msg="unauthorized")
HTTPError_404 = MockHTTPError(code=404, msg="not found")


def test_vks_get_key_by_email_failure() -> None:
    email = "alice@example.org"
    expected_error_msg = (
        f"Key \\[{email}\\] was not found on the keyserver \\[{KEY_SERVER}\\]"
    )
    with pytest.raises(keyserver.KeyserverKeyNotFoundError, match=expected_error_msg):
        keyserver.vks_get_key_by_email(
            keyserver=KEY_SERVER,
            email=email,
            url_opener=mock.Mock(side_effect=HTTPError_404),
        )


class TestKeyserver(unittest.TestCase):
    def test_parse_search_keyserver(self) -> None:
        response = io.BytesIO(
            b"""info:1:1
pub:CB5A3A5C2C4419BB09EFF879D6D229C51AB5D107:1:2048:1550241679::
uid:Chuck Norris <chuck.norris@roundhouse.gov>:1550241679::

pub:F119E26211119BB09EFF879D6D229C51AB5D107C:1:2048:1550241679::
uid:With Uml%C3%A4uts <with.umlauts@umlauts.info>:1550241679::

pub:DB5A3A5C2C4419BB09EFF879D6D229C51AB5D107:1:4096:1550241679:1850241679:
uid:Chuck Norris <chuck.norris@roundhouse.gov>:1650241679::
"""
        )
        keys = list(keyserver.parse_search_keyserver(response))
        self.assertEqual(
            keys,
            [
                gpg.KeyInfo(
                    uid=CN_UID,
                    fingerprint=CN_FINGERPRINT,
                    key_algorithm=1,
                    key_length=2048,
                    creation_date="1550241679",
                    expiration_date=None,
                ),
                gpg.KeyInfo(
                    uid=UMLAUTS_UID,
                    fingerprint=UMLAUTS_FINGERPRINT,
                    key_algorithm=1,
                    key_length=2048,
                    creation_date="1550241679",
                    expiration_date=None,
                ),
                gpg.KeyInfo(
                    uid=CN_UID,
                    fingerprint="DB5A3A5C2C4419BB09EFF879D6D229C51AB5D107",
                    key_algorithm=1,
                    key_length=4096,
                    creation_date="1550241679",
                    expiration_date="1850241679",
                ),
            ],
        )

    def test_normalize_fingerprint(self) -> None:
        for length in (8, 16, 32, 40):
            fp = "A" * length
            self.assertEqual(keyserver.normalize_fingerprint(fp), f"0x{fp}")
            self.assertEqual(keyserver.normalize_fingerprint(f"0x{fp}"), f"0x{fp}")
        self.assertEqual(keyserver.normalize_fingerprint("123 af  47a"), "0x123af47a")
        with self.assertRaises(ValueError):
            keyserver.normalize_fingerprint("A" * 7)
        with self.assertRaises(ValueError):
            keyserver.normalize_fingerprint("Z" * 8)

    def test_search_keyserver(self) -> None:
        # Check that passing a non-existing keyserver value raises the correct
        # type of error.
        search_keyserver = functools.partial(
            keyserver.search_keyserver,
            search_term=CN_FINGERPRINT,
            keyserver=KEY_SERVER,
        )
        with self.assertRaises(keyserver.KeyserverError):
            list(search_keyserver(url_opener=mock.Mock(side_effect=_URLError)))

        # Check that a missing key does not raises an error, and that any other
        # type of HTTPError does raise an error.
        list(search_keyserver(url_opener=mock.Mock(side_effect=HTTPError_404)))
        with self.assertRaises(keyserver.KeyserverError):
            list(search_keyserver(url_opener=mock.Mock(side_effect=HTTPError_401)))

    def test_download_key(self) -> None:
        # Check that an urllib error of type URLError or HTTPError raises the
        # correct type of error.
        download_key = functools.partial(
            keyserver.download_key,
            fingerprint=CN_FINGERPRINT,
            keyserver=KEY_SERVER,
        )
        with self.assertRaises(keyserver.KeyserverError):
            download_key(url_opener=mock.Mock(side_effect=_URLError))
        with self.assertRaises(keyserver.KeyserverKeyNotFoundError):
            download_key(url_opener=mock.Mock(side_effect=HTTPError_404))
        with self.assertRaises(keyserver.KeyserverError):
            download_key(url_opener=mock.Mock(side_effect=HTTPError_401))

    def test_upload_keys(self) -> None:
        # Check that an urllib error of type URLError raises the correct type
        # of error.
        upload_keys = functools.partial(
            keyserver.upload_keys,
            keys_as_ascii_armor=CN_PUB_KEY,
            keyserver=KEY_SERVER,
        )
        with self.assertRaises(keyserver.KeyserverError):
            upload_keys(url_opener=mock.Mock(side_effect=_URLError))


class TestVks(unittest.TestCase):
    keyserver_url = "keyserver.example.org"

    @staticmethod
    def get_mock_url_opener(
        post_response: Optional[Dict[str, Any]] = None
    ) -> mock.Mock:
        mock_response = mock.Mock()
        if post_response is not None:
            mock_response.read.return_value = json.dumps(post_response).encode()
        mock_cm = mock.MagicMock()
        mock_cm.__enter__.return_value = mock_response
        return mock.Mock(return_value=mock_cm)

    def test_vks_get_key_by_fingerprint(self) -> None:
        mock_url_opener = self.get_mock_url_opener()
        for value, query in (
            ("A" * 40,) * 2,
            ("0x" + "A" * 40, "A" * 40),
            ("0" + "A" * 39,) * 2,
        ):
            keyserver.vks_get_key_by_fingerprint(
                self.keyserver_url, value, mock_url_opener
            )
            mock_url_opener.assert_called_once_with(
                f"https://{self.keyserver_url}:443/vks/v1/by-fingerprint/{query}"
            )
            mock_url_opener.reset_mock()
        with self.assertRaises(ValueError):
            keyserver.vks_get_key_by_fingerprint(
                self.keyserver_url, "A", mock_url_opener
            )

    def test_vks_get_key_by_keyid(self) -> None:
        mock_url_opener = self.get_mock_url_opener()
        for value, query in (
            ("A" * 16,) * 2,
            ("0x" + "A" * 16, "A" * 16),
            ("0" + "A" * 15,) * 2,
        ):
            keyserver.vks_get_key_by_keyid(self.keyserver_url, value, mock_url_opener)
            mock_url_opener.assert_called_once_with(
                f"https://{self.keyserver_url}:443/vks/v1/by-keyid/{query}"
            )
            mock_url_opener.reset_mock()
        with self.assertRaises(ValueError):
            keyserver.vks_get_key_by_fingerprint(
                self.keyserver_url, "A", mock_url_opener
            )

    def test_vks_get_key_by_email(self) -> None:
        mock_url_opener = self.get_mock_url_opener()
        keyserver.vks_get_key_by_email(
            self.keyserver_url, "brian@example.org", mock_url_opener
        )
        mock_url_opener.assert_called_once_with(
            f"https://{self.keyserver_url}:443/vks/v1/by-email/brian%40example.org"
        )

    def test_vks_upload_key(self) -> None:
        d = {
            "key_fpr": "<FINGERPRINT>",
            "status": {"address@example.org": "unpublished"},
            "token": "...",
        }
        mock_url_opener = self.get_mock_url_opener(post_response=d)
        key = "key material"
        result = keyserver.vks_upload_key(key, self.keyserver_url, mock_url_opener)
        request = mock_url_opener.call_args[0][0]
        request.full_url = f"https://{self.keyserver_url}:443/vks/v1/upload"
        request.data = b'{"keytext": "' + key.encode() + b'"}'
        request.headers = {"Content-Type": "application/json"}
        expected = deserialize(keyserver.VksUploadResponse)(d)
        self.assertEqual(expected, result)

    def test_vks_request_verify(self) -> None:
        d = {
            "key_fpr": "<FINGERPRINT>",
            "status": {"address@example.org": "pending"},
            "token": "...",
        }
        token = "..."
        emails = ["chuck@example.org", "brian@example.org"]
        mock_url_opener = self.get_mock_url_opener(post_response=d)
        result = keyserver.vks_request_verify(
            token, emails, self.keyserver_url, mock_url_opener
        )
        request = mock_url_opener.call_args[0][0]
        request.full_url = f"https://{self.keyserver_url}:443/vks/v1/request-verify"
        request.data = json.dumps({"token": token, "addresses": emails}).encode()
        request.headers = {"Content-Type": "application/json"}
        expected = deserialize(keyserver.VksUploadResponse)(d)
        self.assertEqual(expected, result)


def to_info(key: gpg.Key) -> gpg.KeyInfo:
    return gpg.KeyInfo(
        uid=key.uids[0],
        fingerprint=key.fingerprint,
        key_algorithm=key.pub_key_algorithm,
        creation_date=key.creation_date,
        expiration_date=key.expiration_date,
        key_length=key.key_length,
    )


@unittest.skipUnless(ENV_KEY_SERVER is not None and ENV_WITH_GPG, "Key Server Tests")
class TestKeyserverIntegration(IntegrationTest):
    def test_send_search(self) -> None:
        if ENV_KEY_SERVER is None:  # To make mypy happy
            return
        self.s.import_file(CN_PUB_KEY)
        self.s.import_file(UMLAUTS_PUB_KEY)
        key_a, key_b = self.s.list_pub_keys()

        self.s.send_keys(key_a.key_id, key_b.key_id, keyserver=ENV_KEY_SERVER)

        keys = keyserver.search_keyserver(
            key_a.uids[0].full_name or "", keyserver=ENV_KEY_SERVER
        )
        self.assertEqual(list(keys), [to_info(key_a)])

        keys = keyserver.search_keyserver(
            key_b.uids[0].full_name or "", keyserver=ENV_KEY_SERVER
        )
        self.assertEqual(list(keys), [to_info(key_b)])

        # By fingerprint
        keys = keyserver.search_keyserver(key_b.fingerprint, keyserver=ENV_KEY_SERVER)
        self.assertEqual(list(keys), [to_info(key_b)])

        # By ID
        keys = keyserver.search_keyserver(key_b.key_id, keyserver=ENV_KEY_SERVER)
        self.assertEqual(list(keys), [to_info(key_b)])

    def test_recv_keys(self) -> None:
        if ENV_KEY_SERVER is None:  # To make mypy happy
            return
        try:
            with tempfile.TemporaryDirectory() as gpg_temp_dir:
                temp_store = gpg.GPGStore(gpg_temp_dir)
                temp_store.import_file(SGT_HARTMANN_PUB_KEY)
                temp_store.import_file(UMLAUTS_PUB_KEY)
                key_a, key_b = temp_store.list_pub_keys(sigs=True)
                self.assertTrue(key_a.signatures or key_b.signatures)
                temp_store.send_keys(
                    key_a.key_id, key_b.key_id, keyserver=ENV_KEY_SERVER
                )
        except FileNotFoundError:
            pass
        self.s.recv_keys(key_a.key_id, key_b.fingerprint, keyserver=ENV_KEY_SERVER)
        keys = set(self.s.list_pub_keys(sigs=True))
        self.assertEqual({key_a, key_b}, keys)
