from gettext import find
from setuptools import setup, find_packages

setup(
    name="calc_course_package",
    version="0.1 alpha",
    packages=find_packages('src'),
    package_dir={'':'src'}
)