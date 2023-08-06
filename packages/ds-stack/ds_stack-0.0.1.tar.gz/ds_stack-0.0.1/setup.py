from setuptools import setup, find_packages
import codecs
import os
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows ',
  'Operating System :: MacOS :: MacOS X ',
  'Operating System :: Unix ',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
VERSION = '0.0.1'
DISCRIPTION='stack data structure'
LONG_DESCRIPTION = 'This python module can use the different functions of Stack Data Structure'
setup(
  name='ds_stack',
  version=VERSION,
  description=DISCRIPTION,
  long_description_content_type="text/markdown",
  long_description=long_description,
  url='',  
  author='Yashas R Nair',
  author_email='<yashasrnair@gmail.com>',
  license='MIT', 
  classifiers=classifiers,
  keywords=['ds_stack','stack','data structure','data structure stack'],
  packages=find_packages(),
  install_requires=['']

)