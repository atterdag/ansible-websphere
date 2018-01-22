#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Valdemar Lemche <valdemar@lemche.net>
# Copyright (c) 2015 Amir Mofasser <amir.mofasser@gmail.com>
# The MIT License (MIT) (see https://opensource.org/licenses/MIT)

"""This is an Ansible module. Installs/Uninstall IBM Installation Manager
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
---
module: ibmim_installer

short_description:
    - Install/Uninstall IBM Installation Manager

description:
    - Install/Uninstall IBM Installation Manager

version_added: "1.9.4"

author:
    - "Amir Mofasser (@amofasser)"
    - "Valdemar Lemche (@atterdag)"

options:
    accessRights:
        description:
            - Allow only root, a normal user, or members of a normal user's
              primary group to run IIM
        default: admin
        choices:
            - admin
            - nonAdmin
            - group
        type: string
        aliases:
            - aR
        version_added: "2.4"

    dataLocation:
        description:
            - Specify the directory location for the Installation Manager data
              directory. This location stores information about installed
              packages.
        default: /opt/IBM/IMDataLocation
        type: path
        aliases:
            - dL
        version_added: "2.4"

    dest:
        description:
            - Path to desired installation directory of Installation Manager
        default: /opt/IBM/InstallationManager
        type: path
        aliases:
            - installationDirectory
            - iD

    logdir:
        description:
            - Path and file name of installation log file
        default: /tmp
        type: path

    preserve:
        description:
            - Preseve packages used during installation
        default: false
        type: boolean
        version_added: "2.4"

    reponsefile:
        description:
            - Create IIM reponse file in C(logdir)
        default: false
        type: boolean
        aliases:
            - record
        version_added: "2.4"

    sharedResourcesDirectory:
        description:
            - Repository path of installed packages if preserve is set to yes
        default: /opt/IBM/IMShared
        type: path
        aliases:
            - sRD
        version_added: "2.4"

    src:
        description:
            - Path to installation files for Installation Manager
        required: true
        type: path
        aliases:
            - repositories

    state:
        description:
            - Whether Installation Manager should be installed or removed
        default: present
        choices:
            - present
            - absent
        type: string

notes:
    - For more information about IIM accessrights see
      U(https://www.ibm.com/support/knowledgecenter/en/SSDV2W_1.8.5/com.ibm.silentinstall12.doc/topics/r_admin_nonadmin.html)
"""

EXAMPLES = """
# Install IIM into /srv/was/IBMIM using user was
- name: Install
    become: yes
    become_user: was
    ibmim_installer:
        state: present
        src: /srv/was/IBMIM
        logdir: /srv/was/tmp'
        accessrights: nonAdmin

# Uninstall IIM installed in /opt/IBM/InstallationManager as root
- name: Uninstall
    become: yes
    ibmim_installer:
        state: absent
        dest: /opt/IBM/InstallationManager
"""

RETURN = """
im_version:
    description: IBM Installation Manager version installed
    returned: success
    type: string
    sample: "1.8.0"
    version_added: "1.9.4"

im_internal_version:
    description: IBM Installation Manager version and date stamp
    returned: success
    type: string
    sample: "1.8.0.20140902_1503"
    version_added: "1.9.4"

im_arch:
    description: IBM Installation Manager version CPU architecture
    returned: success
    type: string
    sample: "64-bit"
    version_added: "1.9.4"

im_header:
    description: IBM Installation Manager version output header
    returned: success
    type: string
    sample: "Installation Manager (installed)"
    version_added: "1.9.4"

stdout:
    description: Standard output from imcl command
    returned: success
    type: string
    sample: "Installed com.ibm.cic.agent_1.8.7000.20170706_2137 to the /opt/IBM/InstallationManager/eclipse directory."
    version_added: "2.4"

stderr:
    description: Standard error from imcl command
    returned: failure
    type: string
    sample: "/bin/sh: 1: /tmp/iim/tools/imcl: not found"
    version_added: "2.4"
"""

import os
import subprocess
import platform
import datetime
import re

"import module snippets"
from ansible.module_utils.basic import AnsibleModule


def is_installed(dest):
    """Checks if Installation Manager is already installed at dest
    :param dest: Installation directory of Installation Manager
    :return: True if already installed. False if not installed
    """

    """ If destination dir does not exists then its safe to assume that IM is
    not installed
    """
    if not os.path.exists(dest):
        return False
    else:
        if "installed" in get_version(dest)["im_header"]:
            return True
        return False


