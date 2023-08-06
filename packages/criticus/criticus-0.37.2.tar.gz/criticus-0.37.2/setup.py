# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['criticus',
 'criticus.py',
 'criticus.py.analyze_collation',
 'criticus.py.cbgm_interface',
 'criticus.py.export_to_docx',
 'criticus.py.md2tei',
 'criticus.py.reformat_collation',
 'criticus.py.serve_tei_transcriptions',
 'criticus.py.tei2json',
 'criticus.py.txt2json',
 'criticus.resources']

package_data = \
{'': ['*']}

install_requires = \
['Markdown==3.2.2',
 'PySimpleGUI>=4.57.0,<5.0.0',
 'lxml>=4.8.0,<5.0.0',
 'markdown-del-ins>=1.0.0,<2.0.0',
 'natsort>=8.1.0,<9.0.0',
 'python-docx>=0.8.11,<0.9.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'criticus',
    'version': '0.37.2',
    'description': 'A suite of tools for transcribing, collating and creating an apparatus criticus.',
    'long_description': '# Criticus\nA suite of tools for transcribing, collating and and creating an apparatus criticus.\n\n## install\nRequires Python 3.8+\n\n### Windows: \n- `pip install criticus`\n- `python -m criticus`\n### MacOS: \n- `pip3 install criticus`\n- `python3 -m criticus`\n\nRead the full [tutorial on GitHub](https://github.com/d-flood/criticus).\n',
    'author': 'David Flood',
    'author_email': 'davidfloodii@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/d-flood/criticus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
