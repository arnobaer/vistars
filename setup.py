from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="vistars",
    version="1.0.0",
    author="Bernhard Arnold",
    author_email="bernhard.arnold@cern.ch",
    description=("Simple CERN vistars viewer."),
    license="GPLv3",
    url = "http://github.com/arnobaer/vistars",
    py_modules=['vistars'],
    install_requires=["PyQt5"],
    entry_points="""
        [console_scripts]
        vistars=vistars:main
    """,
    long_description=long_description,
)
