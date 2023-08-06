# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_dtn7']

package_data = \
{'': ['*']}

install_requires = \
['cbor2>=5.4.3,<6.0.0',
 'requests>=2.27.1,<3.0.0',
 'websocket-client>=1.3.2,<2.0.0']

setup_kwargs = {
    'name': 'py-dtn7',
    'version': '0.2.1a2',
    'description': '',
    'long_description': '# py-dtn7 (Work in Progress -- don\'t use yet)\n\n[![Licence AGPL-3.0](https://img.shields.io/github/license/teschmitt/py-dtn7)](LICENSE)\n\nA Python library for the DTN7 REST and WebSocket API of [dtn7-rs](https://github.com/dtn7/dtn7-rs)\nincluding a BP7 style `Bundle` type (sort of).\n\n\n### Be warned:\n\nThis is very much a work-in-progress.\nApart from not being very useful yet, anything might change at any time\nsince the package is still under development and the requirements are not all\ncompletely clear yet.\n\n### PR Politics\n\nI\'m sorry to say that right now I can\'t accept any Pull Requests, since this repo is part\nof my Bachelor Thesis and logically any external contribution is forbidden. If you want to\ncontribute, please check back around November 2022. Until then feel free to\nfork this repo and do some of your own experiments.\n\n## Quickstart\n\n```pycon\n>>> from py_dtn7 import DTNRESTClient\n>>> client = DTNRESTClient(host="http://localhost", port=3000)\n>>> d.peers\n{\'box1\': {\'eid\': [1, \'//box1/\'], \'addr\': {\'Ip\': \'10.0.0.42\'}, \'con_type\': \'Dynamic\', \'period\': None, \'cla_list\': [[\'MtcpConvergenceLayer\', 16162]], \'services\': {}, \'last_contact\': 1653316457}}\n>>> d.info\n{\'incoming\': 0, \'dups\': 0, \'outgoing\': 0, \'delivered\': 3, \'broken\': 0}\n```\n\nWhen sending a bundle to a known peer, we can simply supply the peer name and endpoint,\notherwise we use the complete URI:\n\n```pycon\n>>> d.send(payload={"body": "This will be transferred as json"}, peer_name="box1", endpoint="info")\n<Response [200]>\n>>> r = d.send(payload="Is there anybody out there?", destination="dtn://greatunkown/incoming")\n>>> r.content.decode("utf-8")\n\'Sent payload with 27 bytes\'\n```\n\n## Documentation\n\nUse `pdoc` to generate the API docs or check out [py-dtn7.readthedocs.org](https://py-dtn7.readthedocs.org)\n',
    'author': 'Thomas Schmitt',
    'author_email': 't.e.schmitt@posteo.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/teschmitt/py-dtn7',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
