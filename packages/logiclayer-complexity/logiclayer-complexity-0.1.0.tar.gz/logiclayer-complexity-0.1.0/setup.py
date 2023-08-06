# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['logiclayer_complexity']

package_data = \
{'': ['*']}

install_requires = \
['economic-complexity>=0.1.0,<0.2.0',
 'logiclayer>=0.2.0,<0.3.0',
 'tesseract-olap>=0.2.0,<0.3.0']

setup_kwargs = {
    'name': 'logiclayer-complexity',
    'version': '0.1.0',
    'description': '',
    'long_description': '<p>\n<a href="https://github.com/Datawheel/logiclayer-complexity/releases"><img src="https://flat.badgen.net/github/release/Datawheel/logiclayer-complexity" /></a>\n<a href="https://github.com/Datawheel/logiclayer-complexity/blob/master/LICENSE"><img src="https://flat.badgen.net/github/license/Datawheel/logiclayer-complexity" /></a>\n<a href="https://github.com/Datawheel/logiclayer-complexity/"><img src="https://flat.badgen.net/github/checks/Datawheel/logiclayer-complexity" /></a>\n<a href="https://github.com/Datawheel/logiclayer-complexity/issues"><img src="https://flat.badgen.net/github/issues/Datawheel/logiclayer-complexity" /></a>\n</p>\n\n## Getting started\n\nThis module must be used with LogicLayer. An instance of `OlapServer` from the `tesseract_olap` package is also required to retrieve the data.\n\n```python\n# app.py\n\nfrom logiclayer import LogicLayer\nfrom logiclayer_complexity import EconomicComplexityModule\nfrom tesseract_olap import OlapServer\nfrom tesseract_olap.logiclayer import TesseractModule\n\nlayer = LogicLayer()\nolap = OlapServer(backend="clickhouse://...", schema="./schema/")\n\ncmplx = EconomicComplexityModule(olap)\nlayer.add_module("/complexity", cmplx)\n\n# You can reuse the `olap` object with an instace of `TesseractModule`\ntsrc = TesseractModule(olap)\nlayer.add_module("/tesseract", tsrc)\n```\n\nYou can also use the module with a FastAPI instance:\n\n```python\ncmplx = EconomicComplexityModule(olap)\n\napp = FastAPI()\napp.include_router(cmplx.router, prefix="/complexity")\n```\n\n---\n&copy; 2022 [Datawheel, LLC.](https://www.datawheel.us/)  \nThis project is licensed under [MIT](./LICENSE).\n',
    'author': 'Miguel Castillo',
    'author_email': 'miguel@datawheel.us',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Datawheel/logiclayer-complexity',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
