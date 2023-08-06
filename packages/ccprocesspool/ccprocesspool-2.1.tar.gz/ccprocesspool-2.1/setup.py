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


setup(name='ccprocesspool',
      version='2.1',
      description='Process pool to add/check/stop all processes in pool',
      long_description=READMarkDown.read_string(),
      long_description_content_type='text/markdown',
      url='',
      author='OpenFibers',
      author_email='openfibers@gmail.com',
      license='MIT',
      packages=['ccprocesspool'],
      zip_safe=False)
