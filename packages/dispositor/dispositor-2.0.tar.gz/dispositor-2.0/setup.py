from setuptools import setup, find_packages

setup(name='dispositor',
      version='2.0',
      description='Added the offset degree experiment',
      packages=['dispositor', 'dispositor.db', 'dispositor.experiments.degree_of_displacement'],
      author_email='astro.slfd@gmail.com',
      zip_safe=False)