import os
import re

from setuptools import find_namespace_packages, setup


def get_version():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, "..", "pretf", "pretf", "version.py")) as open_file:
        contents = open_file.read()
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", contents, re.MULTILINE)
    return match.group(1)

setup(
    name="pretf.aws",
    version=get_version(),
    author="Raymond Butcher",
    author_email="randomy@gmail.com",
    license="MIT License",
    packages=find_namespace_packages("pretf.*"),
    install_requires=["boto3", "pretf"],
    zip_safe=False,
)
