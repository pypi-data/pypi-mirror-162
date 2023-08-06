# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nautobot_golden_config',
 'nautobot_golden_config.api',
 'nautobot_golden_config.management.commands',
 'nautobot_golden_config.migrations',
 'nautobot_golden_config.nornir_plays',
 'nautobot_golden_config.tests',
 'nautobot_golden_config.tests.forms',
 'nautobot_golden_config.tests.test_nornir_plays',
 'nautobot_golden_config.tests.test_utilities',
 'nautobot_golden_config.utilities']

package_data = \
{'': ['*'],
 'nautobot_golden_config': ['static/nautobot_golden_config/diff2html-3.4.13/*',
                            'templates/nautobot_golden_config/*']}

install_requires = \
['deepdiff>=5.5.0,<6.0.0',
 'django-pivot>=1.8.1,<2.0.0',
 'matplotlib>=3.3.2,<4.0.0',
 'nautobot-plugin-nornir>=1.0.0',
 'nautobot>=1.4.0b1']

setup_kwargs = {
    'name': 'nautobot-golden-config',
    'version': '1.2.0b0',
    'description': 'A plugin for configuration on nautobot',
    'long_description': '# Nautobot Golden Config\n\n<p align="center">\n  <img src="https://raw.githubusercontent.com/nautobot/nautobot-plugin-golden-config/develop/docs/images/icon-NautobotGoldenConfig.png" class="logo" height="200px">\n  <br>\n  <a href="https://github.com/nautobot/nautobot-plugin-golden-config/actions"><img src="https://github.com/nautobot/nautobot-plugin-golden-config/actions/workflows/ci.yml/badge.svg?branch=main"></a>\n  <!-- TODO: uncomment after RTD project is up! <a href="https://docs.nautobot.com/projects/golden-config/en/latest/"><img src="https://readthedocs.org/projects/golden-config/badge/"></a> -->\n  <a href="https://pypi.org/project/nautobot-golden-config/"><img src="https://img.shields.io/pypi/v/nautobot-golden-config"></a>\n  <a href="https://pypi.org/project/nautobot-golden-config/"><img src="https://img.shields.io/pypi/dm/nautobot-golden-config"></a>\n  <br>\n  An App for <a href="https://github.com/nautobot/nautobot">Nautobot</a>.\n</p>\n\n## Overview\n\nThe Golden Config plugin is a Nautobot plugin that provides a NetDevOps approach to golden configuration and configuration compliance.\n\n### Key Use Cases\n\nThis plugin enable four (4) key use cases.\n\n1. **Configuration Backups** - Is a Nornir process to connect to devices, optionally parse out lines/secrets, backup the configuration, and save to a Git repository.\n2. **Intended Configuration** - Is a Nornir process to generate configuration based on a Git repo of Jinja files to combine with a GraphQL generated data and a Git repo to store the intended configuration.\n3. **Source of Truth Aggregation** - Is a GraphQL query per device that creates a data structure used in the generation of configuration.\n4. **Configuration Compliance** - Is a process to run comparison of the actual (via backups) and intended (via Jinja file creation) CLI configurations upon saving the actual and intended configuration. This is started by either a Nornir process for cli-like configurations or calling the API for json-like configurations\n\n> Notice: The operators of their own Nautobot instance are welcome to use any combination of these features. Though the appearance may seem like they are tightly coupled, this isn\'t actually the case. For example, one can obtain backup configurations from their current RANCID/Oxidized process and simply provide a Git Repo of the location of the backup configurations, and the compliance process would work the same way. Also, another user may only want to generate configurations, but not want to use other features, which is perfectly fine to do so.\n\n## Screenshots\n\nThere are many features and capabilities the plugin provides into the Nautobot ecosystem. The following screenshots are intended to provide a quick visual overview of some of these features.\n\nThe golden configuration is driven by jobs that run a series of tasks and the result is captured in this overview.\n\n![Overview](https://raw.githubusercontent.com/nautobot/nautobot-plugin-golden-config/develop/docs/images/ss_golden-overview.png)\n\nThe compliance report provides a high-level overview on the compliance of your network.\n![Compliance Report](https://raw.githubusercontent.com/nautobot/nautobot-plugin-golden-config/develop/docs/images/ss_compliance-report.png)\n\nThe compliance overview will provide a per device and feature overview on the compliance of your network devices.\n![Compliance Overview](https://raw.githubusercontent.com/nautobot/nautobot-plugin-golden-config/develop/docs/images/ss_compliance-overview.png)\n\nDrilling into a specific device and feature, you can get an immediate detailed understanding of your device.\n![Compliance Device](https://raw.githubusercontent.com/nautobot/nautobot-plugin-golden-config/develop/docs/images/ss_compliance-device.png)\n\n![Compliance Rule](https://raw.githubusercontent.com/nautobot/nautobot-plugin-golden-config/develop/docs/images/ss_compliance-rule.png)\n\n## Try it out!\n\nThis App is installed in the Nautobot Community Sandbox found over at [demo.nautobot.com](https://demo.nautobot.com/)!\n\n> For a full list of all the available always-on sandbox environments, head over to the main page on [networktocode.com](https://www.networktocode.com/nautobot/sandbox-environments/).\n\n## Documentation\n\nFull web-based HTML documentation for this app can be found over on the [Nautobot Docs](https://docs.nautobot.com/projects/golden-config/en/latest/) website:\n\n- [User Guide](https://docs.nautobot.com/projects/golden-config/en/latest/user/app_overview/) - Overview, Using the App, Getting Started, Navigating compliance (cli, json, custom), backup, app usage, intended state creation.\n- [Administrator Guide](https://docs.nautobot.com/projects/golden-config/en/latest/admin/admin_install/) - How to Install, Configure, Upgrade, or Uninstall the App.\n- [Developer Guide](https://docs.nautobot.com/projects/golden-config/en/latest/dev/dev_contributing/) - Extending the App, Code Reference, Contribution Guide.\n- [Release Notes / Changelog](https://docs.nautobot.com/projects/golden-config/en/latest/admin/release_notes/)\n- [Frequently Asked Questions](https://docs.nautobot.com/projects/golden-config/en/latest/user/app_faq/)\n\n### Contributing to the Docs\n\nYou can find all the Markdown source for the App documentation under the [docs](https://github.com/nautobot/nautobot-plugin-golden-config/tree/develop/docs) folder in this repository. Any PRs with fixes or improvements are very welcome!\n\nProject documentation is generated by [mkdocs](https://www.mkdocs.org/) from the documentation located in the docs folder. A container hosting the docs will be started using the invoke commands (details in the [Development Environment Guide](https://docs.nautobot.com/projects/golden-config/en/latest/dev/dev_environment/)) on [http://localhost:8001](http://localhost:8001), as changes are saved the docs will be automatically reloaded.\n\n## Questions\n\nFor any questions or comments, please check the [FAQ](https://docs.nautobot.com/projects/golden-config/en/latest/user/app_faq/) first. Feel free to also swing by the [Network to Code slack channel](https://networktocode.slack.com/) (channel #nautobot), sign up [here](http://slack.networktocode.com/).\n',
    'author': 'Network to Code, LLC',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nautobot/nautobot-plugin-golden-config',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
