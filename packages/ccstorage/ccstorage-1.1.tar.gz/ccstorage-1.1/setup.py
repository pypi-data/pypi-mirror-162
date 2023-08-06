from setuptools import setup
import os


class READMarkDown:

    @staticmethod
    def read_string(file_name='./README.md'):
        if os.path.isfile(file_name):
            with open(file_name) as f:
                lst = f.read()
                return lst
        else:
            return None


setup(name='ccstorage',
      version='1.1',
      description='Local storage: CCStorage, and simple local file string read/write: CCIO',
      long_description=READMarkDown.read_string(),
      long_description_content_type='text/markdown',
      url='',
      author='OpenFibers',
      author_email='openfibers@gmail.com',
      license='MIT',
      packages=['ccstorage'],
      zip_safe=False)
