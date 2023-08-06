# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asciiplot',
 'asciiplot._chart',
 'asciiplot._chart.grid',
 'asciiplot._chart.serialized',
 'asciiplot._utils']

package_data = \
{'': ['*']}

install_requires = \
['colored==1.4.2', 'dataclasses', 'more-itertools']

setup_kwargs = {
    'name': 'asciiplot',
    'version': '0.1.6',
    'description': 'Platform-agnostic, highly customizable sequence plotting in console',
    'long_description': "# __asciiplot__\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/asciiplot)\n[![Build](https://github.com/w2sv/asciiplot/actions/workflows/build.yaml/badge.svg)](https://github.com/w2sv/asciiplot/actions/workflows/build.yaml)\n[![codecov](https://codecov.io/gh/w2sv/asciiplot/branch/master/graph/badge.svg?token=69Q1VL8IHI)](https://codecov.io/gh/w2sv/asciiplot)\n[![PyPI](https://img.shields.io/pypi/v/asciiplot)](https://pypi.org/project/asciiplot)\n![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/w2sv/asciiplot)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/asciiplot)\n[![GitHub](https://img.shields.io/github/license/w2sv/asciiplot?style=plastic)](https://github.com/w2sv/asciiplot/blob/master/LICENSE)\n\n#### Platform-agnostic, highly customizable sequence plotting in console\n\n## Installation\n```shell\n$pip install asciiplot\n```\n\n## Plot Appearance Configuration Options\n\nSet:\n- chart height & title\n- the color of virtually all chart components and areas, picked from a wide array of shades due to the integration of [colored](https://pypi.org/project/colored/)\n- consistent margin between consecutive data points to widen your chart\n- the chart indentation within its hosting terminal, or whether it ought to be centered in it, respectively\n- axes descriptions\n- x-axis tick labels, which may be set to contain strings instead of just numeric values\n- y-axis tick label decimal places\n\n## Usage Examples\n\n```python\nfrom asciiplot import asciiize, Color\n\n\nprint(\n    asciiize(\n        [1, 1, 2, 3, 5, 8, 13, 21],\n        sequence_colors=[Color.BLUE_3B],\n        height=21,\n        inter_points_margin=5,\n        background_color=Color.LIGHT_SALMON_1,\n        label_color=Color.BLUE_VIOLET,\n        axes_background_color=Color.DEEP_PINK_3A,\n        title='Fibonacci',\n        title_color=Color.RED_1,\n        x_axis_description='x',\n        y_axis_description='y',\n        center_horizontally=True\n    )\n)\n```\n![alt text](https://github.com/w2sv/asciiplot/blob/master/readme-images/fibonacci.png?raw=true)\n\n```python\nfrom asciiplot import asciiize, Color\n\n\nprint(\n    asciiize(\n        [17, 21, 19, 19, 5, 7, 12, 4],\n        [7, 8, 3, 17, 19, 18, 5, 2, 20],\n        sequence_colors=[Color.RED, Color.BLUE_VIOLET],\n        inter_points_margin=5,\n        height=20,\n        background_color=Color.GREY_7,\n        title='Random Sequences',\n        title_color=Color.MEDIUM_PURPLE,\n        label_color=Color.MEDIUM_PURPLE,\n        x_axis_description='x',\n        y_axis_description='y',\n        center_horizontally=True\n    )\n)\n```\n![alt text](https://github.com/w2sv/asciiplot/blob/master/readme-images/random.png?raw=true)\n\n## Acknowledgements\nCore sequence asciiization algorithm adopted from https://github.com/kroitor/asciichart/blob/master/asciichartpy/\n\n## Testing\n\n```shell\ngit clone https://github.com/w2sv/asciiplot.git\ncd asciiplot\npoetry install\nmake test  # runs mypy, pytest doctest and outputs test coverage\n```\n\n## License\n[MIT License](https://github.com/w2sv/asciiplot/blob/master/LICENSE)\n",
    'author': 'w2sv',
    'author_email': 'zangenbergjanek@googlemail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/w2sv/asciiplot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
