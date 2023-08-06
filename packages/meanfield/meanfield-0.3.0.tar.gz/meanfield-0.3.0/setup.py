'''
Author: acse-xy721 xy721@ic.ac.uk
Date: 2022-08-09 17:54:57
LastEditors: acse-xy721 xy721@ic.ac.uk
LastEditTime: 2022-08-09 20:00:16
FilePath: /irp-xy721/meanfield/setup.py
'''

from setuptools import setup
import setuptools

requirements = ['numpy']  

setup(
    name = "meanfield",
    version = "0.3.0", #name of version
    keywords = ("pip", "pathtool","timetool", "magetool", "mage"),
    description = "mean-field model",
    license='MIT-0',
    author = "xy721",
    author_email = "yxy332211@gmail.com",
    packages= ['meanfield'],
    include_package_data = True,
    platforms = "any",
    install_requires = []
)
