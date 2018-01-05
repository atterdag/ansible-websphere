# Ansible formatting tags

Format | Tag
:----- | :----
Italic | `I()`
Bold   | `B()`
Module | `M()`
URL    | `U()`
Const  | `C()`

# Ansible option types

Type    | Yaml type    | Yaml default value | Python type | Python default value
:------ | :----------- | :----------------- | :---------- | --------------------
Boolean | `boolean`    | `true`/`false`     | `bool`      | `True`/`False`
Hash    | `dictionary` |                    | `dict`      |
Integer | `integer`    |                    | `int`       |
String  | `string`     | `test value`       | `str`       | `test value`
JSON    | `json`       |                    | `json`      |
Array   | `list`       |                    | `list`      |
Path    | `path`       |                    | `path`      |

## DOCUMENTATION example

```yaml
type: bool
```

## module_args example

```python
type="bool"
```

# imcl command for IIM (from ansible role)

```
tmp_imcl_command: "{{ unarchive_dest | default('/tmp') }}/{{ unarchive_creates }}/Linux_x86_64/EnterpriseCD-Linux-x86_64/InstallationManager/tools/imcl"
```

```
base_installation_path: "/opt/IBM"
data_installation_path: "{{ base_installation_path }}/IMDataLocation"
im_installation_path: "{{ base_installation_path }}/InstallationManager"
shared_installation_path: "{{ base_installation_path }}/IMShared"
imcl_command: "{{ base_installation_path }}/InstallationManager/eclipse/tools/imcl"
```

```
installation_manager_params: "-acceptLicense
 -accessRights group
 -eclipseLocation {{ im_installation_path }}
 -installationDirectory {{ im_installation_path }}
 -dataLocation {{ data_installation_path }}
 -log {{ tmp_dir | default('/tmp') }}/install-im-log.xml
 -nl en
 -record {{ tmp_dir | default('/tmp') }}/install-im-response.xml
 -repositories {{ unarchive_dest | default('/tmp') }}/{{ unarchive_creates }}/Linux_x86_64/EnterpriseCD-Linux-x86_64/InstallationManager
 -sharedResourcesDirectory {{ shared_installation_path }}
 -preferences com.ibm.cic.common.core.preferences.keepFetchedFiles=false,\
com.ibm.cic.common.core.preferences.preserveDownloadedArtifacts=false,\
offering.service.repositories.areUsed=false,\
com.ibm.cic.common.core.preferences.searchForUpdates=false
 -silent"
```

```
{{ tmp_imcl_command }} install com.ibm.cic.agent {{ installation_manager_params }}
```
