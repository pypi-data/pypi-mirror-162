# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mtb', 'mtb.log']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mtb-log',
    'version': '0.5.0',
    'description': 'Logging utilities',
    'long_description': "# mtb.log\n\n© Mel Massadian 2017-2022\n\nLogging utilities\n\n## Usage with Poetry\n\nFor now there is no plan to settle anything in this library so it's meant to be used as a dev package:\n\n``` bash\n# public\npoetry add git+ssh://git@gitlab.com:mtb-libs/mtb_log.git\n# private\npoetry add git+ssh://git@gitlab.com/mtb-libs/mtb_log.git\n```\n\n### USED IN\n\n- Houdini Preferences (17.5 | 18 | 18.5)\n- mtb_houdini\n- mtb_hou_io\n- mtb_maya (almost abandoned...)\n- blender_builder\n",
    'author': 'Mel Massadian',
    'author_email': 'melmassadian@gmail.com',
    'maintainer': 'Mel Massadian',
    'maintainer_email': 'melmassadian@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.2,<3.10',
}


setup(**setup_kwargs)
