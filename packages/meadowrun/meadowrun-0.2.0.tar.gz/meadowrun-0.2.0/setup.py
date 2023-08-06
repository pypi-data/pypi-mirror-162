# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['meadowrun',
 'meadowrun._vendor',
 'meadowrun._vendor.aiodocker',
 'meadowrun._vendor.platformdirs',
 'meadowrun.aws_integration',
 'meadowrun.aws_integration.management_lambdas',
 'meadowrun.azure_integration',
 'meadowrun.azure_integration.mgmt_functions',
 'meadowrun.azure_integration.mgmt_functions.azure_core',
 'meadowrun.azure_integration.mgmt_functions.clean_up',
 'meadowrun.azure_integration.mgmt_functions.vm_adjust',
 'meadowrun.func_worker']

package_data = \
{'': ['*'], 'meadowrun': ['docker_files/*']}

install_requires = \
['aiobotocore>=2.1.2,<3.0.0',
 'aiohttp>=3.8.0,<4.0.0',
 'asyncssh>=2.11.0,<3.0.0',
 'boto3==1.21.21',
 'cloudpickle>=2.0.0,<3.0.0',
 'filelock>=3.6.0,<4.0.0',
 'kubernetes-asyncio>=24.2.0,<25.0.0',
 'protobuf>=3.18.1,<4.0.0',
 'psutil>=5.8.0,<6.0.0',
 'requests>=2.27.1,<3.0.0',
 'typing-extensions>=4.1.1,<5.0.0']

entry_points = \
{'console_scripts': ['meadowrun-local = '
                     'meadowrun.run_job_local_main:command_line_main',
                     'meadowrun-manage-azure-vm = '
                     'meadowrun.manage:main_azure_vm',
                     'meadowrun-manage-ec2 = meadowrun.manage:main_ec2']}

setup_kwargs = {
    'name': 'meadowrun',
    'version': '0.2.0',
    'description': 'The easiest way to run python code on one or more remote machines',
    'long_description': None,
    'author': 'Richard Lee',
    'author_email': 'hrichardlee@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/meadowdata/meadowrun',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
