from setuptools import setup
from cvascode import __version__

setup(name='cvascode',
      version=__version__,
      author='Ben Stuart',
      author_email='ben@benstuart.ie',
      url='https://github.com/benchoncy/cvascode',
      license='LICENSE',
      description='Utility to generate CVs from templates.',
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      entry_points={
          'console_scripts': [
            'cvascode=cvascode.app:main',
          ]
      },
      packages=['cvascode'],
      install_requires=[
          'pyyaml',
          'jinja2',
          'schema',
          'docxtpl'
      ]
      )
