from setuptools import setup

setup(
  name = 'kvtintri',
  packages = ['kvtintri'],
  version = '0.1',
  description = 'This is a helper library used to manage Tintri VMstore devices via python.',
  author = 'Russell Pope',
  author_email = 'rpope@kovarus.com',
  url = 'https://github.com/kovarus/tintri-automation',
  keywords = ['tintri'],
  install_requires = ['requests', 'prettytable'],
  classifiers = [],
)
