from setuptools import setup, find_packages

setup(
    author="Sergey Bondarkov",
    description="A tool for parsing crime statistics reports (form 4-ЕГС) from crimestat.ru.",
    name="crimestat3000",
    version="0.1.0",
    packages=find_packages(include=["crimestat3000", "crimestat3000.*"]),
    install_requires=['pandas', 're', 'time', 'random'],
    python_requires='>=3'
)
