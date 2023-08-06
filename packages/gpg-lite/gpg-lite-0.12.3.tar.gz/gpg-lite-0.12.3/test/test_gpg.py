import unittest
import os
import tempfile
import io
from functools import partial
from typing import Tuple, Any, cast, IO, Callable

import gpg_lite as gpg
from gpg_lite import keyserver, store
from gpg_lite.cmd import GPGError
from gpg_lite.model import SignatureValidity

ENV_WITH_GPG = os.environ.get("WITH_GPG", None) == "true"

CN_UID = gpg.Uid(full_name="Chuck Norris", email="chuck.norris@roundhouse.gov")
CN_FINGERPRINT = "CB5A3A5C2C4419BB09EFF879D6D229C51AB5D107"
CN_SIGNATURE = gpg.Signature(
    issuer_uid=CN_UID,
    issuer_key_id=CN_FINGERPRINT[-16:],
    issuer_fingerprint=CN_FINGERPRINT,
    creation_date="1550241679",
    signature_class="13x",
    validity=SignatureValidity.good,
)

AUTHORITY_UID = gpg.Uid(
    full_name="Unit Test Authority (validation key)", email="authority@roundhouse.gov"
)
AUTHORITY_FINGERPRINT = "848FA2707A1AC6060FFE5D253A6500D5C1DE39AC"
AUTHORITY_SIGNATURE = gpg.Signature(
    issuer_uid=AUTHORITY_UID,
    issuer_key_id=AUTHORITY_FINGERPRINT[-16:],
    issuer_fingerprint=None,
    creation_date="1571225229",
    signature_class="13x",
    validity=SignatureValidity.good,
)
AUTHORITY_SIGNATURE_REVOKED_FAKE = gpg.RevocationSignature(
    issuer_uid=AUTHORITY_UID,
    issuer_key_id=AUTHORITY_FINGERPRINT[-16:],
    issuer_fingerprint=None,
    creation_date="1571225230",
    signature_class="30x",
    validity=SignatureValidity.bad,
    reason="00",
    comment="revsig\\nFake revocation",
)

SGT_HARTMANN_UID = gpg.Uid(
    full_name="Gunnery Sgt. Hartmann", email="hartmann@bullshit.gov"
)
SGT_HARTMANN_FINGERPRINT = "DA1A363BC5E11DA73806A8A4E3E4024A0E56221E"
SGT_HARTMANN_SIGNATURE = gpg.Signature(
    issuer_uid=SGT_HARTMANN_UID,
    issuer_key_id=SGT_HARTMANN_FINGERPRINT[-16:],
    issuer_fingerprint=SGT_HARTMANN_FINGERPRINT,
    creation_date="1571232229",
    signature_class="12x",
    validity=SignatureValidity.good,
)
SGT_HARTMANN_SIGNATURE_REVOKED = gpg.RevocationSignature(
    issuer_uid=SGT_HARTMANN_UID,
    issuer_key_id=SGT_HARTMANN_FINGERPRINT[-16:],
    issuer_fingerprint=SGT_HARTMANN_FINGERPRINT,
    creation_date="1571252229",
    signature_class="30x",
    validity=SignatureValidity.good,
    reason="00",
    comment="revsig\\nInvalid email",
)

UMLAUTS_UID = gpg.Uid(full_name="With Umläuts", email="with.umlauts@umlauts.info")
UMLAUTS_FINGERPRINT = "F119E26211119BB09EFF879D6D229C51AB5D107C"
MISSING_PUB_KEY_SIGNATURE = gpg.Signature(
    issuer_uid=None,
    issuer_key_id="2E3E7FE28FE412AE",
    issuer_fingerprint="2866A142A16F54E06EB73CF92E3E7FE28FE412AE",
    creation_date="1573661452",
    signature_class="13x",
    validity=SignatureValidity.no_public_key,
)

KEY_SERVER = "http://hagrid.hogwarts.org:11371"

CN_KEY_PAYLOAD = b"""pub:u:2048:1:D6D229C51AB5D107:1550241679:::u:::scESC::::::23:1571230031:1 http\\x3a//hagrid.hogwarts.org\\x3a11371:
fpr:::::::::CB5A3A5C2C4419BB09EFF879D6D229C51AB5D107:
uid:u::::1550241679::B1E8D4565D26BED47D1EB8BB2B5733AEC1F154B5::Chuck Norris <chuck.norris@roundhouse.gov>::::::::::0:
sig:!::1:D6D229C51AB5D107:1550241679::::Chuck Norris <chuck.norris@roundhouse.gov>:13x::CB5A3A5C2C4419BB09EFF879D6D229C51AB5D107:::8:
sig:!::1:3A6500D5C1DE39AC:1571225229::::Unit Test Authority (validation key) <authority@roundhouse.gov>:13x:::::2:
sig:?::1:2E3E7FE28FE412AE:1573661452::::[User ID not found]:13x::2866A142A16F54E06EB73CF92E3E7FE28FE412AE:::8:
sig:!::1:E3E4024A0E56221E:1571232229::::Gunnery Sgt. Hartmann <hartmann@bullshit.gov>:12x::DA1A363BC5E11DA73806A8A4E3E4024A0E56221E:::10:
rev:!::1:E3E4024A0E56221E:1571252229::::Gunnery Sgt. Hartmann <hartmann@bullshit.gov>:30x,00::DA1A363BC5E11DA73806A8A4E3E4024A0E56221E:::8:::::revsig\\nInvalid email:
rev:-::1:3A6500D5C1DE39AC:1571225230::::Unit Test Authority (validation key) <authority@roundhouse.gov>:30x,00:::::2:::::revsig\\nFake revocation
sub:u:2048:1:D892C41917B20115:1550241679::::::e::::::23:
fpr:::::::::55C5314BB9EFD19AE7CC4774D892C41917B20115:
sig:!::1:D6D229C51AB5D107:1550241679::::Chuck Norris <chuck.norris@roundhouse.gov>:13x::CB5A3A5C2C4419BB09EFF879D6D229C51AB5D107:::8:
"""
CN_KEY = gpg.Key(
    key_id=CN_FINGERPRINT[-16:],
    fingerprint=CN_FINGERPRINT,
    validity=gpg.Validity.ultimately_valid,
    key_length=2048,
    pub_key_algorithm=1,
    creation_date="1550241679",
    signatures=(
        CN_SIGNATURE,
        AUTHORITY_SIGNATURE,
        MISSING_PUB_KEY_SIGNATURE,
        SGT_HARTMANN_SIGNATURE,
        SGT_HARTMANN_SIGNATURE_REVOKED,
        AUTHORITY_SIGNATURE_REVOKED_FAKE,
    ),
    key_capabilities={
        gpg.KeyCapability.sign,
        gpg.KeyCapability.certify,
    },
    combined_key_capabilities={
        gpg.KeyCapability.sign,
        gpg.KeyCapability.certify,
        gpg.KeyCapability.encrypt,
    },
    disabled=False,
    key_type=gpg.KeyType.public,
    uids=(CN_UID,),
    owner_trust="u",
    sub_keys=(
        gpg.SubKey(
            key_type=gpg.KeyType.public,
            key_id="D892C41917B20115",
            fingerprint="55C5314BB9EFD19AE7CC4774D892C41917B20115",
            validity=gpg.Validity.ultimately_valid,
            key_length=2048,
            pub_key_algorithm=1,
            creation_date="1550241679",
            signatures=(CN_SIGNATURE,),
            key_capabilities={gpg.KeyCapability.encrypt},
        ),
    ),
    origin=KEY_SERVER,
)

