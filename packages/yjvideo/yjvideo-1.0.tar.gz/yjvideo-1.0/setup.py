from distutils.core import  setup
import setuptools
packages = ['yjvideo']# 唯一的包名，自己取名
setup(name='yjvideo',
	version='1.0',
	author='chengyanqiang',
    packages=packages, 
    package_dir={'requests': 'requests'},)
