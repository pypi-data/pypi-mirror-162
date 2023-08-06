# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['certificates']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['certificates = certificates.__main__:main']}

setup_kwargs = {
    'name': 'certificates',
    'version': '1.1.0',
    'description': 'Generate event certificates easily.',
    'long_description': '#  Certificates\n\nGenerate event certificates easily.\n\n## Requirements\n\n* Inkscape (`apt install inkscape`)\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install certificates.\n\n```bash\npip install certificates\n```\n\n## Usage\n\n`certificates participants.csv template.svg`\n\n```\nusage: certificates [-h] [--output OUTPUT] participants template\n\npositional arguments:\n  participants          csv filaname containing participants\n  template              certificate template in svg format used to build\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --output OUTPUT, -o OUTPUT\n                        destination of the generated certificates\n```\n\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## License\n[Apache 2.0](https://choosealicense.com/licenses/apache-2.0/)\n',
    'author': 'cassiobotaro',
    'author_email': 'cassiobotaro@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cassiobotaro/certificates',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
