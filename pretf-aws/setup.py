
from setuptools import setup


setup(
    name="pretf-aws",
    version='0.0.1',
    author="Raymond Butcher",
    author_email="randomy@gmail.com",
    license="MIT License",
    packages=["pretf_aws"],
    install_requires=["boto-source-profile-mfa>=0.0.7", "pretf"],
)
