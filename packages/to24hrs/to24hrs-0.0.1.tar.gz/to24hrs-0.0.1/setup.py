from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'time converter'
LONG_DESCRIPTION = 'A package to convert 12hr to 24 format.' \
                   'To use this library, use the following syntax:' \
                   'convert("hh:mm AM to hh:mm PM")'

# Setting up
setup(
    name="to24hrs",
    version=VERSION,
    author="Developer Mayuresh",
    author_email="dharwadkarmayuresh@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'tutorial', 'to 24 hour', 'conversion', '12 hr to 24 hr'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)