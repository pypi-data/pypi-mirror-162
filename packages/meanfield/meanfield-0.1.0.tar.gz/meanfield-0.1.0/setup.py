'''
Author: acse-xy721 xy721@ic.ac.uk
Date: 2022-08-09 17:54:57
LastEditors: acse-xy721 xy721@ic.ac.uk
LastEditTime: 2022-08-09 17:58:00
FilePath: /irp-xy721/meanfield/setup.py
'''

from setuptools import setup, find_packages

setup(
    name = "meanfield",
    version = "0.1.0", #name of version
    keywords = ("pip", "pathtool","timetool", "magetool", "mage"),
    description = "mean-field model",
    author = "xy721",
    author_email = "yxy332211@gmail.com",
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)