AUTHORITY_KEY_PAYLOAD = b"""pub:-:4096:1:3A6500D5C1DE39AC:1565257866:::-:::scESC::::::23::0:
fpr:::::::::848FA2707A1AC6060FFE5D253A6500D5C1DE39AC:
uid:-::::1565257866::4D51176EBCDF1F58C3D7E0F76625B168A184BB8E::Unit Test Authority (validation key) <authority@roundhouse.gov>::::::::::0:
sig:!::1:3A6500D5C1DE39AC:1571225229::::Unit Test Authority (validation key) <authority@roundhouse.gov>:13x:::::2:
sub:-:4096:1:A4C037FA518B5C4F:1565257866::::::e::::::23:
fpr:::::::::3AC9B4462D255449989A3D6EA4C037FA518B5C4F:
sig:!::1:3A6500D5C1DE39AC:1571225229::::Unit Test Authority (validation key) <authority@roundhouse.gov>:13x:::::2:
"""
AUTHORITY_KEY = gpg.Key(
    key_id=AUTHORITY_FINGERPRINT[-16:],
    fingerprint=AUTHORITY_FINGERPRINT,
    validity=gpg.Validity.unknown,
    key_length=4096,
    pub_key_algorithm=1,
    creation_date="1565257866",
    signatures=(AUTHORITY_SIGNATURE,),
    key_capabilities={
        gpg.KeyCapability.sign,
        gpg.KeyCapability.certify,
    },
    combined_key_capabilities={
        gpg.KeyCapability.sign,
        gpg.KeyCapability.certify,
        gpg.KeyCapability.encrypt,
    },
    disabled=False,
    key_type=gpg.KeyType.public,
    uids=(AUTHORITY_UID,),
    owner_trust="-",
    sub_keys=(
        gpg.SubKey(
            key_type=gpg.KeyType.public,
            key_id="A4C037FA518B5C4F",
            fingerprint="3AC9B4462D255449989A3D6EA4C037FA518B5C4F",
            validity=gpg.Validity.unknown,
            key_length=4096,
            pub_key_algorithm=1,
            creation_date="1565257866",
            signatures=(AUTHORITY_SIGNATURE,),
            key_capabilities={gpg.KeyCapability.encrypt},
        ),
    ),
    origin=None,
)


class TestUtils(unittest.TestCase):
    def test_split_url(self) -> None:
        self.assertEqual(
            keyserver.split_host("http://hagrid.hogwarts.org:11371"),
            ("http://", "hagrid.hogwarts.org", ":11371"),
        )
        self.assertEqual(
            keyserver.split_host("hkp://hagrid.hogwarts.org:11371"),
            ("hkp://", "hagrid.hogwarts.org", ":11371"),
        )
        self.assertEqual(
            keyserver.split_host("hagrid.hogwarts.org:11371"),
            (None, "hagrid.hogwarts.org", ":11371"),
        )
        self.assertEqual(
            keyserver.split_host("http://hagrid.hogwarts.org"),
            ("http://", "hagrid.hogwarts.org", None),
        )
        self.assertEqual(
            keyserver.split_host("hagrid.hogwarts.org"),
            (None, "hagrid.hogwarts.org", None),
        )
        with self.assertRaises(ValueError):
            keyserver.split_host("hagrid.hogwar:ts.org")

    def test_uid_missging_both_fields(self) -> None:
        with self.assertRaises(ValueError):
            gpg.Uid(full_name=None, email=None)

    def test_uid_from_str(self) -> None:
        self.assertEqual(gpg.Uid.from_str("[User ID not found]"), None)
        self.assertEqual(gpg.Uid.from_str("[User-ID nicht gefunden]"), None)
        self.assertEqual(gpg.Uid.from_str("[Identité introuvable]"), None)
        self.assertEqual(
            gpg.Uid.from_str("Chuck Norris <chucknorris@roundhouse.gov>"),
            gpg.Uid(full_name="Chuck Norris", email="chucknorris@roundhouse.gov"),
        )
        self.assertEqual(
            gpg.Uid.from_str(
                "Chuck Norris (Chucks's test PGP key) <chucknorris@roundhouse.gov>"
            ),
            gpg.Uid(
                full_name="Chuck Norris (Chucks's test PGP key)",
                email="chucknorris@roundhouse.gov",
            ),
        )
        self.assertEqual(
            gpg.Uid.from_str("Chuck Norris"),
            gpg.Uid(full_name="Chuck Norris", email=None),
        )
        self.assertEqual(
            gpg.Uid.from_str("chucknorris@roundhouse.gov"),
            gpg.Uid(full_name=None, email="chucknorris@roundhouse.gov"),
        )

    def test_uid_repr(self) -> None:
        cases = (
            (
                "Chuck Norris (Chucks's test PGP key)",
                "chucknorris@roundhouse.gov",
                "Chuck Norris (Chucks's test PGP key) <chucknorris@roundhouse.gov>",
            ),
            (
                "Chuck Norris",
                "chucknorris@roundhouse.gov",
                "Chuck Norris <chucknorris@roundhouse.gov>",
            ),
            ("Chuck Norris", None, "Chuck Norris"),
            (None, "chucknorris@roundhouse.gov", "chucknorris@roundhouse.gov"),
        )
        for name, email, expected in cases:
            self.assertEqual(repr(gpg.Uid(full_name=name, email=email)), expected)


