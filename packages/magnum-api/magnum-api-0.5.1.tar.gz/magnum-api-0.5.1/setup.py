# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magnumapi',
 'magnumapi.geometry',
 'magnumapi.geometry.blocks',
 'magnumapi.geometry.definitions',
 'magnumapi.geometry.primitives']

package_data = \
{'': ['*']}

install_requires = \
['Shapely>=1.8.2,<2.0.0',
 'ipyaggrid>=0.2.2,<0.3.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'pymbse-commons>=0.0.6,<0.0.7',
 'roxie-api>=0.0.10,<0.0.11']

setup_kwargs = {
    'name': 'magnum-api',
    'version': '0.5.1',
    'description': '',
    'long_description': '# Project Overview\nThe CHART MagNum (Magnum Numerics) aims at introducing advanced design techniques in order to support the design process of superconducting accelerator magnet.\nThe project responds to the following strategic goals:\n- Sustainability\n\n  Ensure that outstanding modeling work will have an impact on present or future designs. This also require that models have clearly defined scope and range of applicability.\n- Traceability\n\n  Ensure that the modeler is able to trace back the input parameters, code and script versions, etc., that have been used to produce a particular plot in a ppt or pdf.\n  Traceability is even more important in multi-scale and multi-model analysis.\n- Repeatability\n\n  Ensure that results presented at, e.g., a Conceptual Design Review can be reproduced at any later time.\n  Ensure that as-built models can be re-run at any moment during a potentially decades-long project life cycle.\n- Flexibility\n\n  Allow for different labs and collaborators to have/prefer different licenses.\n  Enable researchers to implement innovative ideas while building upon existing best practices, but without having to solve legacy issues.\n- Usability\n\n  Encapsulate the increased flexibility behind easy-to-use UIs for the standard design work.\n\nThe project implements a number of concepts introduced by the MBSE (Model-Based System Engineering) methdology.\nIn particular, MBSE shifts the focus from documents to models as primary means of communication in complex system design projects.\n',
    'author': 'mmaciejewski',
    'author_email': 'michal.maciejewski@ief.ee.ethz.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.cern.ch/chart-magnum/magnum-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
