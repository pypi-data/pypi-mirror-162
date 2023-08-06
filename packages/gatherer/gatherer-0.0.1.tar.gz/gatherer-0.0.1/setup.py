from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Collects data from multiple MySQL Databases in a multi-tenant architecture'
LONG_DESCRIPTION = 'Gatherer helps to collect scattered data across different databases which share the same ' \
                   'schema. It outputs the whole collected data into a single csv file. '

# Setting up
setup(
    name="gatherer",
    version=VERSION,
    author="rexshijaku (Rexhep Shijaku)",
    author_email="<rexhepshijaku@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=['gatherer'],
    install_requires=[],
    keywords=['python', 'mysql', 'database', 'collector', 'gatherer', 'csv', 'multi-tenant'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
