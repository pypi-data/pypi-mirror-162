# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['caracara',
 'caracara.common',
 'caracara.filters',
 'caracara.modules',
 'caracara.modules.hosts',
 'caracara.modules.prevention_policies',
 'caracara.modules.response_policies',
 'caracara.modules.rtr']

package_data = \
{'': ['*']}

install_requires = \
['crowdstrike-falconpy>=1.1.5,<2.0.0',
 'py7zr>=0.17.4,<0.18.0',
 'pyppmd==0.17.4']

entry_points = \
{'console_scripts': ['agent-versions = '
                     'examples.hosts.show_agent_versions:show_agent_versions',
                     'clear-queued-sessions = '
                     'examples.rtr.clear_queued_sessions:clear_queued_sessions',
                     'create-prevention-policy = '
                     'examples.prevention_policies.create_prevention_policy:create_prevention_policy',
                     'create-response-policy = '
                     'examples.response_policies.create_response_policy:create_response_policy',
                     'describe-prevention-policies = '
                     'examples.prevention_policies.describe_prevention_policies:describe_prevention_policies',
                     'describe-put-files = '
                     'examples.rtr.describe_put_files:describe_put_files',
                     'describe-queued-sessions = '
                     'examples.rtr.describe_queued_sessions:describe_queued_sessions',
                     'describe-response-policies = '
                     'examples.response_policies.describe_response_policies:describe_response_policies',
                     'describe-scripts = '
                     'examples.rtr.describe_scripts:describe_scripts',
                     'download-event-log = '
                     'examples.rtr.download_event_log:download_event_log',
                     'find-devices = examples.hosts.find_devices:find_devices',
                     'list-all-device-states = '
                     'examples.hosts.list_device_states:list_device_states',
                     'list-all-devices = '
                     'examples.hosts.list_all_devices:list_all_devices',
                     'list-all-group-member-ids = '
                     'examples.hosts.list_all_group_member_ids:list_all_group_member_ids',
                     'list-all-group-members = '
                     'examples.hosts.list_all_group_members:list_all_group_members',
                     'list-all-groups = '
                     'examples.hosts.list_all_groups:list_all_groups',
                     'list-device-address-changes = '
                     'examples.hosts.list_network_history:list_network_history',
                     'list-device-logins = '
                     'examples.hosts.list_login_history:list_login_history',
                     'list-hidden-devices = '
                     'examples.hosts.list_hidden_devices:list_hidden_devices',
                     'list-windows-devices = '
                     'examples.hosts.list_windows_devices:list_windows_devices',
                     'queue-command = examples.rtr.queue_command:queue_command',
                     'stale-sensors = '
                     'examples.hosts.find_stale_sensors:find_stale_sensors']}

