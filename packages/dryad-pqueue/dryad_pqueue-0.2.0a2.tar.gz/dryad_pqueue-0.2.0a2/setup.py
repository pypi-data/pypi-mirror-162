# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['callback_handlers', 'callback_handlers.image_combiner']

package_data = \
{'': ['*']}

modules = \
['pqueue', 'config', 'callback_defs', 'callback_runner']
install_requires = \
['Pillow>=9.2.0,<10.0.0', 'psycopg[binary,pool]>=3.0.10', 'requests>=2.28.1']

setup_kwargs = {
    'name': 'dryad-pqueue',
    'version': '0.2.0a2',
    'description': 'run models with parameters from a queue and upload to s3 + webhooks',
    'long_description': 'inherit from Maestro and override `create_generator` and/or `handle_item`\n\nsecrets:\n- `DATABASE_URL`\n- `SUPABASE_API_KEY` \n\noptions:\n- `MODEL`\n- `SUPABASE_URL`\n- `ADMIN_URL`\n\nflags:\n- `FREE`\n- `EXIT`\n- `EXIT_ON_LOAD`\n- `POWEROFF`\n- `TWITTER`: post tweets, requires comma-seperated TWITTER_CREDS and TwitterAPI to be installed\n',
    'author': 'technillogue',
    'author_email': 'technillogue@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4',
}


setup(**setup_kwargs)
