from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Extracting information from the website'
LONG_DESCRIPTION = 'A package that allows to get all urls from a wbebsite, prints useful (information extractable) webpages, get all emails and phone numbers present in the website'

# Setting up
setup(
    name="putali",
    version=VERSION,
    author="Ujjawal Shah",
    author_email="ujjawalshah360@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests', 'ultimate-sitemap-parser'],
    keywords=['python', 'email', 'phone number', 'telephone', 'url', 'count url'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)