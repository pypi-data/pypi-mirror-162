from gettext import find
from setuptools import setup, find_packages



setup(
    name="vailde_name_packege",
    version="0.1 alpha",
    package=find_packages('src'),
    package_dir={'':'src'}
)