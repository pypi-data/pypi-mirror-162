#!/usr/bin/env python3
"""
See: python setup.py --help-commands

python setup.py build        # build everything needed to install in "build/"
python setup.py sdist        # create a source distribution (tarball, zip file, etc.) in "dist/"
python setup.py bdist_wheel  # create wheel in "dist/"
"""
from pathlib import Path
from setuptools import setup, find_packages

BASE_DIR = Path(__file__).resolve().parent

REQUIREMENTS = {
    # install
    "": "requirements.txt",
    # extras
    "pgsql": "requirements_pgsql.txt",
    "django": "requirements_django.txt",
}

VERSION = "0.2.1"

def parse_pip_requirements(extra=""):
    path = BASE_DIR.joinpath(REQUIREMENTS[extra])
    with open(path, "r", encoding="utf-8") as file:
        requirements = []
        for line in file.read().splitlines():
            pos = line.find("#")
            if pos >= 0:
                line = line[0:pos]
            line = line.strip()
            if not line:
                continue
            if line.startswith("-r "):
                continue # should be added as an EXTRA requirement
            requirements.append(line)
        return requirements

if __name__ == "__main__":
    setup(
        name="zut",
        version=VERSION,
        author="Ipamo",
        author_email="dev@ipamo.net",
        description="Reusable Python, Django and PostgreSql utilities",
        long_description=BASE_DIR.joinpath("README.md").read_text().strip(),
        long_description_content_type="text/markdown",
        url="https://gitlab.com/ipamo/zut",
        project_urls={
            "Bug Tracker": "https://gitlab.com/ipamo/zut/issues",
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        packages=["zut"] + [f"zut.{pkg}" for pkg in find_packages(where="./zut")],
        package_data={
            "zut.pgsql": ["*.sql"]
        },
        python_requires=">=3.7.3", # Debian 10 (Buster)
        setup_requires=[
            "setuptools"
        ],
        install_requires=parse_pip_requirements(),
        extras_require={ extra: parse_pip_requirements(extra) for extra in REQUIREMENTS.keys() if extra },
        data_files=[
            ('', REQUIREMENTS.values()),
        ],
    )
