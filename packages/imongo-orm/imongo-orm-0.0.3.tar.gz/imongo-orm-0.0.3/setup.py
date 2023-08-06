import os
import pathlib

from setuptools import find_packages
from setuptools import setup

from imongo import __version__

try:
    # pip >=20
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.req import parse_requirements
    except ImportError:
        import re
        from dataclasses import dataclass

        def parse_requirements(f, *args, **kwargs):
            @dataclass
            class Req:
                requirement: str

            requirements = []
            for line in open(f, "r").read().split("\n"):
                if re.match(r"(\s*#)|(\s*$)", line):
                    continue
                if re.match(r"\s*-e\s+", line):
                    requirements.append(re.sub(r"\s*-e\s+.*#egg=(.*)$", r"\1", line))
                elif re.match(r"\s*-f\s+", line):
                    pass
                else:
                    requirements.append(Req(line))
            return requirements


def load_requirements(fname):
    """Parse requirements.txt file"""
    requirements = list(parse_requirements(fname, session="test"))
    parsed_reqs = []
    for r in requirements:
        try:
            value = getattr(r, "req")
            if value is None:
                raise AttributeError
            parsed_reqs.append(value)
        except AttributeError:
            parsed_reqs.append(r.requirement)
    return parsed_reqs


CURRENT_PATH = str(pathlib.Path(__file__).parent.resolve())
REQUIREMENTS_FILE = os.path.join(CURRENT_PATH, "requirements.txt")
README_FILE = os.path.join(CURRENT_PATH, "..", "README.md")
BUILD_DEPENDENCIES = ["wheel"]
DEPENDENCIES = BUILD_DEPENDENCIES + load_requirements(REQUIREMENTS_FILE)

# Get the long description from the README file
try:
    import pypandoc
    from pypandoc.pandoc_download import download_pandoc

    # see the documentation how to customize the installation path
    # but be aware that you then need to include it in the `PATH`
    download_pandoc()

    LONG_DESCRIPTION = pypandoc.convert_file(README_FILE, "rst")
except ImportError:
    with open(README_FILE, encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()

setup(
    name="imongo-orm",
    version=__version__,
    description="MongoDB ORM interface for Python",
    long_description=LONG_DESCRIPTION,
    author="Roberto Crespo",
    author_email="rcrespoa@alumni.nd.edu",
    packages=find_packages("."),
    install_requires=DEPENDENCIES,
    url="https://github.com/robertocrespond/imongo",
    keywords="mongo mongodb orm db database document",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
