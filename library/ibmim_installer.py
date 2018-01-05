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
    ibmim:
        state: present
        src: /srv/was/IBMIM
        logdir: /srv/was/tmp'
        accessrights: nonAdmin

# Uninstall IIM installed in /opt/IBM/InstallationManager as root
- name: Uninstall
    become: yes
    ibmim:
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
"""

import os
import subprocess
import platform
import datetime
import re

"import module snippets"
from ansible.module_utils.basic import AnsibleModule

def run_module():
    """ Runs the module with arguments
    """

    "define the available arguments/parameters that a user can pass to the module"
    module_args = dict(
        accessRights=dict(
            type="list",
            default="admin",
            choices=["admin", "nonAdmin", "group"]
        ),
        dataLocation=dict(
            default="/opt/IBM/IMDataLocation"
        ),
        dest=dict(
            default="/opt/IBM/InstallationManager"
        ),
        logdir=dict(
            default="/tmp/"
        ),
        preserve=dict(
            type="bool"
        ),
        reponsefile=dict(
            type="bool"
        ),
        sharedResourcesDirectory=dict(
            default="/opt/IBM/IMShared"
        ),
        src=dict(
            default="/install"
        ),
        state=dict(
            type="list",
            default="present",
            choices=["present", "absent"]
        )
    )

    "seed the result dict in the object"
    result = dict(
        changed=False,
        im_version='',
        im_internal_version='',
        im_arch='',
        im_header=''
    )

    module_facts = dict(
        im_version=None,
        im_internal_version=None,
        im_arch=None,
        im_header=None
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

def isProvisioned(self, dest):
    """Checks if Installation Manager is already installed at dest
    :param dest: Installation directory of Installation Manager
    :return: True if already provisioned. False if not provisioned
    """

    """ If destination dir does not exists then its safe to assume that IM is
    not installed
    """
    if not os.path.exists(dest):
        return False
    else:
        if "installed" in getVersion(dest)["im_header"]:
            return True
        return False

def getVersion(self, dest):
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

def main():
    """TBW
    """

    state = module.params['state']
    src = module.params['src']
    dest = module.params['dest']
    logdir = module.params['logdir']

    if state == 'present':

        if module.check_mode:
            module.exit_json(
                changed=False,
                msg="IBM IM where to be installed at {0}".format(dest)
            )

        "Check if IM is already installed"
        if not isProvisioned(dest):

            # Check if paths are valid
            if not os.path.exists(src+"/install"):
                module.fail_json(msg=src + "/install not found")

            if not os.path.exists(logdir):
                if not os.listdir(logdir):
                    os.makedirs(logdir)

            logfile = "{0}_ibmim_{1}.xml".format(
                platform.node(),
                datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            )
            child = subprocess.Popen(
                ["{0}/install "
                 "-acceptLicense "
                 "--launcher.ini {0}/silent-install.ini "
                 "-log {1}/{2} "
                 "-installationDirectory {3}".format(src, logdir, logfile, dest)],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg="IBM IM installation failed",
                    stderr=stderr_value,
                    stdout=stdout_value,
                    module_facts=module_facts
                )
            # Module finished. Get version of IM after installation so that
            # we can print it to the user
            getVersion(dest)
            module.exit_json(
                msg="IBM IM installed successfully",
                changed=True,
                stdout=stdout_value,
                stderr=stderr_value,
                module_facts=module_facts
            )
        else:
            module.exit_json(
                changed=False,
                msg="IBM IM is already installed",
                module_facts=module_facts
            )

    elif state == 'absent':

        if module.check_mode:
            module.exit_json(
                changed=False,
                msg="IBM IM where to be uninstalled from {0}".format(dest),
                module_facts=module_facts
            )

        "Check if IM is already installed"
        if isProvisioned(dest):
            uninstall_dir = "/var/ibm/InstallationManager/uninstall/uninstallc"
            if not os.path.exists("/var/ibm/InstallationManager/uninstall/uninstallc"):
                module.fail_json(msg=uninstall_dir + " does not exist")
            child = subprocess.Popen(
                [uninstall_dir],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg="IBM IM uninstall failed",
                    stderr=stderr_value,
                    stdout=stdout_value,
                    module_facts=module_facts
                )

            # Module finished
            module.exit_json(
                changed=True,
                msg="IBM IM uninstalled successfully",
                stdout=stdout_value,
                module_facts=module_facts
            )
        else:
            module.exit_json(
                changed=False,
                msg="IBM IM is not installed",
                module_facts=module_facts
            )


if __name__ == '__main__':
    main()
