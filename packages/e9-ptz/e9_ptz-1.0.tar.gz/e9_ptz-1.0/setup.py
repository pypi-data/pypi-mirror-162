from distutils.core import setup
import setuptools
packages = ['e9_ptz']# 唯一的包名，自己取名
setup(name='e9_ptz',
	version='1.0',
	author='cyq',
    packages=packages, 
    package_dir={'requests': 'requests'},)
