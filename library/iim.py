#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Valdemar Lemche <valdemar@lemche.net>
# The MIT License (MIT) (see https://opensource.org/licenses/MIT)

""" Include fragment with the following in DOCUMENTATION section of module
extends_documentation_fragment:
    - iim.documentation
"""

class ModuleDocFragment(object):
    "Common parameters for IBM Installation Manager modules"
    DOCUMENTATION = """
options:
    logdir:
        description:
            - Path and file name of installation log file
        default: /tmp

    preserve:
        description:
            - Preseve packages used during installation
        default: false
        type: bool
        version_added: "2.4"

    reponsefile:
        description:
            - Create IIM reponse file in C(logdir)
        default: false
        type: bool
        aliases:
            - record
        version_added: "2.4"

    src:
        description:
            - Path to product repository (installation files)
        required: true
        aliases:
            - repositories

    state:
        description:
            - Whether product should be installed or uninstalled
        default: present
        choices:
            - present
            - absent
"""
