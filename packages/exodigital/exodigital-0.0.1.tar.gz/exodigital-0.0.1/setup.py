import zipfile
from pkg_resources import  Distribution
from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Intended Audience :: Developers',
  'Intended Audience :: End Users/Desktop',
  'Operating System :: Microsoft :: Windows',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 

setup(
  name='exodigital',
  version='0.0.1',
  description='A digital clock with displays the weather and temperature of local and global cities',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  long_description_content_type='text/markdown',
  url='https://t.me/exoticwondrous',  
  author='Ahmed Mohammed',
  author_email='ahmdsmhmmd@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Exo digital clock', 
  packages=find_packages(),
  install_requires=['requests'],
  package_data={'':['*.dll']},
  zip_safe=False
)
