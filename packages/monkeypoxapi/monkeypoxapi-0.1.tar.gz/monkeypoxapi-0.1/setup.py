
from setuptools import setup, find_packages


setup(
    name='monkeypoxapi',
    version='0.1',
    license='MIT',
    author="Cary K",
    author_email='cakuang1@berkeley.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/cakuang1/MonkeyPoxAPI',
    install_requires=[
          'pandas',
          'requests'
      ],

)