class TestGPG(unittest.TestCase):
    def test_parse_keys(self) -> None:
        # Verify parsing of GnuPG output for single and multiple key(s).
        for keys, payload in (
            ([CN_KEY], CN_KEY_PAYLOAD),
            ([AUTHORITY_KEY], AUTHORITY_KEY_PAYLOAD),
            ([CN_KEY, AUTHORITY_KEY], CN_KEY_PAYLOAD + AUTHORITY_KEY_PAYLOAD),
        ):
            parsed_keys = store.parse_keys(
                io.BytesIO(b"tru::1:1571400791:0:3:1:5\n" + payload)
            )
            self.assertEqual(parsed_keys, keys)

    def test_parse_keys_revocation_sig(self) -> None:
        (parsed_key,) = store.parse_keys(
            io.BytesIO(b"tru::1:1571400791:0:3:1:5\n" + CN_KEY_PAYLOAD)
        )
        self.assertEqual(parsed_key, CN_KEY)

        # Verify that valid signatures are detected correctly. The following
        # signatures are invalid and should not be listed:
        #  * MISSING_PUB_KEY_SIGNATURE: signature that could not be verified
        #       because of missing public key in the user's keyring.
        #  * SGT_HARTMANN_SIGNATURE: revoked by SGT_HARTMANN_SIGNATURE_REVOKED
        #  * AUTHORITY_SIGNATURE_REVOKED_FAKE: this does actually not
        #       revoke AUTHORITY_SIGNATURE because the revocation signature
        #       is invalid. Therefore AUTHORITY_SIGNATURE must still be listed
        #       as a valid key.
        self.assertEqual(
            parsed_key.valid_signatures, [CN_SIGNATURE, AUTHORITY_SIGNATURE]
        )

    def test_extract_key_id(self) -> None:
        partial_msg = io.BytesIO(b"\x84\x8c\x03\xf3\rL3@z?c\x01\x03\xff]\xdf")
        pos = partial_msg.tell()
        (key_id,) = gpg.extract_key_id(partial_msg)
        self.assertEqual(key_id, "F30D4C33407A3F63")
        self.assertEqual(partial_msg.tell(), pos)

        wrong_msg = io.BytesIO(b"\x04\x8c\x03\xf3\rL3@z?c\x01\x03\xff]\xdf")
        with self.assertRaises(gpg.GPGError):
            list(gpg.extract_key_id(wrong_msg))

        partial_msg = io.BytesIO(
            b"\x85\x01\x0c\x03\xd8\x92\xc4\x19\x17\xb2\x01\x15\x01\x08"
            b"\x00\xafZ\xd8\x83\xba"
            + 248 * b"\000"
            + b"c\x1d\x16\x85\x02\x0c\x032\xf9\xe2\xf8\rR!^\x01\x10\x00\x97c"
            + 504 * b"\000"
            + b"\x1a\xa2\xf2&\xc0\xe5\x85\x02\x0c\x03\xcc\xfa\xa7\xf4\x12\xb0m"
            b"\x83\x01\x10"
        )

        key_ids = list(gpg.extract_key_id(partial_msg))
        self.assertEqual(
            key_ids, ["D892C41917B20115", "32F9E2F80D52215E", "CCFAA7F412B06D83"]
        )

    def test_extract_key_id_ascii_armored(self) -> None:
        partial_msg = io.BytesIO(b"-----BEGIN PGP MESSAGE-----\r\n\r\n")
        with self.assertRaises(gpg.GPGError) as cm:
            list(gpg.extract_key_id(partial_msg))
        self.assertEqual(
            format(cm.exception), "ASCII armored encrypted data is not supported"
        )

    def test_extract_key_id_from_sig(self) -> None:
        sig = (
            b"\x89\x023\x04\x00\x01\x08\x00\x1d\x16!\x04\xa8\x05h*\x13\xa1\x08\xca"
            b"\xab\x07\xef\xd0k\xe5(\xb1&\xd3\xe13\x05\x02_\x05\xcfP\x00\n\t\x10k"
            b"\xe5(\xb1&\xd3\xe13\xf8\x8a\x10\x00\x97\xb8\x0bWU\x05B\xd5\x17\xba\xd2"
            b"\x9b\xe4o\xd4`\x86Id\x86\xc4m\xa6=\xf2\xf3\xc5\xec\x8b\x16?Q\xfe\x06"
            b"\xf9\xdc`\xfa\xe4\x9d~)\xcaYx\x16\x06t@\xc0\xc0\xe4\xd5\x94\x1a\x19"
            b"\xa5yL.r\xba\x01-\xe8\xc6\xaf \xa8\xc9\xbef\x0b:C\xa4\x83Ahn\x85R\xbe"
            b"\x81\x02\xb14\xce\x89\xef4\xa4\xb5\x96\xcc\x81t/x\x16_\xb1|\xcbb+3"
            b"\xf4`w_\x93\x8cl\xa0\x95$<&\x8fu<\n\xd1-9^\\\x98\x04\xa0F\x9fE\xeb{"
            b"\xc4\xda\x9f\x9f\xf0\xc9#>\xba\xb5\xa8\x99Od\xcdb\x9en\xa0\xb2\x1c\xd2"
            b"\xe8\xa8\x03k\x04o\xd5\x08\xb7W\x19UL\xa4\x14P\xba\x10}XS\x18\x86M"
            b"\xa3k\xdc\x0fO&\xe6J-\xca\x13\xac\xe8\xacb\xc5\x81x\xe3\xf0\x0b\xe1["
            b"\x1f\xc7\xd1b\x89\xb7\xe3E\x06\xa7n\x83\xe8\xc0.\x96\xd8\x19\x9d\xc3J"
            b"\xfcR\xc1%\x960\x95Y\n\x98`\xb1C(KAwO\xf6\xf5\xe1\xdcCk\x96j\xbbC\xd3?"
            b"\x05\x07r\xc1#\x97\x1d\x15~L\xb8HQ\xb4|=\x8dG\x987wN\xc8\xbfm\x889\xd5"
            b"\x9c\xfd\x90@#C\xef\xcf\x12\r\xc1\xdd\x1e\xd2\xc3\x97[\xad\xcc\x86\xbc"
            b"\xa2\xc6R\xce\xf6L\x8f5;\xe0\xc4|\xe2\xeb\xfe\xe5\xb0\xa2F\xc2\x8eX"
            b"\xab \xe7\xe3\xf3\xe9SN\x16K\x99\xb9S}\xa7\x02\xaa\xd6\x9c\xb3\xb8"
            b"\xcelO\xd3!/2r|\x06\x10\x88$L\x99\x15 \xff\xa7\x812\xb6\xf6I\xba\x10"
            b"\xfd\x94\xb6\x05:`*\xa3\xd0\xfb\xf8~\x0f\xedPx\t\x1fq\xe0\x8e\xf0\xcb"
            b"\xf1\xab\xa0yF\xc7iL\xba\xb7e\xfa\xba\xfb\x8e\xe5w\x8bF\xd3\x91\xc7G4"
            b"\x9c]\xcc\xb8\x10\x0c\xdc\x81\xc0_\x1e\x83c=x2\xd6\xa9:s\xc5\xf0\x04#"
            b"\x0c`\xa2\x0c\x95&\x08\xf5:\x12\xe0\x8a\xb6\x86\x9dE\xea\xa9\xd6\xff"
            b"\xe9~\x91_|\x14.\xcb\x14\xdd\xb9\tR\x1a)\x04\xaf\xf6\xb7\xd4(&%\xc4"
            b"\xe9\xea\xac\x00\x17\xe3Nf\xd6\xd1\xa0\xb9\x99\xe3[\xa1O?a\xd7\x06\x9fc"
        )
        key_id = gpg.extract_key_id_from_sig(sig)
        self.assertEqual(key_id, "A805682A13A108CAAB07EFD06BE528B126D3E133")
        sig = b"""-----BEGIN PGP SIGNATURE-----

iQIzBAABCAAdFiEEqAVoKhOhCMqrB+/Qa+UosSbT4TMFAl8YCiwACgkQa+UosSbT
4TMEvQ/5AaSlYmpQK1MWQbNHiL4AMl55GfVlSnQBCpk3lsltOnycEVxP67jawpd7
2DSFBzcF5wRUiMo85R9YkNxBjFwfU2xlT738ZWFQIoOvvwyGJgOlgngZ7+BEGEqP
130pEIGeDVt6kzVuwqB09SZCATGR0qnkB/84+pFimN0tiFkFWHXLHgJ++uMO2Pg+
j45HbZzYh0qqKfY+X9lP5JIuCsnFQv5AOgnUFfy1vKNZd6OGCZuxCla5M+RpOcFD
F3w004RK2p3SNS7ikoATRSDnSHwiWDay8WesmVkOXQurevEONGdvUY91ZW41wA5T
HR3qHWZyg4fWy4G2azCbGA3AEnd2m+sWdvptpbL7InxutLET5hLEXNsnL1Ixiqr/
DViv+hBaixAT0LRCdci3G/FfWAC38zZjo/A6JLpCGaqTuWl1OWkDPxQXPNYT4Wgk
Y9YJFrgF1MQ2BrUuYzrC+ClEvO/TBsVe2r9l4ElZs3rZBH1vOxyCyuAHreNw46R6
MfwW9lYob56DUTRBVrhZI46/LQD/dlwtYedN5p/CNpzavuzQHAmJD1G22WZHwTqV
SL/bsOqwOqJP1BpQloAR+jEnP6jPbQAmPEn3xU+3IPWjKFe95QUj3PIeeSqst2Mt
xERXJ/PqFoAktjU/mhNeDHovXdB+7378YkY3NHNSlFytYG0D5jo=
=qg97
-----END PGP SIGNATURE-----
"""
        key_id = gpg.extract_key_id_from_sig(sig)
        self.assertEqual(key_id, "A805682A13A108CAAB07EFD06BE528B126D3E133")
        key_id = gpg.extract_key_id_from_sig(sig.replace(b"\n", b"\r\n"))
        self.assertEqual(key_id, "A805682A13A108CAAB07EFD06BE528B126D3E133")

        # Signature generated with gpg 2.0.22
        sig = (
            b"\x89\x02\x1c\x04\x00\x01\x02\x00\x06\x05\x02a`,\xa6\x00\n\t\x10\xab"
            b"\xd0chZI\x86\x83\xa2\xeb\x10\x00\x8e\xe6\x15\x0e\x9cf\xd6t\x07"
            b"?f\x81\x100\x88\xa7\x94\x18\xf1j\x9c\xcc]\xb1D\x13\xd3A?"
            b"\xb5(c\x85\xa9\xd86\xdc\x1fm\x99\xbb:D\x8b\x08D/\x85\xea"
            b"\xe5\x17\xc5'\xca_8\x94\x00\x07\xb3\x96\xe6dJ\x0e\xed\xb7F,"
            b"/\xaa\xb5\xaeB\x99\x17\xeb\xc9\xf4\xf1\xa5\xb0\x03\xe2l\x08\xf7\x8d\xfe"
            b" \xee\x04x\xe7h\xbdv<\x98\x8d=\x84\xa6\xc8q\xd0wVJ"
            b'\x1c\x83\x85\xf4o\xd0$ \xa543\xcd\xe5\x05\xc9\x10\xac\x8f"F'
            b"\x1b\xfd\xa6<dKT\xd2\x13\x9e\xe1\x9bd\xc6Q\xb0n\xd2`Z"
            b"\xda\x11\xdd\xe2\x95\xb6uY\xff\x8bA\xb1\xdd.\x0f|\xb1\x9d<c"
            b"\xd0\x1f\xf3\x9f\xcdI\xb4\xb7\x05\xba\x0f\xc5\x1d\x9e\x0b\xeaT\xc76\xaa"
            b"\x05f\xe3\xbe\xf2\xd6U\xc9sE?\xf9\xbd\xb2p0n\x9a@\xec"
            b".\x9c'\xdb\x86{\x96?\x13|W\xbew[G\x94<\xc0\x8d\""
            b"N\xe1C2\xed=\r\x8b\xb9]b\xb7q\xc6\xba\x8ev/8\xa1"
            b"\xf6\xef\xc5J\xdb\xd7\xd2v\xeb\xbf\xd7\x18\x89\x95\xe3=`\xbf\x0c\xa8"
            b"\xb4\xab\x0c\xcb\x07\xe2\xcc\xfa\xed\xe4MI\xec\x08\x94\n\x92\xd7\xfc\xbb"
            b'\xc4\x18Gf\x9c{v\xbc\xb2"\xaaa.\xab\x03\xbb\xf3@\xcbg'
            b"\xb5m\xe1\r`\xa8/\x98\xa6\x843\xd1\x80\xc3\xcdj\x9b6\x8c4"
            b"G\xfc\xfe\x807S*\xf9Ts\xd2^\xb9\xa1\xe5(]V\xbf$"
            b"\xf0\x89\xb3\xbaX\xcdL-\xa0\xca\xdc\tZA\x8e\xad).Q\xf2"
            b"*\xc2t\x93\x8f\xff\xd6\xce\xddq\x14\xe1+gJ(V\xdd7\xd3"
            b"\xed\x01\xcd\x9d\xbdPq\x87\x88\xb3\xc1\x8e\xed\xdc\x9bl\x0e\xb5\xbfI"
            b"\x8c\x0b\xc2\x9cF\xbeib\x9av\xee~\xe59OvJ\xdc+0"
            b"N\xd4\xd6\x0f,V\xda\xb9\x0b\xc0J\xfd\xb7l\xd1<\xd2\x0c\xd5\xba"
            b"|9\xe0\x1fj19\xbc3\x93\x92t%\x10/<\xfc'\xa7\xe7"
            b"\xf0\x8d\xad\x0c\xab\x9f`.\xdf@K\xef\xf2A\xca]+'\x9f\xab"
            b"\xc7\xcd\xd9\x0b\xb4\x87:<\xef\x9a\xa4\x97XEvDi\x1a\x1a!"
            b"\xf1\xa0\xf2"
        )
        key_id = gpg.extract_key_id_from_sig(sig)
        self.assertEqual(key_id, "ABD063685A498683")

    def test_capture_fpr(self) -> None:
        b = b"""
[GNUPG:] NEWSIG
gpg: Signature made Tue 10 Mar 2020 11:29:27 CET
gpg:                using RSA key AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
[GNUPG:] KEY_CONSIDERED AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0
[GNUPG:] SIG_ID PaAuiNMUyUDRMsctXpV+7rX+0CI 2020-03-10 1583836167
[GNUPG:] KEY_CONSIDERED AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0
[GNUPG:] GOODSIG 066E042415D8FD9C Chuck Norris <chucknorris@roundhouse.gov>
gpg: Good signature from "Chuck Norris <chucknorris@roundhouse.gov>" [undefined]
[GNUPG:] VALIDSIG AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 2020-03-10 1583836167 0 4 0 1 8 00 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
[GNUPG:] TRUST_UNDEFINED 0 pgp
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
"""
        self.assertEqual(
            store.capture_fpr(b), ["AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"]
        )
        b = b"""
gpg: Signature made Mi 12 Feb 2020 15:34:46 CET
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
"""
        self.assertEqual(store.capture_fpr(b), [])
        b = b"""
[GNUPG:] NEWSIG
gpg: Signature made Tue 10 Mar 2020 11:29:27 CET
gpg:                using RSA key AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
[GNUPG:] KEY_CONSIDERED AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0
[GNUPG:] SIG_ID PaAuiNMUyUDRMsctXpV+7rX+0CI 2020-03-10 1583836167
[GNUPG:] KEY_CONSIDERED AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0
[GNUPG:] GOODSIG 066E042415D8FD9C Chuck Norris <chucknorris@roundhouse.gov>
gpg: Good signature from "Chuck Norris <chucknorris@roundhouse.gov>" [undefined]
[GNUPG:] VALIDSIG AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 2020-03-10 1583836167 0 4 0 1 8 00 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
[GNUPG:] TRUST_UNDEFINED 0 pgp
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
[GNUPG:] NEWSIG
gpg: Signature made Tue 10 Mar 2020 11:29:27 CET
gpg:                using RSA key BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
[GNUPG:] KEY_CONSIDERED BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB 0
[GNUPG:] SIG_ID PaAuiNMUyUDRMsctXpV+7rX+0CI 2020-03-10 1583836167
[GNUPG:] KEY_CONSIDERED BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB 0
[GNUPG:] GOODSIG 066E042415D8FD9C Gunnery Sgt. Hartmann <hartmann@bullshit.gov>
gpg: Good signature from "Gunnery Sgt. Hartmann <hartmann@bullshit.gov" [undefined]
[GNUPG:] VALIDSIG BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB 2020-03-10 1583836167 0 4 0 1 8 00 BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
[GNUPG:] TRUST_UNDEFINED 0 pgp
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
"""
        self.assertEqual(
            store.capture_fpr(b),
            [
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
            ],
        )

    def test_assert_mdc(self) -> None:
        b = b"""
[GNUPG:] ENC_TO AAAAAAAAAAAAA 1 0
[GNUPG:] KEY_CONSIDERED AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0
[GNUPG:] KEY_CONSIDERED AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0
[GNUPG:] DECRYPTION_KEY BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA u
[GNUPG:] KEY_CONSIDERED AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0
gpg: encrypted with 4096-bit RSA key, ID AAAAAAAAAAAAA, created 2019-02-18
      "Chuck Norris <chucknorris@roundhouse.gov>"
[GNUPG:] BEGIN_DECRYPTION
[GNUPG:] DECRYPTION_COMPLIANCE_MODE 23
[GNUPG:] DECRYPTION_INFO 2 9
[GNUPG:] PLAINTEXT 62 1628663575 test.txt
[GNUPG:] PLAINTEXT_LENGTH 14
[GNUPG:] NEWSIG
gpg: Signature made Wed 11 Aug 2021 08:32:55 CEST
gpg:                using RSA key AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
[GNUPG:] KEY_CONSIDERED AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0
[GNUPG:] SIG_ID txTzNz6Yi2We04M0MWGw3pDp73w 2021-08-11 1628663575
[GNUPG:] KEY_CONSIDERED AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0
[GNUPG:] GOODSIG 066E042415D8FD9C Chuck Norris <chucknorris@roundhouse.gov>
gpg: Good signature from "Chuck Norris <chucknorris@roundhouse.gov>" [ultimate]
[GNUPG:] VALIDSIG AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 2021-08-11 1628663575 0 4 0 1 10 00 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
[GNUPG:] KEY_CONSIDERED AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 0
[GNUPG:] TRUST_ULTIMATE 0 pgp
[GNUPG:] VERIFICATION_COMPLIANCE_MODE 23
[GNUPG:] DECRYPTION_OKAY
[GNUPG:] GOODMDC
[GNUPG:] END_DECRYPTION
"""
        store.assert_mdc(b)

        with self.assertRaises(GPGError) as cm:
            store.assert_mdc(
                b.replace(
                    b"[GNUPG:] DECRYPTION_OKAY\n[GNUPG:] GOODMDC",
                    b"gpg: WARNING: message was not integrity protected\n"
                    b"gpg: decryption forced to fail!\n[GNUPG:] DECRYPTION_FAILED",
                )
            )
        self.assertEqual(str(cm.exception), "Message integrity could not be verified.")


