from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='trilio',
  version='0.1.5',
  description='Trilio is a blockchain written in Python that utilizes the proof-of-work concept and helps creating a more smooth and transparent transaction experience, with multiple integrations such as NFT(s) and tokens. ',
  long_description=open('README.txt').read(),
  url='',
  author='Abdurrahman Ismail Giumale',
  author_email='abdxrrahman.ismail@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='python,experimental,blockchain,in-development,token,blockchain-technology,proof-of-work,python-blockchain', 
  packages=find_packages(),
  install_requires=["datetime"] 
)