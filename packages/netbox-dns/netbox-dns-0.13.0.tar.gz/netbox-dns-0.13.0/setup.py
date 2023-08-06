# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netbox_dns',
 'netbox_dns.api',
 'netbox_dns.filters',
 'netbox_dns.forms',
 'netbox_dns.graphql',
 'netbox_dns.management',
 'netbox_dns.management.commands',
 'netbox_dns.migrations',
 'netbox_dns.tables',
 'netbox_dns.templatetags',
 'netbox_dns.views']

package_data = \
{'': ['*'], 'netbox_dns': ['templates/netbox_dns/*']}

install_requires = \
['dnspython>=2.2.1,<3.0.0']

setup_kwargs = {
    'name': 'netbox-dns',
    'version': '0.13.0',
    'description': 'Netbox Dns is a netbox plugin for managing zone, nameserver and record inventory.',
    'long_description': '<h1 align="center">NetBox DNS</h1>\n\n<p align="center"><i>NetBox DNS is a NetBox plugin for managing DNS data.</i></p>\n\n<div align="center">\n<a href="https://pypi.org/project/netbox-dns/"><img src="https://img.shields.io/pypi/v/netbox-dns" alt="PyPi"/></a>\n<a href="https://github.com/auroraresearchlab/netbox-dns/stargazers"><img src="https://img.shields.io/github/stars/auroraresearchlab/netbox-dns" alt="Stars Badge"/></a>\n<a href="https://github.com/auroraresearchlab/netbox-dns/network/members"><img src="https://img.shields.io/github/forks/auroraresearchlab/netbox-dns" alt="Forks Badge"/></a>\n<a href="https://github.com/auroraresearchlab/netbox-dns/pulls"><img src="https://img.shields.io/github/issues-pr/auroraresearchlab/netbox-dns" alt="Pull Requests Badge"/></a>\n<a href="https://github.com/auroraresearchlab/netbox-dns/issues"><img src="https://img.shields.io/github/issues/auroraresearchlab/netbox-dns" alt="Issues Badge"/></a>\n<a href="https://github.com/auroraresearchlab/netbox-dns/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/auroraresearchlab/netbox-dns?color=2b9348"></a>\n<a href="https://github.com/auroraresearchlab/netbox-dns/blob/master/LICENSE"><img src="https://img.shields.io/github/license/auroraresearchlab/netbox-dns?color=2b9348" alt="License Badge"/></a>\n</div>\n\n## Features\n\n* Manage name servers\n* Manage DNS zone information, automatically generating SOA and NS records\n* Automatically create and update PTR records for A and AAAA records\n* Optionally organize zones in views to cater for split horizon DNS and multi site deployments\n\nNetBox DNS is using the standardized NetBox plugin interface, so it also takes advantage of the NetBox tagging and change log features.\n\n## Requirements\n\n* NetBox 3.2 or higher\n* Python 3.8 or higher\n\n## Installation & Configuration\n\n### Installation\n\n```\n$ source /opt/netbox/venv/bin/activate\n(venv) $ pip install netbox-dns\n```\n\n### Configuration\n\nAdd the plugin to the NetBox config. `~/netbox/configuration.py`\n\n```python\nPLUGINS = [\n    "netbox_dns",\n]\n```\n\nTo permanently mount the plugin when updating NetBox:\n\n```\necho netbox-dns >> ~/netbox/local_requirements.txt\n```\n\nTo add the required netbox_dns tables to your database run the following command from your NetBox directory:\n\n```\n./manage.py migrate\n```\n\nFull reference: [Using Plugins - NetBox Documentation](https://netbox.readthedocs.io/en/stable/plugins/)\n\n## Screenshots\n\n![Zones](https://raw.githubusercontent.com/auroraresearchlab/netbox-dns/main/docs/images/ZoneList.png)\n\n![Zone Detail](https://raw.githubusercontent.com/auroraresearchlab/netbox-dns/main/docs/images/ZoneDetail.png)\n\n![Records](https://raw.githubusercontent.com/auroraresearchlab/netbox-dns/main/docs/images/RecordList.png)\n\n![Record Detail](https://raw.githubusercontent.com/auroraresearchlab/netbox-dns/main/docs/images/RecordDetail.png)\n\n## Contribute\n\nContributions are always welcome! Please see: [contributing guide](CONTRIBUTING.md)\n\n## License\n\nMIT\n',
    'author': 'Aurora Research Lab',
    'author_email': 'info@auroraresearchlab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/auroraresearchlab/netbox-dns',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
