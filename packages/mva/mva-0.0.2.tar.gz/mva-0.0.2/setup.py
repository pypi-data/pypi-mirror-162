import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.2'
PACKAGE_NAME = 'mva'
AUTHOR = 'Naveen Goutham'
AUTHOR_EMAIL = 'naveen.goutham@outlook.com'
URL = 'https://github.com/gouthamnaveen/mva'

LICENSE = 'Apache License 2.0'
DESCRIPTION = 'A package to correct the bias of forecasts/hindcasts. Read the documentation at https://github.com/gouthamnaveen/mva'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
	'numpy']

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      keywords=['mva','mean','variance','bias correction','mean and variance adjustment','bias adjustment','calibration','python'],
      packages=find_packages()
      )
