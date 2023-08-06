from setuptools import setup, find_packages

long_description = 'A Python package to generate simple logos'

reques = ['pillow', 'telegraph', 'requests']

setup(
  name='pystlogo',
  version='0.0.1',
  description='A Python package to generate simple logos',
  long_description=long_description,
  url='https://github.com/Sithijatd/pystlogo',  
  author='Sithijatd',
  author_email='Sithijatd@users.noreply.github.com',
  license='MIT', 
  classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3',
  'Programming Language :: Python :: 3.4',
  'Programming Language :: Python :: 3.5',
  'Programming Language :: Python :: 3.6',
  'Programming Language :: Python :: 3.9',
  'Programming Language :: Python :: 3.10',
],
  keywords=['Telegram', 'python', 'logo', 'anime'], 
  packages=find_packages(),
  install_requires=reques
)
