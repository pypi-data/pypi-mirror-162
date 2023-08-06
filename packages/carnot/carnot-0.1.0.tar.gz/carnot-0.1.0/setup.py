# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['carnot']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=4.3.0,<5.0.0']

setup_kwargs = {
    'name': 'carnot',
    'version': '0.1.0',
    'description': 'Module for defining reversible transactions.',
    'long_description': '# carnot\n\n`carnot` is a module that enables reversible transactions for general purposes. Reversible transactions may make your codes simpler and have better readability inspite of complicated logics.\n\n## Installing\n\n- Python >= 3.8\n\n```\npython -m pip install carnot\n```\n\n## Usage\n\n```python\nfrom carnot import reversible_function, transaction\n\ncount = 0\n\n@reverse_function\ndef add(num: int) -> None:\n    global count\n    count += num\n    add.set_args(num)\n\n@add.backward\ndef _add(num: int) -> None:\n    global count\n    count -= num\n\n@transaction\ndef add_and_emit_error() -> None:\n    add(2)\n    raise Exception\n\nif __name__ == "__main__":\n    try:\n        add_and_emit_error()\n    except:\n        pass\n    finally:\n        print(count)    # 0\n```\n',
    'author': 'jjj999',
    'author_email': 'jjj999to@gmail.com',
    'maintainer': 'jjj999',
    'maintainer_email': 'jjj999to@gmail.com',
    'url': 'https://jjj999.github.io/carnot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