class IntegrationTest(unittest.TestCase):
    def _setup_key(self) -> gpg.Key:
        self.s.import_file(CN_SEC_KEY, passphrase="test")
        self.s.import_file(CN_PUB_KEY)
        (key,) = self.s.list_sec_keys()
        return key

    def setUp(self) -> None:
        # pylint: disable=consider-using-with
        gpg_homedir = tempfile.TemporaryDirectory()
        self.gpg_homedir = gpg_homedir
        # pylint: disable=unnecessary-dunder-call
        d = gpg_homedir.__enter__()
        self.s = gpg.GPGStore(d)

    def tearDown(self) -> None:
        try:
            self.gpg_homedir.__exit__(None, None, None)
        except FileNotFoundError:
            pass


@unittest.skipUnless(ENV_WITH_GPG, "Integration tests")
class TestGPGIntegration(IntegrationTest):
    def test_revoke_key(self) -> None:
        if self.s._version < (2, 2, 0):  # pylint: disable=protected-access
            self.skipTest("Key revocation not supported for gnupg < 2.2.0")
        key = self._setup_key()
        self.assertTrue(key.validity != gpg.Validity.revoked)
        self.s.revoke_key(key.fingerprint, passphrase="test")
        (key,) = self.s.list_sec_keys()
        self.assertEqual(key.validity, gpg.Validity.revoked)

    def test_export_secret(self) -> None:
        key = self._setup_key()
        # no matching key for the given fingerprint
        with self.assertRaises(GPGError) as cm:
            self.s.export_secret("A" * 40, passphrase="test")
        self.assertIn("not found", str(cm.exception))
        # check if an ascii-armored key is returned
        exported = self.s.export_secret(key.fingerprint, passphrase="test", armor=True)
        self.assertTrue(exported.startswith(b"-----BEGIN PGP PRIVATE KEY BLOCK-----"))
        self.assertTrue(exported.endswith(b"-----END PGP PRIVATE KEY BLOCK-----\n"))
        # load the exported key and compare it with the original one
        with tempfile.TemporaryDirectory() as tmp:
            s = gpg.GPGStore(tmp)
            s.import_file(exported, passphrase="test")
            (imported_key,) = s.list_sec_keys()
            self.assertEqual(imported_key, key)

    def test_list_keys(self) -> None:
        self._setup_key()
        self.s.import_file(UMLAUTS_PUB_KEY)

        def extract_keys(**kwargs: Any) -> Tuple[gpg.Key, gpg.Key]:
            keys = self.s.list_pub_keys(**kwargs)
            if keys[0].uids == (CN_UID,):
                key_1, key_2 = keys
            else:
                key_2, key_1 = keys
            return key_1, key_2

        pub_key, umlauts_key = extract_keys()

        self.assertEqual(pub_key.uids, (CN_UID,))
        self.assertEqual(pub_key.key_type, gpg.KeyType.public)
        self.assertFalse(pub_key.signatures)
        self.assertEqual(umlauts_key.uids, (UMLAUTS_UID,))
        self.assertEqual(umlauts_key.key_type, gpg.KeyType.public)
        self.assertFalse(umlauts_key.signatures)

        pub_key, umlauts_key = extract_keys(sigs=True)
        self.assertEqual(pub_key.uids, (CN_UID,))
        self.assertEqual(pub_key.key_type, gpg.KeyType.public)
        self.assertTrue(pub_key.signatures)
        self.assertEqual(umlauts_key.uids, (UMLAUTS_UID,))
        self.assertEqual(umlauts_key.key_type, gpg.KeyType.public)
        self.assertTrue(umlauts_key.signatures)

        keys = self.s.list_pub_keys(search_terms=(pub_key.fingerprint,), sigs=True)
        self.assertEqual(keys, [pub_key])

        (sec_key,) = self.s.list_sec_keys()
        self.assertEqual(sec_key.uids, (CN_UID,))
        self.assertEqual(sec_key.key_type, gpg.KeyType.secret)

        keys = self.s.list_pub_keys(search_terms=(), sigs=True)
        self.assertEqual(keys, [])

    def test_gen_key(self) -> None:
        self.s.gen_key(
            full_name=cast(str, CN_UID.full_name),
            email=cast(str, CN_UID.email),
            passphrase="test",
            key_length=1024,
        )
        (pub_key,) = self.s.list_pub_keys()
        self.assertEqual(pub_key.uids, (CN_UID,))
        self.assertEqual(pub_key.key_length, 1024)
        self.assertEqual(pub_key.key_type, gpg.KeyType.public)
        (sec_key,) = self.s.list_sec_keys()
        self.assertEqual(sec_key.uids, (CN_UID,))
        self.assertEqual(sec_key.key_length, 1024)
        self.assertEqual(sec_key.key_type, gpg.KeyType.secret)

    def test_gen_key_unprotected_ecc(self) -> None:
        if self.s._version < (2, 2, 0):  # pylint: disable=protected-access
            self.skipTest("ECC keys not supported for gnupg < 2.2.0")
        self.s.gen_key(
            full_name=cast(str, CN_UID.full_name),
            email=cast(str, CN_UID.email),
            passphrase=None,
            key_length=1024,
            key_type="eddsa",
            subkey_type="ecdh",
            key_curve="Ed25519",
            subkey_curve="Curve25519",
        )
        # key length does not seem to be respected by ECC keys
        (pub_key,) = self.s.list_pub_keys()
        self.assertEqual(pub_key.uids, (CN_UID,))
        self.assertEqual(pub_key.key_type, gpg.KeyType.public)
        (sec_key,) = self.s.list_sec_keys()
        self.assertEqual(sec_key.uids, (CN_UID,))
        self.assertEqual(sec_key.key_type, gpg.KeyType.secret)

    def test_decrypt(self) -> None:
        message = b"a"
        self.s.import_file(CN_SEC_KEY, passphrase="test")
        decrypted = io.BytesIO()

        def capture_output(stream: IO[bytes]) -> None:
            decrypted.write(stream.read())
            decrypted.seek(0)

        with self.assertRaises(BaseException):
            self.s.decrypt(
                source=io.BytesIO(ENCRYPTED_MESSAGE),
                output=capture_output,
                passphrase="wrongpass",
            )
        self.s.decrypt(
            source=io.BytesIO(ENCRYPTED_MESSAGE),
            output=capture_output,
            passphrase="test",
        )
        self.assertEqual(decrypted.read(), message)

        with self.subTest("Missing MDC"):
            decrypted.seek(0)
            decrypted.truncate()
            encrypted_msg_without_mdc = (
                b"\x84\x8c\x03\xf3\rL3@z?c\x01\x03\xfe=\x97\x01kJP"
                b"\x90H\x06\x9a\xa2\x17!\xa8\xf9$n\xcf/\xad\xcb\xac\xc3;Y\xe9"
                b"\xebw\x0c7^Z<\xces{\xfe\x9a*`\xcf\x01\x9d\xbcZ\r"
                b"\xf4\x1ae0a3\x97 p\xc8\x9afa\xbd\x93\xea\xa3\xa4\xb9{"
                b'\x18"\x10%\x9cZ\xea\xa8,,\xd7zt\xcf\xe3\xce.4\xe16'
                b"\x01\xd0'\xab\x050<3\xc3xA\x13\xf3\x83\x83\xa2}\xc3X\xc5"
                b"\xb1vE\xdeV\xd5of\x8c\xd1*\x04\xa03\xb6\xa5\xc0\xaf\x14~"
                b"\xa3\x8c\xc9&\x18\xc5\xf4\xb8\x04\x99\x8a\t\x82f\xc2\xe1\xaf\xad\x85D"
                b"\xf0\xfe2\xc5\x865\xb8m\xa3R\xd0\xfa\x13\xba*\x85\x0c\x9f\xbdS"
                b"!\xbf"
            )
            with self.assertRaises(GPGError) as cm:
                self.s.decrypt(
                    source=io.BytesIO(encrypted_msg_without_mdc),
                    output=capture_output,
                    passphrase="test",
                )
            self.assertEqual(
                str(cm.exception), "Message integrity could not be verified."
            )

    def test_encrypt_decrypt(self) -> None:
        key = self._setup_key()
        message = b"a"
        decrypted = io.BytesIO()

        def capture_output(stream: IO[bytes]) -> None:
            decrypted.write(stream.read())
            decrypted.seek(0)

        decrypt = cast(
            Callable[[IO[bytes]], None],
            partial(self.s.decrypt, output=capture_output, passphrase="test"),
        )
        self.s.encrypt(
            source=message,
            output=decrypt,
            recipients=(key.fingerprint,),
            trust_model=gpg.TrustModel.always,
        )
        self.assertEqual(decrypted.read(), message)

    def test_encrypt_decrypt_compression(self) -> None:
        key = self._setup_key()
        message = b"a" * 50
        compressed = io.BytesIO()
        not_compressed = io.BytesIO()

        def capture_output(stream: IO[bytes], buffer: IO[bytes]) -> None:
            buffer.write(stream.read())
            buffer.seek(0)

        self.s.encrypt(
            source=message,
            output=partial(capture_output, buffer=compressed),
            recipients=(key.fingerprint,),
            trust_model=gpg.TrustModel.always,
            compress_algo=gpg.CompressAlgo.ZLIB,
            compress_level=9,
        )

        self.s.encrypt(
            source=message,
            output=partial(capture_output, buffer=not_compressed),
            recipients=(key.fingerprint,),
            trust_model=gpg.TrustModel.always,
            compress_algo=gpg.CompressAlgo.NONE,
        )

        # Check that invalid compression levels raise the expected error.
        for compress_level in (-1, 33, "seven"):
            with self.assertRaises(ValueError):
                self.s.encrypt(
                    source=message,
                    output=partial(capture_output, buffer=compressed),
                    recipients=(key.fingerprint,),
                    trust_model=gpg.TrustModel.always,
                    compress_algo=gpg.CompressAlgo.ZLIB,
                    compress_level=cast(int, compress_level),
                )

        # Check missing passphrase raises an error when signing is requested.
        with self.assertRaises(ValueError):
            self.s.encrypt(
                source=message,
                output=partial(capture_output, buffer=compressed),
                recipients=(key.fingerprint,),
                sign=key.fingerprint,
                passphrase=None,
                trust_model=gpg.TrustModel.always,
                compress_algo=gpg.CompressAlgo.ZLIB,
                compress_level=cast(int, compress_level),
            )

        self.assertLess(len(compressed.read()), len(not_compressed.read()))

    def test_delete_keys(self) -> None:
        self.s.import_file(SGT_HARTMANN_PUB_KEY)
        (key,) = self.s.list_pub_keys()
        self.assertEqual(key.fingerprint, SGT_HARTMANN_FINGERPRINT)
        self.s.delete_pub_keys(key.fingerprint)
        self.assertFalse(self.s.list_pub_keys())

    def test_detach_sig(self) -> None:
        self.s.import_file(CN_SEC_KEY, passphrase="test")
        (cn_key,) = self.s.list_pub_keys()
        (cn_key,) = self.s.list_sec_keys()
        msg = b"Camelot! ... It's only a model."
        with self.s.detach_sig(msg, passphrase="test") as out:
            sig = out.read()
        fpr = self.s.verify_detached_sig(sig=sig, src=msg)
        self.assertEqual(fpr, cn_key.sub_keys[0].fingerprint)
        with self.assertRaises(gpg.GPGError):
            self.s.verify_detached_sig(sig=sig, src=b"wrong message")

    def test_gnupg_home_dir_expansion(self) -> None:
        input_paths = (
            "/some/path",
            "/some/path/",
            "~/some/path/",
            "/home/user/some/~/path",
            "/home/user/some/../path",
            "~/../some/path",
            "",
            None,
        )
        home_dir = os.path.expanduser("~")
        default_gnupg_home_dir = store.get_default_gnupg_home_dir()
        expected_values = (
            "/some/path",
            "/some/path",
            os.path.join(home_dir, "some/path"),
            "/home/user/some/~/path",
            "/home/user/path",
            os.path.join(os.path.dirname(home_dir), "some/path"),
            default_gnupg_home_dir,
            default_gnupg_home_dir,
        )

        # Note: the reason for using os.path.abspath() on the expected_value
        # in the comparison below is to ensure the path uses the correct,
        # plateform specific, path separator.
        for input_path, expected_value in zip(input_paths, expected_values):
            g = store.GPGStore(gnupg_home_dir=input_path)
            self.assertEqual(g.gnupg_home_dir, os.path.abspath(expected_value))


