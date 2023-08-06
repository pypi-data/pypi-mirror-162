import logging
from os import path
from codecs import open
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open("README.md", "r") as fh:
    long_description = fh.read()


def _parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


# parse_requirements() returns generator of pip.req.InstallRequirement objects
try:
    install_reqs = _parse_requirements("requirements.txt")
except Exception:
    logging.warning("Fail load requirements file, so using default ones.")
    install_reqs = []

exec(open('bpc/version.py').read())

setup(
    name="bpc",
    version=__version__,
    author="kyitharhein",
    author_email="kyitharhein18@gmail.com",
    description="Burmese text normalizer, wordbreak, converter, cleaner and phonemizer for speech related tasks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/1chimaruGin/Burmese_Phomizer_and_Cleaner",
    download_url='https://github.com/1chimaruGin/Burmese_Phomizer_and_Cleaner/archive/refs/tags/v0.0.1.tar.gz',
    packages=find_packages(exclude=['build', 'dist']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=install_reqs,
)