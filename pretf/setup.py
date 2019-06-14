import os
import re

from setuptools import setup


def get_version():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, "pretf", "version.py")) as open_file:
        contents = open_file.read()
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", contents, re.MULTILINE)
    return match.group(1)

setup(
    name="pretf",
    version=get_version(),
    author="Raymond Butcher",
    author_email="ray.butcher@claranet.uk",
    license="MIT License",
    packages=["pretf"],
    entry_points={"console_scripts": ("pretf=pretf.cli:main",)},
    install_requires=["colorama", "pyhcl"],
    extras_require={"aws": ["pretf.aws"]},
    zip_safe=False,
)
