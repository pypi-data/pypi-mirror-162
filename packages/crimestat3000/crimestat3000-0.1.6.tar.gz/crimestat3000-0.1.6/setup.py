from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    author="Sergey Bondarkov",
    author_email="q4qk79ncm@mozmail.com",
    description="A tool for parsing crime statistics reports (form 4-ЕГС) from crimestat.ru.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="crimestat3000",
    version="0.1.6",
    url='https://github.com/def-useful/crimestat3000',
    packages=find_packages(include=["crimestat3000", "crimestat3000.*"]),
    install_requires=['pandas'],
    python_requires='>=3.7'
)
