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


setup(name='ccrootpath',
      version='1.1',
      description='Set project root path for importing local modules',
      long_description=READMarkDown.read_string(),
      long_description_content_type='text/markdown',
      url='https://github.com/OpenFibers/CCRootPath',
      author='OpenFibers',
      author_email='openfibers@gmail.com',
      license='MIT',
      packages=['ccrootpath'],
      zip_safe=False)
