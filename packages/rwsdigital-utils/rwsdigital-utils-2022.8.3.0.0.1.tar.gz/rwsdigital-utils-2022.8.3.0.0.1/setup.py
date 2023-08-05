# setup.py

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="rwsdigital-utils",
    version="2022.08.03.0.0.1",
    description="Odoo Development Utils by RWS Digital",
    long_description=long_description,
    long_description_content_type="text/markdown",
    readme="README.md",
    author="Salvatore Castaldo",
    author_email = "salvatore.cast17@gmail.com",
    license="MIT License",
    url = "https://github.com/sCast17/rwsdigital-utils",
    classifiers = [
    	"Development Status :: 3 - Alpha",
    	"Intended Audience :: Developers",
    	"License :: OSI Approved :: MIT License",
    	"Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
    package_dir={"": "src"},
    packages=find_packages(where="src")
    )