setup_kwargs = {
    'name': 'caracara',
    'version': '0.1.4',
    'description': 'The CrowdStrike Falcon Developer Toolkit',
    'long_description': '![CrowdStrike Falcon](https://raw.githubusercontent.com/CrowdStrike/falconpy/main/docs/asset/cs-logo.png) [![Twitter URL](https://img.shields.io/twitter/url?label=Follow%20%40CrowdStrike&style=social&url=https%3A%2F%2Ftwitter.com%2FCrowdStrike)](https://twitter.com/CrowdStrike)<br/>\n\n# Caracara\n\n\n\n<!--\n![PyPI - Status](https://img.shields.io/pypi/status/caracara)\n[![Pylint](https://github.com/CrowdStrike/caracara/actions/workflows/pylint.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/pylint.yml)\n[![Flake8](https://github.com/CrowdStrike/caracara/actions/workflows/flake8.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/flake8.yml)\n[![Bandit](https://github.com/CrowdStrike/caracara/actions/workflows/bandit.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/bandit.yml)\n[![CodeQL](https://github.com/CrowdStrike/caracara/actions/workflows/codeql.yml/badge.svg)](https://github.com/CrowdStrike/caracara/actions/workflows/codeql.yml)\n-->\n[![PyPI](https://img.shields.io/pypi/v/caracara)](https://pypi.org/project/caracara/)\n![OSS Lifecycle](https://img.shields.io/osslifecycle/CrowdStrike/caracara)\n\nA friendly wrapper to help you interact with the CrowdStrike Falcon API. Less code, less fuss, better performance, and full interoperability with [FalconPy](https://github.com/CrowdStrike/falconpy/).\n\n- [Features](#features)\n- [Installation](#installation-instructions)\n- [Basic Usage](#basic-usage-example)\n- [Examples](#examples-collection)\n- [Documentation](#documentation)\n- [Contributing](#contributing)\n\n## Features\n\nA few of the developer experience enhancements provided by the Caracara toolkit include:\n| Feature | Details |\n| :---  | :--- |\n| __Automatic pagination with concurrency__ | Caracara will handle all request pagination for you, so you do not have to think about things like batch sizes, batch tokens or parallelisation. Caracara will also multithread batch data retrieval requests where possible, dramatically reducing data retrieval times for large datasets such as host lists. |\n| __Friendly to your IDE (and you!)__ | Caracara is written with full support for IDE autocomplete in mind. We have tested autocomplete in Visual Studio Code and PyCharm, and will accept issues and patches for more IDE support where needed. Furthermore, all code, where possible, is written with type hints so you can be confident in parameters and return values. |\n| __Logging__ | Caracara is built with the in-box `logging` library provided with Python 3. Simply set up your logging handlers in your main code file, and Caracara will forward over `debug`, `info` and `error` logs as they are produced. Note that the `debug` logs are very verbose, and we recommend writing these outputs to a file as opposed to the console when retrieving large amounts of lightly filtered data. |\n| __Real Time Response (RTR) batch session abstraction__ | Caracara provides a rich interface to RTR session batching, allowing you to connect to as many hosts as possible. Want to download a specific file from every system in your Falcon tenant? Caracara will even extract it from the `.7z` container for you. |\n| __Rich and detailed sample code__ | Every module of Caracara comes bundled with executable, fully configurable code samples that address frequent use cases. All samples are built around a common structure allowing for code reuse and easy reading. Just add your API credentials to `config.yml`, and all samples will be ready to go. |\n| __Simple filter syntax__ | Caracara provides an object-orientated Falcon Query Language (FQL) generator. The `FalconFilter` object lets you specify filters such as `Hostname`, `OS` and `Role`, automatically converting them to valid FQL. Never write a FQL filter yourself again! |\n| __Single authentication point of entry__ | Authenticate once and have access to every module. |\n| __100% FalconPy compatibility__ | Caracara is built on FalconPy, and can even be configured with a FalconPy `OAuth2` object via the `auth_object` constructor parameter, allowing you to reuse FalconPy authentication objects across Caracara and FalconPy. Authenticate once with FalconPy, and access every feature of FalconPy and Caracara. |\n\n## Installation Instructions\n\nCaracara supports all major Python packaging solutions. Instructions for [Poetry](https://python-poetry.org) and [Pip](https://pypi.org/project/pip/) are provided below.\n\n<details>\n<summary><h3>Installing Caracara from PyPI using Poetry (Recommended!)</h3></summary>\n\n### Poetry: Installation\n\n```shell\npoetry add caracara\n```\n\n### Poetry: Upgrading\n\n```shell\npoetry update caracara\n```\n\n### Poetry: Removal\n\n```shell\npoetry remove caracara\n```\n</details>\n\n<details>\n<summary><h3>Installing Caracara from PyPI using Pip</h3></summary>\n\n### Pip: Installation\n\n```shell\npython3 -m pip install caracara\n```\n\n### Pip: Upgrading\n\n```shell\npython3 -m pip install caracara --upgrade\n```\n\n### Pip: Removal\n\n```shell\npython3 -m pip uninstall caracara\n```\n\n</details>\n\n## Basic Usage Examples\n\n```python\n"""List Windows devices.\n\nThis example will use the API credentials provided as keywords to list the\nIDs and hostnames of all systems within your Falcon tenant that run Windows.\n"""\n\nfrom caracara import Client\n\nclient = Client(\n    client_id="12345abcde",\n    client_secret="67890fghij",\n)\n\nfilters = client.FalconFilter()\nfilters.create_new_filter("OS", "Windows")\n\nresponse_data = client.hosts.describe_devices(filters)\nprint(f"Found {len(response_data)} devices running Windows")\n\nfor device_id, device_data in response_data.items():\n    hostname = device_data.get("hostname", "Unknown Hostname")\n    print(f"{device_id} - {hostname}")\n```\n\nYou can also leverage the built in context manager and environment variables.\n\n```python\n"""List stale sensors.\n\nThis example will use the API credentials set in the environment to list the\nhostnames and IDs of all systems within your Falcon tenant that have not checked\ninto your CrowdStrike tenant within the past 7 days.\n\nThis is determined based on the filter LastSeen less than or equal (LTE) to 7 days ago (-7d).\n"""\n\nfrom caracara import Client\n\n\nwith Client(client_id="${CLIENT_ID_ENV_VARIABLE}", client_secret="${CLIENT_SECRET_ENV_VARIABLE}") as client:\n    filters = client.FalconFilter()\n    filters.create_new_filter("LastSeen", "-7d", "LTE")\n    response_data = client.hosts.describe_devices(filters)\n\nprint(f"Found {len(response_data)} stale devices")\n\nfor device_id, device_data in response_data.items():\n    hostname = device_data.get("hostname", "Unknown Hostname")\n    print(f"{device_id} - {hostname}")\n```\n\n## Examples Collection\n\nEach API wrapper is provided alongside example code. Cloning or downloading/extracting this repository allows you to execute examples directly.\n\nUsing the examples collection requires that you install our Python packaging tool of choice, [Poetry](https://python-poetry.org). Please refer to the Poetry project\'s [installation guide](https://python-poetry.org/docs/#installation) if you do not yet have Poetry installed.\n\nOnce Poetry is installed, make sure you run `poetry install` within the root repository folder to set up the Python virtual environment.\n\nTo configure the examples, first copy `examples/config.example.yml` to `examples/config.yml`. Then, add your API credentials and example-specific settings to `examples/config.yml`. Once you have set up profiles for each Falcon tenant you want to test with, execute examples using one of the two options below.\n\n### Executing the Examples\n\nThere are two ways to use Poetry to execute the examples.\n\n<details>\n<summary><h4>Executing from a Poetry Shell</h4></summary>\n\nThe `poetry shell` command will enter you into the virtual environment. All future commands will run within the Caracara virtual environment using Python 3, until you run the `deactivate` command.\n\n```shell\npoetry shell\nexamples/get_devices/list_windows_devices.py\n```\n\n</details>\n\n<details>\n<summary><h4>Executing without Activating the Virtual Environment</h4></summary>\n\nIf you do not want to enter the Caracara virtual environment (e.g., because you are using your system\'s installation of Python for other purposes), you can use the `poetry run` command to temporarily invoke the virtual environment for one-off commands.\n\n```shell\npoetry run examples/get_devices/list_windows_devices.py\n```\n\nAll examples are also configured in the `pyproject.toml` file as scripts, allowing them to be executed simply.\n\n```shell\npoetry run stale-sensors\n```\n\n> To get a complete list of available examples, execute the command `util/list-examples.sh` from the root of the repository folder.\n\n</details>\n\n## Documentation\n\n__*Coming soon!*__\n\n## Contributing\n\nInterested in taking part in the development of the Caracara project? Start [here](CONTRIBUTING.md).\n\n## Why Caracara?\n\nSimple! We like birds at CrowdStrike, so what better bird to name a Python project after one that eats just about anything, including snakes :)\n',
    'author': 'CrowdStrike',
    'author_email': 'falconpy@crowdstrike.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
