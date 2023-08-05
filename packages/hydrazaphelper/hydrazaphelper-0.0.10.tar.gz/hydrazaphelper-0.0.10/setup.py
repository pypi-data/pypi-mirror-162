from setuptools import setup, find_packages
import pathlib


VERSION = '0.0.10'
DESCRIPTION = 'Robot Framework Wrapper For OWASP ZAP Application '

# The directory containing this file
HERE = pathlib.Path(__file__).parent

setup(name='hydrazaphelper',
      version=VERSION,
      description='Robot Framework Wrapper For wrapper for owasp zap',
      author='efe.pisirici',
      author_email='efe.pisirici@accenture.com',
      license='Apache',
      setup_requires=['wheel'],
      install_requires=['requests'],
      readme='README.md'
      )