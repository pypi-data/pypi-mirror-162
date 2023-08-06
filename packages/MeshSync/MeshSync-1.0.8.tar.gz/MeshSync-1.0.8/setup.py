# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

import re
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('meshsync/mesh_sync.py').read(),
    re.M
).group(1)

with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name="MeshSync",
    packages=["meshsync"],
    entry_points={
        "console_scripts": ['meshsync = meshsync.mesh_sync:main']
    },
    version=version,
    description="Command line tool to download/update Mesh projects with ease!",
    long_description=long_descr,
    author="Rawa Dev",
    author_email="rawa@rawa.dev",
    url="https://rawa.dev",
)
