 #!/usr/bin/env python
###############################################################################

###############################################################################

import sys
from setuptools import setup, find_packages

def check_python_version():
    if sys.version_info[:2] < (3, 8):
        print('Python 3.8 or newer is required. Python version detected: {}'.format(sys.version_info))
        sys.exit(-1)


setup(
    name="sinais",
    version="0.0.2",
    description="Easy generation of signals for signal processing using python.",
    author="Rafael do Nascimento Pereira",
    author_email="rnp@25ghz.net",
    url="https://github.com/rafaelnp/sinais",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
     package_dir={"":"sinais"},
    packages=find_packages(where="sinais"),
    license="GPL-3",
    python_requires=">=3.8",

    install_requires = [
        "fxpmath>=0.4.0",
        "numpy>=1.20.0",
        "plotly>=5.1.0",
    ],
    extras_requires = [
        "pytest==6.2.4",
         "twine>=3.6.0",
    ],
)
