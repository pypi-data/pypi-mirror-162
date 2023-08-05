# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="ucid-api",
    version="0.1.6",
    description="ucid api calling library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://medium-multiply.readthedocs.io/",
    author="Mritunjay Kumar",
    author_email="mritunjaykr583@gmail.com",
    license="DELIVERY",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["ucid_api", "ucid_api.constant", "ucid_api.utils", "ucid_api.exception"],
    include_package_data=True,
    install_requires=["requests==2.28.1", "urllib3==1.26.11"]
)
