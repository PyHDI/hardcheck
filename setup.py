from setuptools import setup, find_packages

import utils.version
import re
import os

m = re.search(r'(\d+\.\d+\.\d+(-.+)?)', utils.version.VERSION)
version = m.group(1) if m is not None else '0.0.0'


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(name='hardcheck',
      version=version,
      description='Checkpointing/Restore Framework for Reconfigurable Systems',
      long_description=read('README.rst'),
      keywords='FPGA, Verilog HDL',
      author='Shinya Takamaeda-Yamazaki',
      author_email='shinya.takamaeda_at_gmail_com',
      license="Apache License 2.0",
      url='https://github.com/PyHDI/hardcheck',
      packages=find_packages(),
      #package_data={ 'path' : ['*.*'], },
      install_requires=['pyverilog>=1.0.6', 'veriloggen>=0.6.1', 'ipgen>=0.2.0', 'Jinja2>=2.8'],
      extras_require={
          'test': ['pytest>=2.8.2', 'pytest-pythonpath>=0.7'],
      },
      )
