from setuptools import setup, find_packages

setup(name='dispositor',
      version='1.7',
      description='Added the ability to save to the database',
      packages=['dispositor', 'dispositor.db', 'dispositor.experiments.degree_of_displacement'],
      author_email='astro.slfd@gmail.com',
      zip_safe=False)