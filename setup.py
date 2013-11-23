from setuptools import setup, find_packages

VERSION="0.1"

setup(
    name="punchbowl",
    version=VERSION,

    description="IRC bot framework",
    author="Mac Chapman",
    author_email="mac@veryhappythings.co.uk",
    url="http://www.veryhappythings.co.uk",

    install_requires = [
        "irc==8.0.1",
    ],
    entry_points = {
    },
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    package_data = {
    },
    data_files = [
    ],

    keywords = [
    ],
    classifiers = [
    ],
)

