from setuptools import setup
import os
import zpp_args

setup(name="zpp_args",
      version=zpp_args.__version__,
      author="ZephyrOff",
      author_email="contact@apajak.fr",
      keywords = "terminal args zephyroff",
      classifiers = ["Development Status :: 5 - Production/Stable", "Environment :: Console", "License :: OSI Approved :: MIT License", "Programming Language :: Python :: 3"],
      packages=["zpp_args"],
      description="Module pour le traitement des arguments d'une ligne de commande",
      long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
      long_description_content_type='text/markdown',
      url = "https://github.com/ZephyrOff/py-zpp_args",
      platforms = "ALL",
      license="MIT")