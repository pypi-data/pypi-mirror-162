# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vamas']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'vamas',
    'version': '0.1.0',
    'description': 'Python package to read vamas (.vms) files',
    'long_description': "vamas\n=====\n\nThis is a Python library to read `VAMAS`_ files (.vms). [1]_\n\n.. _`VAMAS`: https://doi.org/10.1002/sia.740130202\n\n\nInstalling\n----------\n\nInstallation via `pip`_:\n\n.. code-block:: bash\n\n    $ pip install vamas\n\n.. _pip: https://pip.pypa.io/en/stable/\n\n\nExample Usage\n-------------\n\n.. code-block:: python\n    \n  from vamas import Vamas\n\n\n  vamas_data = Vamas('path/to/vamas-file.vms')\n\n\nThe created object has two attributes, ``header`` and ``blocks``, which are\ninstances of ``VamasHeader`` and a list of ``VamasBlock``, respectively.\nSee the `documentation`_ for all attributes of those classes.\n\n.. _`documentation`: https://matkrin.github.io/vamas\n\n|\n\n----\n\n.. [1] W. A. Dench, L. B. Hazell, M. P. Seah, *Surf. Interface Anal.* **1988**,\n  *13*, 63-122.\n  `<https://doi.org/10.1002/sia.740130202>`_\n",
    'author': 'Matthias Krinninger',
    'author_email': 'matkrin@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/matkrin/vamas',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
