from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.3'
DESCRIPTION = 'Extracting contact-info from the website homepage'
LONG_DESCRIPTION = 'A package that allows to get contact-info (emails & phonenumbers) from the website homepage'

# Setting up
setup(
    name="putali",
    version=VERSION,
    author=["Ujjawal Shah","Mahesh Dahal"],
    author_email="ujjawalshah360@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests', 'bs4'],
    keywords=['python', 'email', 'phone number', 'telephone', 'website', 'homepage'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)