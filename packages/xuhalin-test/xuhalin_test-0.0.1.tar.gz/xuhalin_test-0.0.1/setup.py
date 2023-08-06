#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: mage
# Mail: mage@woodcol.com
# Created Time: 2018-1-23 19:17:34
#############################################


from setuptools import setup, find_packages

setup(
  name = "xuhalin_test",
  version = "0.0.1",
  keywords = ("pip", "test"),
  description = "test",
  long_description = "test",
  license = "MIT Licence",

  url = "http://180.169.109.94:3000/xuhailin/project_mock",
  author = "xuhailiin",
  author_email = "117570235@qq.com",

  packages = find_packages(),
  include_package_data = True,
  platforms = "any",
  install_requires = []
)