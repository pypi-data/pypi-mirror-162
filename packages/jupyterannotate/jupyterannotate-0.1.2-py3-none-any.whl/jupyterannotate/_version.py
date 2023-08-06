#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Stuart Quin.
# Distributed under the terms of the Modified BSD License.

import json


package_json = None
with open("./package.json", "r") as package_json_file:
    package_json = json.loads(package_json_file.read())

__version__ = package_json["version"]
version_info = tuple(__version__.split("."))
