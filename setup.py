from setuptools import setup

from pretf import __version__

setup(
    name='pretf',
    version=__version__,
    author='Raymond Butcher',
    author_email='ray.butcher@claranet.uk',
    license='MIT License',
    packages=(
        'pretf',
    ),
    entry_points = {
        'console_scripts': (
            'pretf=pretf.cli:main',
        ),
    },
    install_requires=(
        'boto-source-profile-mfa>=0.0.7',
        'colorama',
        'deepmerge',
    ),
)
