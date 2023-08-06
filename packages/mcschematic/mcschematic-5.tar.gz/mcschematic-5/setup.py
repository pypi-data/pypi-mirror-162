from setuptools import setup, find_packages
import codecs
import os

VERSION = '5'
DESCRIPTION = 'A Minecraft schematic creator library.'
LONG_DESCRIPTION = 'Allows the creation of Minecraft schematic files directly through code.'

# Setting up
setup(
    name="mcschematic",
    version=VERSION,
    author="Sloimay",
    author_email="<sloimay@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['nbtlib'],
    keywords=['python', 'minecraft', 'schematic'],
    classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Other Audience",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)