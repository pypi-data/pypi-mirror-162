from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'XOne_Team library'
LONG_DESCRIPTION = 'The  Best  Library Will Come In THe Future All Code Returned To Amr Elmenyawy'

# Setting up
setup(
    name="XOne_Magic",
    version=VERSION,
    author="Amr Elmenyawy",
    author_email="XOne_support@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['python', 'Xsms', 'Xcall', 'XGmail', 'XFB', 'XKwai'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