CN_PUB_KEY = b"""-----BEGIN PGP PUBLIC KEY BLOCK-----

mI0EXcPQFwEEAMm1d9jlC5Zw1y/buUV6MuT5ABp4H8Sr3+MUf/GMFKPvd4Qboitd
Yf3eX753y0MNgzFlsSl8CtSO9pd+lqEt4WNMbIVWti04JAM6tD4lqeSzW57vlQlb
sGRf70fg9Qt1dc2LR0HcUi6bw46eWbSGGR3ZM7jbxB9F/VjpaTKI9S69ABEBAAG0
KkNodWNrIE5vcnJpcyA8Y2h1Y2subm9ycmlzQHJvdW5kaG91c2UuZ292PojOBBMB
CAA4FiEEKGahQqFvVOButzz5Lj5/4o/kEq4FAl3D0BcCGy8FCwkIBwIGFQoJCAsC
BBYCAwECHgECF4AACgkQLj5/4o/kEq59GQP+ONPvcLBccHAYbf0utUCiWZux9EwH
BN/TfOo1Vpgbq/DiBZcPoVeDvGTJDPg3dSUxsQzMHztp1UAi6o5Q6XCAGALMlxU9
QIHb4fyfbTQX1QrtB2EyLD/9O8nePrhqTqAd+xpdyvAw8L+hMoTyk0JnVW/UBVLH
RK4L9NaBxhSapfS4jQRdw9AXAQQAsuju5Ccwg3mDJcV+bR9yHIc+XyXcsbzFW0VU
lgNXiQoVHKJQ+X/SgElmxKwik8yeQ4CiM3/GeKmjhKB7JZnp4U+61Dfew+qc6Net
uAdNu7f26x5q237tjU9zx4JzhdnDMhrXkuYl/VR95S7CHlt1QlVxP1/Psx11a/Ej
xB+7ZDsAEQEAAYkBawQYAQgAIBYhBChmoUKhb1Tgbrc8+S4+f+KP5BKuBQJdw9AX
AhsuAL8JEC4+f+KP5BKutCAEGQEIAB0WIQRK0g8wPkscJLLIn7rzDUwzQHo/YwUC
XcPQFwAKCRDzDUwzQHo/YzIkA/4m5TWu7yvVzxjtybqHpShxrrZeTzWRrSu/SiCQ
bR8pGWP9NhnRDcfH/zMX6sMMorE6BBHI8fFMzJB974Lv0q2S8njVMuv+tIH7t+Um
KxlTY2Nz+uzFjuv2rDvPL4ozb4iZfOFq1WOwrml3fpE3qQzqLypd4OBj4H+ITghJ
DiJ55n2eBACItELQ3PcTXeh7XmXTeV3/lVhGHWlhUvcQUCNZCo9AFoX9aYBPX6OF
arsEzjNcZilc/R+r3xYF4kV2kspQQPGoslHN0Zq4Wxp0tOh/IevqjJ3bSzcCqwGz
c9fhdV81kJHiCZUFT03X+D5LrOJJ857/vwL1Roi5UgjRjX1jMFV/tg ==
=0f3v
-----END PGP PUBLIC KEY BLOCK-----
"""

