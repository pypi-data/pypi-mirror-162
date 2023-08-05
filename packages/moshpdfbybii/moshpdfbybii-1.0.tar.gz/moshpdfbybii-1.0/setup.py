from pathlib import Path
import setuptools


setuptools.setup(
    name="moshpdfbybii",
    version=1.0,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"])


)

# On terminal run below
# pip install setuptools wheel twine
# python .\setup.py sdist bdist_wheel
# twine upload dist/*
