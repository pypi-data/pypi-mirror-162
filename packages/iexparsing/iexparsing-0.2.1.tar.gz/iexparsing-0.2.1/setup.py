# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iexparsing']

package_data = \
{'': ['*']}

install_requires = \
['deprecation>=2.1.0,<3.0.0']

setup_kwargs = {
    'name': 'iexparsing',
    'version': '0.2.1',
    'description': 'Parse IEX market data streams',
    'long_description': "# iexparsing\nA collection of parsers for [IEX](https://exchange.iex.io/).\n\nUse the parsers to gather relevant quotes and trades information. \n\nCurrently, only IEX-TP and TOPS parsing is supported.\n\n## IEX-TP Parsing Example\n\n```py\nfrom iexparsing import iextp\n\nsession = iextp.Session()\n\noutbound_segment = session.decode_packet(b'\\x01\\x00\\xFF\\xFF\\x01\\x00\\x00\\x00\\x00\\x00\\x87\\x42\\x07\\x00\\x02\\x00\\x8c\\xa6\\x21\\x00\\x00\\x00\\x00\\x00\\xca\\xc3\\x00\\x00\\x00\\x00\\x00\\x00\\xec\\x45\\xc2\\x20\\x96\\x86\\x6d\\x14\\x01\\x00\\x69\\x02\\x00\\xBE\\xEF')\nprint(outbound_segment)\n```\n\n```\nIEX-TP outbound segment: [b'i', b'\\xbe\\xef']\n```\n\nYou can then pass `outbound_segment.messages` to a messages-protocol parser, e.g. TOPS.\n\n## TOPS Parsing Example\n\n```py\nfrom iexparsing import tops\n\nsession = tops.Session()\n    \nprint(session.decode_message(b'\\x51\\x00\\xac\\x63\\xc0\\x20\\x96\\x86\\x6d\\x14\\x5a\\x49\\x45\\x58\\x54\\x20\\x20\\x20\\xe4\\x25\\x00\\x00\\x24\\x1d\\x0f\\x00\\x00\\x00\\x00\\x00\\xec\\x1d\\x0f\\x00\\x00\\x00\\x00\\x00\\xe8\\x03\\x00\\x00'))\n```\n\n```\nbest bid: 9700 ZIEXT shares for 99.05 USD; best ask: 1000 ones for 99.07 USD @ 2016-08-23 19:30:32.572716\n```\n\n## TODO\n\n- [x] Make a basic parser\n- [x] Write documentation\n- [ ] Report errors\n- [ ] Add a DEEP parser\n- [ ] Parse trading breaks\n",
    'author': 'Amit Goren',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mmatamm/iexparsing',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