CN_SEC_KEY = b"""-----BEGIN PGP PRIVATE KEY BLOCK-----

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
T03X+D5LrOJJ857/vwL1Roi5UgjRjX1jMFV/tg ==
=G52m
-----END PGP PRIVATE KEY BLOCK-----
"""

UMLAUTS_PUB_KEY = b"""-----BEGIN PGP PUBLIC KEY BLOCK-----

mI0EXcQPZwEEAMFLJh5nhUL3e2cIIEHw2lUwleWu/FMgy5GVVGho1pzSjqxc2cML
0PTLePd5/w/BOHH7tx2404CcwNVF8NrdPgFLV7mZu0Q4eUJNG+yz4EpUBCVK2si/
vNijeF3YH2vO18cyTCGiCW6vXi1cJqf6k73PCrSOPqj7QuNi41Ahkr5FABEBAAG0
KVdpdGggVW1sw6R1dHMgPHdpdGgudW1sYXV0c0B1bWxhdXRzLmluZm8+iM4EEwEI
ADgWIQS1Rlqvu4FLhxmgfbVt8x+lbBrrcQUCXcQPZwIbLwULCQgHAgYVCgkICwIE
FgIDAQIeAQIXgAAKCRBt8x+lbBrrca0uA/9Dj+s3F4FzO2MsDGaD8WXuZ8LPFSRW
zehWewIeRS6hT7L9+LNF3m0GVOueXCPrHj/8iBstc5UbFuph3Pu/3Cgw5YnnSkcC
/LPFGRlc5Z6oRF259qZNW8NafOoi1E4o/LAN1QG5SChYUS2jcyDrosJekGEaPP3n
0KqQQPYC7Smu3riNBF3ED2cBBADClqvryRmApeYO8tQcGWaiFa27vFmM4FCAzbPK
tt88N1GaHWgycgVV/dChhWDVVkEDnas+WwVMz39ZZi8tejBrk1mtoIIBctn8AWJL
W7VH9ZOrfPm1UuqLE7YMhu9hl7i4ANIJnJMsjYnOnb/Z9ButzIobZdigV7a1j47t
pXHnuwARAQABiQFrBBgBCAAgFiEEtUZar7uBS4cZoH21bfMfpWwa63EFAl3ED2cC
Gy4AvwkQbfMfpWwa63G0IAQZAQgAHRYhBHW94ZPbXFu5K4+7zYDWfVUAnJDMBQJd
xA9nAAoJEIDWfVUAnJDMBb4EAKt1sMe/6MhTsn3weshU5U6T217W/lxXmz5vErnO
yd0WaMWOsGN7WEV/UtoVMZ/EBBdIqswUiujDPd8oL3yCsNBZNDigyCGX6shqCeRP
AAUkpC/0KWDP33PNenGSMFzoBcghYBRUuVucvamzskDfidsKbLv+/7FkRwzstg7L
5/GUKGkD/2LlSZlm+qDBzDt5q+tQaGOQnJmebF7o4FQ8feY7GNcFQ9DMV9lR5vuZ
jV4OTQVS2Prv2ASuN7rPRbUYeJD5t7Mko9DzL+6XGgjPim6Wg1xlRSRkskksbX3y
QndrRiimeh43nPBLOBRN9HQoaywkc6hoAZTQAvCgOZli507dp8Mz
=sfjX
-----END PGP PUBLIC KEY BLOCK-----
"""

