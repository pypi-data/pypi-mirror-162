import re
from setuptools import setup

version = re.search(
        '^__version__\s*=\s*"(.*)"',
        open('gazerr/__init__.py').read(),
        re.M
    ).group(1) 

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name = "gazerr",
    packages = ["gazerr"],
    license = "MIT",
    install_requires = ['numpy', 'pandas'],
    entry_points = {
        "console_scripts": ['gazerr = gazerr.cli:main']
    },
    include_package_data=True,
    version = version,
    description = "Python library and CLI for estimation of gaze duration error.",
    long_description = long_descr,
    long_description_content_type='text/markdown',
    author = "John Hawkins",
    author_email = "john@playgroundxyz.com",
    url = "http://john-hawkins.github.io",
    project_urls = {
        'Documentation': "https://gazerr.readthedocs.io",
        'Source': "https://github.com/playground-xyz/gazerr",
        'Tracker': "https://github.com/playground-xyz/gazerr/issues" 
    }
)