def get_version(dest):
    """Runs imcl with the version parameter and stores the output in a dict
    :param dest: Installation directory of Installation Manager
    :return: dict
    """
    child = subprocess.Popen(
        ["{0}/eclipse/tools/imcl version".format(dest)],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout_value, stderr_value = child.communicate()
    module_facts = dict()
    try:
        module_facts["im_version"] = \
            re.search("Version: ([0-9].*)", stdout_value).group(1)
        module_facts["im_internal_version"] = \
            re.search("Internal Version: ([0-9].*)", stdout_value).group(1)
        module_facts["im_arch"] = \
            re.search("Architecture: ([0-9].*-bit)", stdout_value).group(1)
        module_facts["im_header"] = \
            re.search("Installation Manager.*", stdout_value).group(0)
    except AttributeError:
        pass
    return module_facts


def generate_module_args():
    """define the available arguments/parameters that a user can pass to
    the module
    """
    module_args = dict(
        accessRights=dict(
            default="admin",
            choices=["admin", "nonAdmin", "group"],
            type="str",
            aliases=["aR"]
        ),
        dataLocation=dict(
            default="/opt/IBM/IMDataLocation",
            type="path",
            aliases=["dL"]
        ),
        dest=dict(
            default="/opt/IBM/InstallationManager",
            type="path",
            aliases=["iD", "installationDirectory"]
        ),
        logdir=dict(
            default="/tmp",
            type="path"
        ),
        preserve=dict(
            type="bool"
        ),
        reponsefile=dict(
            type="bool",
            aliases=["record"]
        ),
        sharedResourcesDirectory=dict(
            default="/opt/IBM/IMShared",
            type="path",
            aliases=["sRD"]
        ),
        src=dict(
            required=True,
            type="path",
            aliases=["repositories"]
        ),
        state=dict(
            default="present",
            choices=["present", "absent"],
            type="str"
        )
    )
    return module_args


def install(module, module_facts):
    """ TBW
    """
    if module.check_mode:
        module.exit_json(
            changed=False,
            msg="IBM Installation Manager where to be installed at {0}".format(
                module.params['dest']
            )
        )
    "Check if IM is already installed"
    if not is_installed(module.params['dest']):
        "Check if paths are valid"
        if not os.path.exists(module.params['src']):
            module.fail_json(msg=module.params['src'])
        if not os.path.exists(module.params['logdir']):
            if not os.listdir(module.params['logdir']):
                os.makedirs(module.params['logdir'])
        logfile = "install-iim-{0}-{1}-log.xml".format(
            platform.node(),
            datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        )
        responsefile = "install-iim-{0}-{1}-response.xml".format(
            platform.node(),
            datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        )
        imcl_command = "{7}/tools/imcl install com.ibm.cic.agent " \
            "-acceptLicense " \
            "-accessRights {0} " \
            "-eclipseLocation {2} " \
            "-installationDirectory {2} " \
            "-dataLocation {1} " \
            "-log {3}/{8} " \
            "-nl en " \
            "-record {3}/{9} " \
            "-repositories {7} " \
            "-sharedResourcesDirectory {6} " \
            "-preferences com.ibm.cic.common.core.preferences.keepFetchedFiles={4}," \
            "com.ibm.cic.common.core.preferences.preserveDownloadedArtifacts={4}," \
            "offering.service.repositories.areUsed=false," \
            "com.ibm.cic.common.core.preferences.searchForUpdates=false " \
            .format(module.params['accessRights'],
                module.params['dataLocation'],
                module.params['dest'],
                module.params['logdir'],
                module.params['preserve'],
                module.params['reponsefile'],
                module.params['sharedResourcesDirectory'],
                module.params['src'],
                logfile,
                responsefile)
        child = subprocess.Popen(
            [imcl_command],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            module.fail_json(
                msg="IBM Installation Manager installation failed",
                stderr=stderr_value,
                stdout=stdout_value,
                module_facts=module_facts
            )
        """ Module finished. Get version of IM after installation so that
        we can print it to the user
        """
        result = get_version(module.params['dest'])
        module.exit_json(
            msg="IBM Installation Manager installed successfully",
            changed=True,
            stdout=stdout_value,
            stderr=stderr_value,
            module_facts=module_facts
        )
    else:
        module.exit_json(
            changed=False,
            msg="IBM Installation Manager is already installed",
            module_facts=module_facts
        )


def uninstall(module, module_facts):
    """ Uninstall IBMIM
    """
    if module.check_mode:
        module.exit_json(
            changed=False,
            msg="IBM Installation Manager where to be uninstalled from {0}".format(module.params('dest')),
            module_facts=module_facts
        )

    imcl_command = "{0}/eclipse/tools/imcl".format(module.params['dest'])

    "Check if IM is already installed"
    if is_installed(module.params['dest']):
        if not os.path.exists(imcl_command):
            module.fail_json(msg=imcl_command + " does not exist")
        child = subprocess.Popen(
            [imcl_command + " uninstall com.ibm.cic.agent"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            module.fail_json(
                msg="IBM Installation Manager uninstall failed",
                stderr=stderr_value,
                stdout=stdout_value,
                module_facts=module_facts
            )

        # Module finished
        module.exit_json(
            changed=True,
            msg="IBM Installation Manager uninstalled successfully",
            stdout=stdout_value,
            module_facts=module_facts
        )
    else:
        module.exit_json(
            changed=False,
            msg="IBM Installation Manager is not installed",
            module_facts=module_facts
        )


def run_module():
    """ Runs the module with arguments
    """
    module_facts = dict(
        changed=False,
        im_version='',
        im_internal_version='',
        im_arch='',
        im_header=''
    )

    "seed the result dict in the object"
    result = dict(
        changed=False,
        im_version='',
        im_internal_version='',
        im_arch='',
        im_header=''
    )

    module = AnsibleModule(
        argument_spec=generate_module_args(),
        supports_check_mode=True
    )

    if module.params['state'] == 'present':
        install(module, module_facts)
    elif module.params['state'] == 'absent':
        uninstall(module, module_facts)


def main():
    """ TBW
    """

    run_module()


if __name__ == '__main__':
    main()
