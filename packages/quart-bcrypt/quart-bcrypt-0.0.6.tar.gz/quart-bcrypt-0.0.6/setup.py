# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quart_bcrypt']

package_data = \
{'': ['*']}

install_requires = \
['bcrypt>=3.2.2,<4.0.0', 'quart>=0.18.0,<0.19.0']

setup_kwargs = {
    'name': 'quart-bcrypt',
    'version': '0.0.6',
    'description': 'Quart-Bcrypt is a Quart extension that provides bcrypt hashing utilities for your application.',
    'long_description': '# Quart-Bcrypt\n\n![Quart Bcrypt Logo](logos/logo.png)\n\nQuart-Bcrypt is a Quart extension that provides bcrypt hashing utilities for\nyour application. Orginal code from Flash-Bcrypt, which can be found at\nhttps://github.com/maxcountryman/flask-bcrypt\n\nDue to the recent increased prevelance of powerful hardware, such as modern\nGPUs, hashes have become increasingly easy to crack. A proactive solution to\nthis is to use a hash that was designed to be "de-optimized". Bcrypt is such\na hashing facility; unlike hashing algorithms such as MD5 and SHA1, which are\noptimized for speed, bcrypt is intentionally structured to be slow.\n\nFor sensitive data that must be protected, such as passwords, bcrypt is an\nadvisable choice.\n\n## Installation\n\nInstall the extension with the following command:\n\n    $ pip3 install quart-bcrypt\n\n## Usage\n\nTo use the extension simply import the class wrapper and pass the Quart app\nobject back to here. Do so like this:\n\n    from quart import Quart\n    from quart_bcrypt import Bcrypt\n    \n    app = Quart(__name__)\n    bcrypt = Bcrypt(app)\n\nTwo primary hashing methods are now exposed by way of the bcrypt object. Note that you\nneed to use decode(\'utf-8\') on generate_password_hash().\n\n    pw_hash = bcrypt.generate_password_hash(\'hunter2\').decode(\'utf-8\')\n    bcrypt.check_password_hash(pw_hash, \'hunter2\') # returns True\n\n## Documentation\n\nView documentation at https://quart-bcrypt.readthedocs.io/en/latest/',
    'author': 'Chris Rood',
    'author_email': 'quart.addons@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Quart-Addons/quart-bcrypt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
