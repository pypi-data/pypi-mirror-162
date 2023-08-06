import pathlib
from setuptools import setup


class Version(object):
    name = "relational_calculus"
    description = "RWTH Aachen Computer Science i5/dbis assets for Lecture Datenbanken und Informationssysteme"
    version = "0.1.5"


# The directory containing this file
HERE = pathlib.Path(__file__).parent.resolve()

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="dbis-relational-calculus",
    version=Version.version,
    description=Version.description,
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://git.rwth-aachen.de/i5/teaching/dbis-relational-calculus.git",
    author="Til Mohr, Lara Radtke, Philipp Hochmann",
    author_email="hochmann@dbis.rwth-aachen.de",
    license="Apache",
    classifiers=[
        "Programming Language :: Python :: 3.10",
    ],
    packages=["relational_calculus"],
    include_package_data=True,
    install_requires=["typeguard"],
)
