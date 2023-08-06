from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='Beanory',
  version='0.0.2',
  description='An encryption method',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Jack Boyd',
  author_email='boydypug@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='encryption, decryption, binary', 
  packages=find_packages(),
  install_requires=[''] 
)
