# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['firedantic',
 'firedantic._async',
 'firedantic._sync',
 'firedantic.tests',
 'firedantic.tests.tests_async',
 'firedantic.tests.tests_sync']

package_data = \
{'': ['*']}

install_requires = \
['google-cloud-firestore>=2.6.0,<3.0.0',
 'grpcio>=1.47.0,<2.0.0',
 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'firedantic',
    'version': '0.3.0',
    'description': 'Pydantic base models for Firestore',
    'long_description': '# Firedantic\n\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/ioxiocom/firedantic/Build%20and%20upload%20to%20PyPI)](https://github.com/ioxiocom/firedantic/actions/workflows/publish.yaml)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PyPI](https://img.shields.io/pypi/v/firedantic)](https://pypi.org/project/firedantic/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/firedantic)](https://pypi.org/project/firedantic/)\n[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)\n\nDatabase models for Firestore using Pydantic base models.\n\n## Installation\n\nThe package is available on PyPI:\n\n```bash\npip install firedantic\n```\n\n## Usage\n\nIn your application you will need to configure the firestore db client and optionally\nthe collection prefix, which by default is empty.\n\n```python\nfrom os import environ\nfrom unittest.mock import Mock\n\nimport google.auth.credentials\nfrom firedantic import configure\nfrom google.cloud.firestore import Client\n\n# Firestore emulator must be running if using locally.\nif environ.get("FIRESTORE_EMULATOR_HOST"):\n    client = Client(\n        project="firedantic-test",\n        credentials=Mock(spec=google.auth.credentials.Credentials)\n    )\nelse:\n    client = Client()\n\nconfigure(client, prefix="firedantic-test-")\n```\n\nOnce that is done, you can start defining your Pydantic models, e.g:\n\n```python\nfrom pydantic import BaseModel\n\nfrom firedantic import Model\n\nclass Owner(BaseModel):\n    """Dummy owner Pydantic model."""\n    first_name: str\n    last_name: str\n\n\nclass Company(Model):\n    """Dummy company Firedantic model."""\n    __collection__ = "companies"\n    company_id: str\n    owner: Owner\n\n# Now you can use the model to save it to Firestore\nowner = Owner(first_name="John", last_name="Doe")\ncompany = Company(company_id="1234567-8", owner=owner)\ncompany.save()\n\n# Prints out the firestore ID of the Company model\nprint(company.id)\n```\n\nQuerying is done via a MongoDB-like `find()`:\n\n```python\nfrom firedantic import Model\nimport firedantic.operators as op\n\nclass Product(Model):\n    __collection__ = "products"\n    product_id: str\n    stock: int\n\n\nProduct.find({"product_id": "abc-123"})\nProduct.find({"stock": {">=": 3}})\n# or\nProduct.find({"stock": {op.GTE: 3}})\n```\n\nThe query operators are found at\n[https://firebase.google.com/docs/firestore/query-data/queries#query_operators](https://firebase.google.com/docs/firestore/query-data/queries#query_operators).\n\n### Async usage\n\nFiredantic can also be used in an async way, like this:\n\n```python\nimport asyncio\nfrom os import environ\nfrom unittest.mock import Mock\n\nimport google.auth.credentials\nfrom google.cloud.firestore import AsyncClient\n\nfrom firedantic import AsyncModel, configure\n\n# Firestore emulator must be running if using locally.\nif environ.get("FIRESTORE_EMULATOR_HOST"):\n    client = AsyncClient(\n        project="firedantic-test",\n        credentials=Mock(spec=google.auth.credentials.Credentials),\n    )\nelse:\n    client = AsyncClient()\n\nconfigure(client, prefix="firedantic-test-")\n\n\nclass Person(AsyncModel):\n    __collection__ = "persons"\n    name: str\n\n\nasync def main():\n    alice = Person(name="Alice")\n    await alice.save()\n    print(f"Saved Alice as {alice.id}")\n    bob = Person(name="Bob")\n    await bob.save()\n    print(f"Saved Bob as {bob.id}")\n\n    found_alice = await Person.find_one({"name": "Alice"})\n    print(f"Found Alice: {found_alice.id}")\n    assert alice.id == found_alice.id\n\n    found_bob = await Person.get_by_id(bob.id)\n    assert bob.id == found_bob.id\n    print(f"Found Bob: {found_bob.id}")\n\n    await alice.delete()\n    print("Deleted Alice")\n    await bob.delete()\n    print("Deleted Bob")\n\n\nif __name__ == "__main__":\n    # Starting from Python 3.7 ->\n    # asyncio.run(main())\n\n    # Compatible with Python 3.6 ->\n    loop = asyncio.get_event_loop()\n    result = loop.run_until_complete(main())\n```\n\n## Subcollections\n\nSubcollections in Firestore are basically dynamically named collections.\n\nFiredantic supports them via the `SubCollection` and `SubModel` classes, by creating\ndynamic classes with collection name determined based on the "parent" class it is in\nreference to using the `model_for()` method.\n\n```python\nfrom typing import Optional, Type\n\nfrom firedantic import AsyncModel, AsyncSubCollection, AsyncSubModel, ModelNotFoundError\n\n\nclass UserStats(AsyncSubModel):\n    id: Optional[str]\n    purchases: int = 0\n\n    class Collection(AsyncSubCollection):\n        # Can use any properties of the "parent" model\n        __collection_tpl__ = "users/{id}/stats"\n\n\nclass User(AsyncModel):\n    __collection__ = "users"\n    name: str\n\n\nasync def get_user_purchases(user_id: str, period: str = "2021") -> int:\n    user = await User.get_by_id(user_id)\n    stats_model: Type[UserStats] = UserStats.model_for(user)\n    try:\n        stats = await stats_model.get_by_id(period)\n    except ModelNotFoundError:\n        stats = stats_model()\n    return stats.purchases\n\n```\n\n## Development\n\nPRs are welcome!\n\nTo run tests locally, you should run:\n\n```bash\npoetry install\npoetry run invoke test\n```\n\n### About sync and async versions of library\n\nAlthough this library provides both sync and async versions of models, please keep in\nmind that you need to explicitly maintain only async version of it. The synchronous\nversion is generated automatically by invoke task:\n\n```bash\npoetry run invoke unasync\n```\n\nWe decided to go this way in order to:\n\n- make sure both versions have the same API\n- reduce human error factor\n- avoid working on two code bases at the same time to reduce maintenance effort\n\nThus, please make sure you don\'t modify any of files under\n[firedantic/\\_sync](./firedantic/_sync) and\n[firedantic/tests/tests_sync](./firedantic/tests/tests_sync) by hands. `unasync` is also\nrunning as part of pre-commit hooks, but in order to run the latest version of tests you\nhave to run it manually.\n\n## License\n\nThis code is released under the BSD 3-Clause license. Details in the\n[LICENSE](./LICENSE) file.\n',
    'author': 'Digital Living International Ltd',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ioxiocom/firedantic',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
