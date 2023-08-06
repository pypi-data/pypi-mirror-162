# -*- coding: ascii -*-


"""setup.py: setuptools control."""


import sys
import os
import re
import atexit
import time
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from Pragmatic import GetRelease

# Read version from Pragmatic.py
version = re.search(
	'^__version__\s*=\s*"(.*)"',
	open('Pragmatic/Pragmatic.py').read(),
	re.M
	).group(1)

# Use README.md as long description
with open("README.md", "rb") as f:
	long_descr = f.read().decode("utf-8")




class PostDevelopCommand(develop):
	def run(self):
		develop.run(self)

		print('Collecting LLVM')
		GetRelease.Get('LLVM', 'llvm-0.1')
		time.sleep(1)

		# print('Collecting Pragmatic plugin')
		# GetRelease.Get('PragmaticPlugin', '0.1')
		# time.sleep(1)

class PostInstallCommand(install):
	def run(self):
		install.run(self)
		
		print('Collecting LLVM')
		GetRelease.Get('LLVM', 'llvm-0.1')
		time.sleep(1)

		# print('Collecting Pragmatic plugin')
		# GetRelease.Get('PragmaticPlugin', '0.1')
		# time.sleep(1)


# Setuptools setup
setup(
	name = "Pragmatic",
	packages = ["Pragmatic"],
	entry_points =
	{
		"console_scripts": ['Pragmatic = Pragmatic.Pragmatic:Main']
	},
	cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
	version = version,
	description = "Python command line application bare bones template.",
	long_description = long_descr,
	long_description_content_type='text/markdown',
	author = "Szoke Balazs",
	author_email = "bala.szoke@gmail.com",
	url = "https://github.com/QEDengine",
	)