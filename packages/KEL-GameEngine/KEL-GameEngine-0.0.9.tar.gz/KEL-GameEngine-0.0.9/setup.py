from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.9'
DESCRIPTION = 'A Simple Game Engine Libary'
LONG_DESCRIPTION = 'Chech github: https://github.com/coding610/KEL/tree/master'


# Setting up
setup(
    name="KEL-GameEngine",
    version=VERSION,
    author="Sixten Bohman",
    author_email="sixten.bohman.08@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,

    packages=find_packages(),
    
    install_requires=['pygame'],
    keywords=['python', 'pygame', 'Game Engine', 'Simple', 'Beginner', 'Learning'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
