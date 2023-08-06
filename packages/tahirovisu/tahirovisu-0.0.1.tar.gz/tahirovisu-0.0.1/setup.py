from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='tahirovisu',
  version='0.0.1',
  description='A very basic Python package demo',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Tahir MAT',
  author_email='matahir33@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='visualization', 
  packages=find_packages(),
  install_requires=[''] 
)