SGT_HARTMANN_PUB_KEY = b"""-----BEGIN PGP PUBLIC KEY BLOCK-----

mQENBF3MKrABCACw6ZFUve5lTSCtDfhcuDH0pFd7AF0uM1o4kEBLKfcEImrgGo7S
LX7tooxsx2gNv4ARHW4XL5pixLj4itRBDeUGczdDzNwQeE6HmWNW2JtqF7/h1TTr
iw3UwS3eOG8sNrZxx2yLoIF/JZP2CDLz7jXDhuAvLdoK8hzNX82PVUkoVKtPYhbk
1gw3y1coH2Z6rdAp6EwrMSg95vbwzKjuhcyYlxRodwlvmJhDBRxr86QCCRNiA6R8
7Nugtt/wP5XbxcxgNBmciX10NPR4eIoQk4acyGlDvOdrF50h2DPAw3HUdOw513xN
4b7NOHlJJk0+Uo4yKcZ2LXmeiSNU6TY93moLABEBAAG0LUd1bm5lcnkgU2d0LiBI
YXJ0bWFubiA8aGFydG1hbm5AYnVsbHNoaXQuZ292PokBVAQTAQgAPhYhBNoaNjvF
4R2nOAaopOPkAkoOViIeBQJdzCqwAhsDBQkDwmcABQsJCAcCBhUKCQgLAgQWAgMB
Ah4BAheAAAoJEOPkAkoOViIeSIEH/RDXmilCOkoR6uxJgNm7MUqavL2/s3ks57uk
qDrldJm3T5SKBCgrUSP3UaiBIwq+M32k23+CLNl8RQBVwhFAnJcHmMK/fEVcSK8G
HKy4CS8yu1xwDIgWWeDBtbo6r4IEah19dBSLOrxeyBFoI65pRHP18AWMaHnKv5nz
GXdGiLlRl6rKbyBxnesXweR+IIZJhciphhzuV8HtnyHsess0Toq2kjiCGp7Kjkz1
6YQSiHawAj3nV+/RK0kNLZsuQOgY7X2WVw4HAU//Ap1XdtMbOxberLcUU7Rzeudg
uiWfkmTMM36mhojOjtPhgB1J9ZZZCe5KM7hRB2VFuJE45r3S5LCIswQTAQgAHRYh
BChmoUKhb1Tgbrc8+S4+f+KP5BKuBQJdzCsMAAoJEC4+f+KP5BKuz3oD/inKIFnX
KzFblhnLeHf+tW7JQ9EVu+7rTKKyHHay7sgzVQ2KfySemFYwn2fgXUOuZtuk0axe
BHV0qTgL0vfnadxXF96tjFQ14xhBym6KR2ccvQN+/GLM5c0iBbp59azMy0q4VyJH
5c435C3Yq9ownEvJRRdYdJgaFTU1wjwQs7qZuQENBF3MKrABCADguI7FCLGtG6rZ
/EJv58Bnihfz9OuUSc/R6DaFbGGtolTzpTskX3pK1daYigPDDv4iMN5KnO1eeJyp
wmyRpC2yKBLw70z87QGPSviQHWTvyj22YF9ByywFKAuZeY2tpWwkLW2bbVm38LLT
hwmDRkQ8nQZPufvpDOHq6AC84ymW5TuHKEYTfF//14hyonOK40HNjSdEC6ZvfN2n
N80y9g3IvaNGsPOo3MW4z877W9v/IAvFlTEVnyRA0hXEykFnUYk//Eh6cnDTlrCO
hLwd9bbcivPPpjiGYLjgvDghyXK/qv2T4ahiMq2qxp5F8c4x/aTq8U//9GIEU7nd
danxrHsZABEBAAGJATwEGAEIACYWIQTaGjY7xeEdpzgGqKTj5AJKDlYiHgUCXcwq
sAIbDAUJA8JnAAAKCRDj5AJKDlYiHiyUB/9ZH1ZUF/lHsFjFgypyv1BfqFIyYZk9
1/zSHdwUl7svtBrc8XewisxgCBywbzJWHCooAAkSmwSrCFnqVfoUFCdAYxd3lrX1
DA2WEDcIr3Im2wUOKw0fB5yyBcep5QAzoRFl3uZwOcAYrqq38L7xAoRka991oPIk
nzY4GfcR+7ftmzKDPcXjTIbLQwmDNR0vDy7kNBB7ycHWwrMfadWGrGmeQ8pgTnP4
Egfkuv5fEQ3njiV3QcRwmTtqPEVPmA1G/TStAPZa9cBfYHTxH1JzxwVhYvBWXoA3
vwMVdh5kI53+JxM0k7OS6SI8cpf4pmiyLypdkyOCql2HYe7iPuRk0IYi
=lmDh
-----END PGP PUBLIC KEY BLOCK-----
"""

