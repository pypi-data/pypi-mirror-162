# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fenkeysmanagement']

package_data = \
{'': ['*']}

install_requires = \
['tabulate>=0.8.10,<0.9.0']

entry_points = \
{'console_scripts': ['fenkm = fenkeysmanagement:main']}

setup_kwargs = {
    'name': 'fenkeysmanagement',
    'version': '1.0.1',
    'description': 'Simple key management. Generate tokens for any usage.',
    'long_description': '# FenKeysManagement\n\nSimple key management. Generate tokens for any usage.\n\nFenKeysManagement is a simple tool for manage and generate tokens that can be\nused in different applications. Like for example a flask API.\n\n## Usage\n\n### Key management\n\nFor managing your keyfile you have a command `fenkm` where you can add, see and revoke tokens.\n\n```\nusage: fenkm [-h] [genkey ...] [revokekey ...] [listkeys ...]\n\nSimple key management. Generate tokens for any usage.\n\npositional arguments:\n  genkey      Generate a new key. Optional argument comment in the format comment=<comment>\n  revokekey   Revoke a key. The format should be <key>=<value> where <key> cant be the id or the key directly\n  listkeys    List all the key available\n\noptions:\n  -h, --help  show this help message and exit\n```\n### Module usage\n\nAs an example, here is a snippet of how I use this in some flask applications.\nThis is not a working flask application, don\'t copy past without understanding it.\n\n```\nimport json\n\nfrom fenkeysmanagement import KeyManager\n\n# ... more imports and flask related code\n\nkey_manager = KeyManager()\n\n# .. more flask related code\n\ndef check_perms(request):\n    data_str = request.data.decode(\'utf-8\')\n    try:\n        data_json = json.loads(data_str)\n        if "auth_key" in data_json.keys():\n            key_manager.reload_keys()\n            if not key_manager.key_revoked(data_json[\'auth_key\']):\n                return True\n        return False\n    except json.decoder.JSONDecodeError:\n        return False\n\n# ... more flask related code\n\n@app.route("/", methods=["POST"])\ndef home():\n    if not check_perms(request):\n        # ... code for handle the failed auth verification\n    # ... code for handle the real request after correct auth verification\n\n# ... more flask related code\n\n```\n',
    'author': 'brodokk',
    'author_email': 'brodokk@brodokk.space',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/brodokk/FenKeysManagement',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
