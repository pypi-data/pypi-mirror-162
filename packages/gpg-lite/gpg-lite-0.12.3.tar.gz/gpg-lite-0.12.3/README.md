[![pipeline status](https://gitlab.com/biomedit/gpg-lite/badges/master/pipeline.svg)](https://gitlab.com/biomedit/gpg-lite/-/commits/master)
[![coverage report](https://gitlab.com/biomedit/gpg-lite/badges/master/coverage.svg)](https://gitlab.com/biomedit/gpg-lite/-/commits/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![python version](https://img.shields.io/pypi/pyversions/gpg-lite.svg)](https://pypi.org/project/gpg-lite)
[![license](https://img.shields.io/badge/License-LGPLv3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![latest version](https://img.shields.io/pypi/v/gpg-lite.svg)](https://pypi.org/project/gpg-lite)

# gpg-lite: a cross-platform python binding for GnuPG

`gpg-lite` is a python API for [GPG / GnuPG](https://gnupg.org/) that offers
the following functionalities:

* PGP key management: create and delete keys. Search for keys in the local
  keyring.
* Data encryption: encrypt and sign files.
* Data decryption: decrypt files.
* Signature verification: verify signatures attached to files.
* Keyserver interactions: query, download and upload keys to keyservers.

The design objectives behind `gpg-lite` are the following:
* Cross-plateform: support for 🐧, 🍏, Windows.
* Multi-version: support as many gpg versions as possible.
* Provide custom functions for keyserver access, as the behavior of the gpg
  binary is inconsistent across versions.
* Reduce functionality to the most useful and frequent operations to reduce
  maintenance costs.

## Installation

### From `PyPI`

It's simple, just do:

```bash
[sudo] pip install [--user] gpg-lite
```

### From git

To install `gpg-lite` from this git repository:

```bash
git clone https://gitlab.com/biomedit/gpg-lite.git
cd gpg-lite
./setup.py install [--user]
```

## Using gpg-lite

Note that in order to use `gpg-lite` you will need to have [GnuPG](https://gnupg.org/)
installed on your local machine.

To get started using `gpg-lite` import the module as follows:

```python
import gpg_lite as gpg
```

Most of the functionality of `gpg-lite` is provided via methods of the
`GPGStore` object class. This class aims to represents an instance of a
**GnuPG home directory**, the directory on your local machine that contains
the GPG keyrings and other related database files.

Here is how a `GPGStore` instance is created if your GnuPG installation is
*standard*. Here *standard* means that your GnuPG executable is named either
`gpg` or `gpg2`, that it is part of your PATH, and that the GnuPG home
directory is at its default location (e.g. `~/.gnupg` on Linux):

```python
gpg_store = gpg.GPGStore()
print("The GnuPG home directory is set to:", gpg_store.gnupg_home_dir)
print("The GnuPG executable is:", gpg_store.gnupg_binary)
```

For **non-standard** GnuPG installations, the optional `gnupg_home_dir` and
`gnupg_binary` arguments of `GPGStore()` can be used: the former allows to
specify the path of a custom GnuPG home directory, while the later allows to
specify a non-standard GnuPG executable name and/or path. Using a leading `~`
character in the `gnupg_home_dir` argument is supported and expands to the
user's home directory.

```python
gpg_store = gpg.GPGStore(
    gnupg_home_dir="~/custom/path/gnupg_home_dir",
    gnupg_binary="/usr/bin/gpg")
print("The GnuPG home directory is set to:", gpg_store.gnupg_home_dir)
print("The GnuPG executable is:", gpg_store.gnupg_binary)
```

### Generate a new key

```python
gpg_store = gpg.GPGStore()
key_fingerprint = gpg_store.gen_key(
    key_type='RSA',
    key_length=4096,
    full_name="Chuck Norris",
    email="chuck.norris@roundhouse.gov",
    passphrase="Chuck Norris does not need one - the password needs him")
print("Created new key with fingerprint:", key_fingerprint)
```

### Retrieve public and secret keys from local keyring

Retrieving one or more keys from the local keyring is done using the
`list_pub_keys()` (for public keys) and `list_sec_keys()` (for secret/private
keys) methods:

* If no `search_terms` argument is passed, all keys are returned.
* If an iterable - typically a tuple or a list - of strings is passed as
  `search_terms` argument, only keys whose fingerprint, key ID or user ID
  matches one of the items in the iterable are returned.
  Note that passing directly a string to `search_terms` is unlikely to return
  the expected keys, as individual characters in the string will be iterated
  over and matched).
  **Important:** if multiple matching keys are found, they are **not** returned
  in any particular order.
* When using `list_pub_keys()`, the `sigs=True` argument can be optionally
  passed to return keys with their signatures.

```python
keys = gpg_store.list_pub_keys()
for key in keys:
    print(key.uids[0], key.fingerprint)

key = gpg_store.list_pub_keys(search_terms=("chuck.norris",))[0]
key = gpg_store.list_pub_keys(search_terms=("chuck.norris@roundhouse.gov",), sigs=True)[0]
fingerprint = key.fingerprint
key = gpg_store.list_pub_keys(search_terms=(fingerprint,), sigs=True)[0]
```

### Export public and secret keys from local keyring

Keys can be exported in both ascii-armored and binary format using
`export()` and `export_secret` methods.

**Important**: secret keys, when exported, are encrypted with the provided password.
However, it is critical to store them in a safe, private space.

```python
fingerprint = "55C5314BB9EFD19AE7CC4774D892C41917B20115"
pub_key_ascii = gpg_store.export(fingerprint, armor=True)
pub_key_binary = gpg_store.export(fingerprint, armor=False)
priv_key_ascii = gpg_store.export_secret(fingerprint, passphrase="secret", armor=True)
priv_key_binary = gpg_store.export_secret(fingerprint, passphrase="secret", armor=False)
```

### Encrypt and sign data

Data decryption is performed using the `encrypt()` method of the `GPGStore`
class.

```python
import tempfile

encrypted_file = tempfile.NamedTemporaryFile(
    prefix="gpg-lite_test_", suffix=".gpg", delete=False).name

with open(encrypted_file, "w") as f:
    gpg_store.encrypt(
        source=b"When Chuck Norris throws exceptions, it's across the room.\n",
        recipients=["chuck.norris@roundhouse.gov"],
        output=f)
```

Optionally, the encrypted file can also be signed with a private key. This
requires to pass the passphrase associated with the private key.

```python
with open(encrypted_file, "w") as f:
    gpg_store.encrypt(
        source=b"When Chuck Norris throws exceptions, it's across the room.\n",
        recipients=["chuck.norris@roundhouse.gov"],
        output=f,
        sign="chuck.norris@roundhouse.gov",
        passphrase="Chuck Norris does not need one - the password needs him")
```

Please see `help(gpg.GPGStore.encrypt)` for more details.

### Decrypt data

Data decryption is performed using the `decrypt()` method of the `GPGStore`
class. Here is an example, reading from the file we encrypted earlier, and
outputting the result to a new unencrypted file:

```python
decrypted_file = encrypted_file[:-4]
with open(encrypted_file, "rb") as f, open(decrypted_file, "w") as f_out:
    gpg_store.decrypt(
      source=f,
      output=f_out,
      passphrase="Chuck Norris does not need one - the password needs him")

with open(decrypted_file, "r") as f:
    print("Decrypted message:", "".join(f.readlines()))

# Delete files created in this demo:
import os
os.remove(encrypted_file)
os.remove(decrypted_file)
```

### Make and verify detached signatures

A so-called detached signature is a file that contains information to verify
both the hash of the file who was signed and the signee, i.e. the person who
signed the file.

Detached signatures can be created as follows:

```python
with tempfile.NamedTemporaryFile(delete=False) as input_file, \
     tempfile.NamedTemporaryFile(delete=False) as signed_file:

    # Create a new file with some text.
    with open(input_file.name, mode="w") as f:
        f.write("When Chuck Norris throws exceptions, it's across the room.\n")

    # Sign the existing file. Note that the file must be opened in binary mode.
    with open(input_file.name, mode="rb") as f_in, open(signed_file.name, mode="wb") as f_out:
        with gpg_store.detach_sig(
            src=f_in,
            signee=fingerprint,
            passphrase="Chuck Norris does not need one - the password needs him"
        ) as stream:
            f_out.write(stream.read())

    # Verify the signature.
    with open(input_file.name, mode="rb") as f, open(signed_file.name, mode="rb") as f_signature:
        signee_fingerprint = gpg_store.verify_detached_sig(src=f, sig=f_signature.read())

print("Signee fingerprint is", signee_fingerprint)
```

Same as above, but using a bytestring as input instead of a file:

```python
content_to_sign = b"Chuck Norris doesn't use web standards. The web conforms to him.\n"
with gpg_store.detach_sig(
    src=content_to_sign,
    signee=fingerprint,
    passphrase="Chuck Norris does not need one - the password needs him"
) as stream:
    signee_fingerprint = gpg_store.verify_detached_sig(src=content_to_sign, sig=stream.read())

print("Signee fingerprint is", signee_fingerprint)
```

### Delete keys from local keyring

Public and secret/private keys

**Warning:** deleted secret keys cannot be recovered or re-generated from their
public counterpart. Only delete secret keys if you are sure you will never
need them again.

```python
key = gpg_store.list_pub_keys(search_terms=("chuck.norris@roundhouse.gov",), sigs=True)[0]
fingerprint = key.fingerprint

gpg_store.delete_sec_keys(fingerprint)
gpg_store.delete_pub_keys(fingerprint)
```

### Specific exceptions raised by gpg-lite

`gpg-lite` has the following exceptions:

* `GPGError`: exception raised when the local GnuPG executable returns an error.
* `KeyserverError`: exception that is raised when a specified keyserver is not
  responding, e.g. because a wrong URL was given or the keyserver is currently
  not available.
* `KeyserverKeyNotFoundError`: exception that is raised when given key is not
  found on a specified keyserver.

## Bug Reports / Feature Requests / Contributing

Our bug tracker can be found on **GitLab** https://gitlab.com/biomedit/gpg-lite/issues.

Public comments and discussions are also welcome on the bug tracker.

Patches are always welcome 🤗!
Take into account that we use a special format for commit messages.
This is due to our release management and to auto generate our
changelog.
Here are our [guidelines](./CONTRIBUTING.md).
Also each change has to pass our CI [pipeline](.gitlab-ci.yml)
including:

* [black](https://pypi.org/project/black/) code formatting
* [pylint](https://pylint.org/) lints
* [unit](./test/) / [integration](./integration_test/) tests
* [bandit](https://pypi.org/project/bandit/) vulnerability checks (each security warning which cannot be
  avoided has to be justified)
* [mypy](http://mypy-lang.org/) type checking

## Supported GPG versions

We officially support all **GPG** versions starting from _v2.2.8_.
Unofficially, we also try to support _v2.0.22_.

## Running the unit tests

Run the following commands in `gpg-lite`'s root directory. To also run tests
that require the presence of `GnuPG` on the machine running the tests, set the
`WITH_GPG=true` environment variable.

```shell
python3 -m unittest discover -s ./test -v
WITH_GPG=true python3 -m unittest discover -s ./test -v
```
