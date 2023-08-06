import sys

from setuptools import setup, find_packages

if sys.version_info[0] != 3:
    print('This script requires Python >= 3')
    exit(1)

with open('README.md', 'r') as readme_file:
    readme = readme_file.read()

setup(
    name='trayan',
    version='0.1.1',
    author='re1von',
    author_email='re1von@bk.ru',
    url='https://github.com/re1von-project/trayan',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
)
