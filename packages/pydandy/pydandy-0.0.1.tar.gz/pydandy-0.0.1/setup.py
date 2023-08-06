# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydandy']

package_data = \
{'': ['*']}

install_requires = \
['filelock>=3.7.1,<4.0.0', 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'pydandy',
    'version': '0.0.1',
    'description': 'A handy-dandy datastore built on top of Pydantic',
    'long_description': '# Pydandy\n\nPydandtic + Handy\n\nA lightweight "Database", built on top of [Pydandtic](https://pydantic-docs.helpmanual.io/). It is currently under development, but the intent is to support in-memory, file, and directory storage options and eventually an Async variant. For the file and directory modes, the data will be backed by either one or manyu JSON files. The main database is also meant to provide a slim ORM-like interface for querying the data.\n\n## Examples\n```python\nfrom pydantic import BaseModel\nfrom pydandy import PydandyDB\n\n# Create an in-memory database\ndb = PydandyDB()\n# Add User Model to the database\n\n@db.register()\nclass User(BaseModel):\n    id: int\n    first_name: str\n    last_name: str\n    # You can use any model, as long you provide a __hash__\n    def __hash__(self):\n        return self.id\n\n# Add a new Record to Users\ndb.User.add(\n    User(\n        id=1,\n        first_name="John",\n        last_name="Baz",\n    )\n)\n\n# Get your record back\nuser = db.User.get(1)\n\n# Filter for records\ndb.User.filter(lambda record: record.first_name.startswith("J"))\n```\n\n## Motivation\nMostly just because, but also because I occasionaly finding myself wanting a small data, portable data store. This seemed like fun project idea, and I really Pydandtic, so it worked out.\n\n## Contributing\nAt this stage, I am not accepting contributions. Mostly because I am still trying to shape out the core functionality. However, this should change soon™ if you are interested in helping out.',
    'author': 'Will Johns',
    'author_email': 'will@wcj.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/WilliamJohns/pydandy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
