# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ky3m', 'ky3m.common', 'ky3m.services']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.10,<0.11']

setup_kwargs = {
    'name': 'ky3m',
    'version': '0.1.1',
    'description': 'Minecraft Mod Manager by Leon "Procybit" Shepelev',
    'long_description': '[](https://github.com/Procybit/Ky3M)\n\n[![GitHub Repo stars](https://img.shields.io/github/stars/Procybit/Ky3M?style=social)](https://github.com/Procybit/Ky3M)\n\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/ky3m?style=for-the-badge)](https://pypi.org/project/ky3m/)\n\n[![GitHub](https://img.shields.io/github/license/Procybit/Ky3M?style=for-the-badge)](LICENSE)\n\n[![GitHub contributors](https://img.shields.io/github/contributors/Procybit/Ky3M?style=for-the-badge)](https://github.com/Procybit/Ky3M) [![GitHub commit activity](https://img.shields.io/github/commit-activity/w/Procybit/Ky3M?style=for-the-badge)](https://github.com/Procybit/Ky3M) [![GitHub issues](https://img.shields.io/github/issues-raw/Procybit/Ky3M?style=for-the-badge)](https://github.com/Procybit/Ky3M)\n\n# Ky3M\n\nMinecraft Mod Manager by Leon "Procybit" Shepelev\n\n## Installing\n\nVia pip or any other PyPI package manager:\n\n```\npython -m pip install ky3m\n```\n\n**Make sure you have Python 3.10 or above installed!**\n\n## Program launch\n\nVia terminal:\n\n```\npython -m ky3m\n```\n\n## Using the CLI\n\nIf the program is run correctly, this should be in the terminal:\n```\nKy3M :>\n```\nAt the moment, the only thing that can be entered into the CLI is methods.\n\nMethods are simple commands that work directly with Ky3M internals.\n\nThe name of the method is written in CAPITAL LETTERS, the specification fields of the method are written with spaces:\n\n```\nKy3M :> METHOD Field_1 Field_2 ANoTheR--fiEld00;[-+^ 4thFIELD\nSomething happened...\n```\n\nIf the method name starts with the "adv" prefix, then the associated log will be displayed:\n\n```\nKy3M :> advMETHOD Field_1 Field_2 ANoTheR--fiEld00;[-+^ 4thFIELD\nSomething happened...\n\nLog intercepted!\n[ky3m.methods] METHOD started!\n[ky3m.something] Something happened! (something: True)\n[ky3m.methods] METHOD ended!\n```\n\n## Methods\n\n### INSPECT\n\nOutputs all .jar files names from Minecraft mods folder.\n\nASSIGNS A UNIQUE ID TO EACH NEWLY OUTPUT FILE.\n\n### PEER `id`\n\nOutputs information about certain .jar file in Minecraft mods folder.\n\nUses `id`  assigned by *INSPECT*\n\n### EXPEL `id`\n\nPermanently deletes certain .jar file from Minecraft mods folder.\n\nUses `id` assigned by *INSPECT*\n\n### ADOPT `id`\n\nCopies certain .jar file from Minecraft mods folder to local library.\n\nUses `id` assigned by *INSPECT*\n\nCAN INTERRUPT CLI AND REQUEST NAME OF SAVED FILE IF NEEDED.\n\nDOESN\'T DELETE CERTAIN FILE.\n\nASSIGNS A UNIQUE ID TO EACH SAVED FILE.\n\n### ADOPTS\n\nOutputs all saved .jar files names from local library.\n\n### RELEASE `id`\n\nCopies certain .jar file from local library to Minecraft mods folder.\n\nUses `id` assigned by *ADOPT*\n\n### PUNISH `id`\n\nPermanently deletes certain .jar file from local library.\n\nUses `id` assigned by *ADOPT*\n\n## License\nThis project follows MIT license. (see [LICENSE](LICENSE))\n',
    'author': 'Leon "Procybit" Shepelev',
    'author_email': 'kyleusnaff@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Procybit/Ky3M',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
