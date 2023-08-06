from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.0.1'
DESCRIPTION = 'Find and verify work emails.'

# Setting up
setup(
    name="emailfinderpy",
    version=VERSION,
    author="Sean Michael Suntoso",
    author_email="<contact@ssuntoso.com>",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ssuntoso/emailfinderpy',
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'dnspython'],
    keywords=['python', 'email', 'email finder', 'work email', 'company domain', 'start up'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)