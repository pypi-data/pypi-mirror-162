Zut
===

Reusable Python, Django and PostgreSql utilities.

## Install

From PyPI:

    pip install zut[pgsql,django]

From Git, last version:

    pip install git+https://gitlab.com/ipamo/zut.git@main#egg=zut[pgsql,django]

Use SSH instead of HTTPS url:

    pip install git+ssh://git@gitlab.com/ipamo/zut.git@main#egg=zut[pgsql,django]

Specific version:

    pip install git+https://gitlab.com/ipamo/zut.git@0.2.0#egg=zut[pgsql,django]

In a `requirements.txt` file:

    zut[pgsql,django] @ git+https://gitlab.com/ipamo/zut.git@v0.2.0#egg=zut[pgsql,django]


## Dev quick start

Install Python, its packet manager (`pip`) and PostgreSql.
Under Linux, also install password manager `pass` (used as _credentials manager_).

Windows pre-requisites:

- Download [Python](https://www.python.org/downloads/) and install it.
- Download [PostgreSql](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads), install it, and add binaries (`C:\Program Files\PostgreSQL\14\bin`) to PATH.

Linux (Debian) pre-requisites:

    sudo apt install python3-venv python3-pip postgresql pass

Create Python virtual environment (example for Windows):

    python -m venv .venv      # Debian: python3 -m venv .venv
    .\.venv\Scripts\activate  # Linux: source .venv/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt

Generate password for PostgreSql user `zut` (save generated password as variable `POSTGRES_PASSWORD` in file `.env`):

    python -c "import random; import string; print(''.join(random.choices(string.ascii_letters + string.digits, k=16)))"

Create test database (cf. parameters in `tests/settings.py`). Example:

    psql -U postgres  # Linux: sudo -u postgres psql
    create user zut password 'REPLACE_ME'; -- !!! REPLACE WITH GENERATED PASSWORD !!!
    create database test_zut owner zut encoding 'utf8' template 'template0';
    \c test_zut
    create extension if not exists unaccent;
    quit

For Linux, configure password manager `pass`. Example:

    # Import your GPG key, show key identifier and mark key as trusted
    gpg --import my-private-gpg-key.asc
    gpg --list-secret-keys
    gpg --edit-key mykey@example.org
    trust
    5
    o
    q

    # Initialize "pass" with your GPG key
    pass init mykey@example.org

Run tests:

    python -m unittest

Run commandes :

    python -m zut --help

It is also possible to add script `zut/bin/zut.ps1` to PATH and then use directly command `zut`.
For Linux : `sudo ln -s $PWD/zut/bin/zut /usr/local/bin/`.


## Publish library

Configure `~/.pypirc`. Example:

```conf
[distutils]
    index-servers =
    pypi
    testpypi
    zut

[pypi]
    username = __token__
    password = # use project-scoped token instead

[testpypi]
    # user-scoped token
    username = __token__
    password = pypi-xxxxx...

# -----------------------------------------------------------------------------
# Project-scoped token
# Usage example: twine --repository zut
#
[zut]
    repository = https://upload.pypi.org/legacy/
    username = __token__
    password = pypi-xxxxx...
```

Prepare distribution:

    pip install twine              # if not already done
    python -m zut checkversion
    python tools.py clean
    python setup.py sdist bdist_wheel
    twine check dist/*

Upload tarball on PyPI:

    # $env:HTTPS_PROXY="..."                         # if necessary
    # $env:TWINE_CERT="C:\...\ca-certificates.crt"   # if necessary
    twine upload --repository zut dist/*