ENCRYPTED_MESSAGE = (
    b"\x84\x8c\x03\xf3\rL3@z?c\x01\x03\xff\\\t\xea;f\xb4`b\x05\xfeJ(\xdf"
    b'^`"\x87B/\x8b\xdfYD\xb4^\x03\x99R\x0bn\x1c\x12\xca6Ju\x8e\x03\x1fI'
    b"U|~\x89>w\x18'\xad\xbb\xa0\x86\x85\x1a\r\x93\xe8$\xd0H\xf8\xef\xfa"
    b"\x16\x87\x17K|\x9d$\xeb<\xbd\x0e3N\xbd{\xf1bT\xcd\xa3-\xc6\x83\x0e"
    b"\x96\xc5\xcb--\x93P\x15\xe7@\x84\x8fR\xfa\t\xc2\x99\x1f\xc4\xf0`\xfc"
    b"\x87v\x04\x1c\x9ef\x03\xc7Jh\x840\x112/\x1b\x06L\xf4\xd2<\x01\xbb"
    b"\xd2\x80=\x17\x9d\xc5ww\n\xd9\xf7%\x9fpzg\\\x1fz\x02\xf8$\x17\xe7V"
    b"\x825\xdd\n\xedu\x12\xa9\xac\xab5\x99\x9b\x7f\x9a\x8f\\\xd1\xa8\xb2"
    b"\xe9!\x1dH\xa3\x1c\xd9\xf9\xd1l\x86\xe7\x12"
)
ENCRYPTED_MESSAGE_CN = (
    b"\x84\x8c\x03\xf3\rL3@z?c\x01\x03\xffw\x058f\x95\xbd\xe5\x8d1q"
    b"\xdd\x80\xbd\x8d\xb5v5\xb3\xcf\x92\xb9?6\x8a \xfc\xc9\xc9\xad"
    b"\xccI\xd7\xc1@\xe3\xb3]\xbag\xcb\xae\x99\xbdkB\xdd\xcaS\x86598"
    b"\x00\xdd\xe1C\xad$1<\xe0\xac\xd5\x9b4\xc0w\xb5O\xf6\x8a/\x88\x7f"
    b"\x1b!\xb7\x08x\x0cUV\xd3\x1e\xaba\xe8\x03]\xc79\xea\x05\x0f*\xdc"
    b"\xa5\x88\xac\xa3Y\xa0\xfb\xd24\xf4\xa0hD\xe3\xaa\x11\xd1\xf9o"
    b"\xf7\xf7\xc3\xc8:\x0c\x16\xd5W\xfa%\x8f7\xd2F\x01q\x07\xd0\xde"
    b"~\xe1V\x00h\xc0O=ls?\x13\xfc\x9e\x8aY>e\x10$\xd2\xdb;\x18\xc0"
    b"\xf7]\xa2)r\xfe\xf8\xd9\x05\xcb\xcc\r8\xb5\xaf\x8b\xa0\xff.\xa1T"
    b"&_\x17\xdb\x0bi\x04\xd0\xa3\xa2\x9c\x8b\x80\x96\xb5\x10I\xea`"
)
