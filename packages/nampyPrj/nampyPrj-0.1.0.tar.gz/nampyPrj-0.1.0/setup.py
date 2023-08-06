from setuptools import setup, find_packages

from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="nampyPrj",
    version="0.1.0",
    description="Demo Numerical Analysis library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={'': 'nampyPrj'},
    url="https://github.com/GiordiR/nampy",
    author="Riccardo Giordani",
    author_email="riccardo.giordani93@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=find_packages('nampyPrj'),
    include_package_data=True,
    install_requires=['numpy', 'sympy', 'matplotlib']
)
