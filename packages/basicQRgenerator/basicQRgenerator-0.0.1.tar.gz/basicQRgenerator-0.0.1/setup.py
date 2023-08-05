from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='basicQRgenerator',
  version='0.0.1',
  description='Creates a QR code and saves it as a .jpg file',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='xdsboi',
  author_email='JJdevcontact@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='qr code', 
  packages=find_packages(),
  install_requires=['requests'] 
)