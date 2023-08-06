from setuptools import setup, find_packages
from os.path import exists, join, dirname
import re
import sys


PROJECT = 'pyDictStore'
AUTHOR = 'Peter Varney, OpenWayside'
AUTHOR_EMAIL = 'pyDictStore@OpenWayside.org'
URL = 'https://OpenWayside.org'
DESCRIPTION = "pyDictStore adds automated dictionary storage to properties" \
              " eliminating the need for code bodies, property getters and" \
              " setters. It also provides a property change event."

def VERSION(project:str):
    init = join(dirname(__file__),'src',project,'__init__.py')
    if exists(init):
        with open(init, 'r', encoding="utf8") as f:
            return re.search(r"__VERSION__ = '(.*?)'"
                            , f.read()
                            ).group(1)
    return None

def DESCRIPTION_LONG():
    return open(join(dirname(__file__),'README.md'), 'r', encoding='utf8').read()

def INSTALL_REQUIRES():
    req = join(dirname(__file__),'requirements.txt')
    if not exists(req): ... #FIXME AUTO BUILT?
    return  open(req, 'r', encoding='utf16').read().split('\n')


if __name__ == '__main__':
    sys.argv.append('build')
    sys.argv.append('sdist')
    sys.argv.append('bdist_wheel')
    setup(
        install_requires=INSTALL_REQUIRES(),
        name=PROJECT,
        version=VERSION(PROJECT),
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=DESCRIPTION,
        long_description=DESCRIPTION_LONG(),
        long_description_content_type="text/markdown",
        url=URL,
        project_urls={
            'Documentation': 'https://openwayside.org/rtm/pyDictStore/',
            #'Funding': '',
            'Source': 'https://github.com/OpenWayside/pyDictStore',
            'Issues': 'https://github.com/OpenWayside/pyDictStore/issues',
        },
        packages=find_packages("src"),
        package_dir={"": "src"},
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.10',
    )