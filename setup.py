import pathlib
from setuptools import setup
from tes_reader import __version__ as version

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="tes-reader",
    version=version,
    description="A module to read and parse TES (The Elder Scrolls) files.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sinan-ozel/tes-reader",
    author="Sinan Ozel",
    license="Creative Commons Zero v1.0 Universal",
    packages=['tes_reader']
)