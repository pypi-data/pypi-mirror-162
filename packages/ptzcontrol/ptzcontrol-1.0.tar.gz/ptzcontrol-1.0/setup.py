from distutils.core import setup
import setuptools
packages = ['ptzcontrol']# 唯一的包名，自己取名
setup(name='ptzcontrol',
	version='1.0',
	author='cyq',
    packages=packages, 
    package_dir={'requests': 'requests'},)
