# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['inspection', 'inspection.handlers']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=4.1.0,<5.0.0']

setup_kwargs = {
    'name': 'inspection',
    'version': '1.1.0',
    'description': 'A runtime checker for modern TypedDicts',
    'long_description': '# inspection\n\nA runtime checker for modern TypedDicts\n\n## Supported Typings\n\n- `Any`\n- `dict`\n- `Dict`\n- `List`\n- `list`\n- `Literal`\n- `NotRequired`\n- `None`\n- `Optional`\n- `T | ...`\n- `TypedDict`\n- `Union`\n- `str` (and all other normal classes)\n\n## How To Use\n\n### Install\n\n```bash\npip install inspection\n# or\npoetry add inspection\n```\n\n### Add To Code\n\n```py\nfrom typing import Any, Optional, TypedDict\n\nfrom typing_extensions import NotRequired\n\nfrom inspection import check_hints\n\n\nclass MyCoolType(TypedDict):\n    anything: NotRequired[You]\n    want: Optional[Really]\n    this: IsJust | An | Example\n\n\ndef function(not_verified_dict: Any) -> MyCoolType:\n    return check_hints(MyCoolType, not_verified_dict)\n```\n',
    'author': 'ooliver1',
    'author_email': 'oliverwilkes2006@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ooliver1/inspection',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
