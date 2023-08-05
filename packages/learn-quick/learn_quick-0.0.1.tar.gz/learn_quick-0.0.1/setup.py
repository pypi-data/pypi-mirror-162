from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='learn_quick',
  version='0.0.1',
  description='A Simplest Explanation of ML algorithms',
  long_description=open('README.txt').read(),
  url='',  
  author='Gaurav Goswami,seyjuti Banerjee',
  author_email='piyush.goswami888@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='education,learning', 
  packages=find_packages(),
  install_requires=[''] 
)