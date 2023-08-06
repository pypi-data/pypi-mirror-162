import json
import os
import sys
from setuptools import setup
from setuptools.command.install import install


class CustomInstall(install):

	def run(self):

		install.run(self)
		print("hello")

		

setup(name='targaryen_controller', version='0.0.1',description='test',author='test',license='MIT',zip_safe=False,cmdclass={'install': CustomInstall})
