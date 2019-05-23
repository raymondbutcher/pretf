from setuptools import setup

setup(
    name='pretf',
    version='0.0.1',
    author='Raymond Butcher',
    author_email='ray.butcher@claranet.uk',
    license='MIT License',
    packages=(
        'pretf',
    ),
    install_requires=(
        'boto-source-profile-mfa>=0.0.7',
        'deepmerge',
    ),
)
