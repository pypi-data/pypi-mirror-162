# -*- coding: utf-8 -*-

from  unitts.version import __version__
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

# usage:
# python setup.py bdist_wininst generate a window executable file
# python setup.py bdist_egg generate a egg file
# Release information about eway

version = __version__
name = "unitts"
description = "unitts is a api for tts engine"
author = "yumoqing"
email = "yumoqing@gmail.com"

package_data = {}
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
	name="unitts",
	version=version,
	
	# uncomment the following lines if you fill them out in release.py
	description=description,
	author=author,
	author_email=email,
   	platforms='any',
	install_requires=[
	],
	packages=[
		"unitts"
	],
	package_data=package_data,
	keywords = [
	],
	url="https://github.com/yumoqing/unitts",
	long_description=long_description,
	long_description_content_type="text/markdown",
	classifiers = [
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
	],
)
