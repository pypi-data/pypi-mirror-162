# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sendsmtp']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['sendsmtp = sendsmtp.__main__:main']}

setup_kwargs = {
    'name': 'sendsmtp',
    'version': '1.0.0',
    'description': 'CLI SMTP client in pure Python',
    'long_description': '########\nsendsmtp\n########\n\nCLI SMTP client in pure Python.\n\nInstallation:\n\n.. code:: console\n\n   python3 -m pip install --user --upgrade sendsmtp\n\nUsage:\n\n.. code:: console\n\n   $ sendsmtp --help\n    usage: sendsmtp [-h] [-m MESSAGE] [-i INPUT] [-p PORT] [-u USERNAME] [--password PASSWORD] [-t] [-c CC] [-b BCC] [-s SUBJECT] HOST FROM TO\n\n    CLI SMTP client in pure Python\n\n    positional arguments:\n      HOST                  Host to connect via SMTP.\n      FROM                  Sender email.\n      TO                    Recipient email(s), comma separated.\n\n    options:\n      -h, --help            show this help message and exit\n      -m MESSAGE, --message MESSAGE\n                            Message to send.\n      -i INPUT, --input INPUT\n                            Path to file to read message contents.\n      -p PORT, --port PORT  Port to connect via SMTP.\n      -u USERNAME, --username USERNAME\n                            Username for login.\n      --password PASSWORD   Password for login.\n      -t, --tls             Flag to use TLS.\n      -c CC, --cc CC        Recipient address(es) to send copy to, comma separated.\n      -b BCC, --bcc BCC     Recipient address(es) to send blind copy to, comma separated.\n      -s SUBJECT, --subject SUBJECT\n                            Message subject.\n',
    'author': 'Ivan Fedorov',
    'author_email': 'inbox@titaniumhocker.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TitaniumHocker/sendsmtp',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
