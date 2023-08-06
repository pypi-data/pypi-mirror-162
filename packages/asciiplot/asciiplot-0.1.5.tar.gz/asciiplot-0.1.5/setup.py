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
    'version': '0.1.5',
    'description': 'Platform-agnostic, customizable sequence plotting in console, offering high GUI suitability',
    'long_description': "# __asciiplot__\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/asciiplot)\n[![Build](https://github.com/w2sv/asciiplot/actions/workflows/build.yaml/badge.svg)](https://github.com/w2sv/asciiplot/actions/workflows/build.yaml)\n[![codecov](https://codecov.io/gh/w2sv/asciiplot/branch/master/graph/badge.svg?token=69Q1VL8IHI)](https://codecov.io/gh/w2sv/asciiplot)\n[![PyPI](https://img.shields.io/pypi/v/asciiplot)](https://pypi.org/project/asciiplot)\n![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/w2sv/asciiplot)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/asciiplot)\n[![GitHub](https://img.shields.io/github/license/w2sv/asciiplot?style=plastic)](https://github.com/w2sv/asciiplot/blob/master/LICENSE)\n\n#### Platform-agnostic sequence plotting in console, offering various chart appearance configuration options giving rise to an increased GUI suitability\n\n## Installation\n```shell\n$pip install asciiplot\n```\n\n## Plot Appearance Configuration Options\n\nSet:\n- chart height & title\n- axes descriptions & tick labels, including the possibility to determine the number of decimal points for float labels\n- the color of virtually all chart components, picked from a wide array of shades due to the integration of [colored](https://pypi.org/project/colored/)\n- consistent margin between consecutive data points to widen your charts\n- the chart indentation within its hosting terminal, or whether it ought to be centered in it, respectively\n\n## Usage Examples\n\n```python\nfrom asciiplot import asciiize\n\n\nprint(\n    asciiize(\n        [1, 1, 2, 3, 5, 8, 13, 21],\n\n        height=15,\n        inter_points_margin=7,\n\n        x_axis_tick_labels=list(range(1, 9)),\n        y_axis_tick_label_decimal_places=0,\n\n        x_axis_description='Iteration',\n        y_axis_description='Value',\n\n        title='Fibonacci Sequence',\n        horizontal_indentation=6\n    )\n)\n```\n\n                        Fibonacci Sequence\n     Value\n      21┤                                                     ╭──\n      19┤                                                    ╭╯\n      18┤                                                   ╭╯\n      16┤                                                  ╭╯\n      15┤                                                ╭─╯\n      13┤                                              ╭─╯\n      12┤                                            ╭─╯\n      11┤                                          ╭─╯\n       9┤                                        ╭─╯\n       8┤                                     ╭──╯\n       6┤                                 ╭───╯\n       5┤                             ╭───╯\n       3┤                       ╭─────╯\n       2┤             ╭─────────╯\n       1┼───────┬─────╯─┬───────┬───────┬───────┬───────┬───────┬ Iteration\n        1       2       3       4       5       6       7       8\n\n```python\nimport numpy as np\nfrom asciiplot import asciiize\n\n\nprint(\n    asciiize(\n        np.random.randint(-100, 100, 30),\n        np.random.randint(-100, 100, 30),\n\n        height=10,\n        inter_points_margin=2,\n\n        x_axis_tick_labels=list(range(1, 31)),\n        y_axis_tick_label_decimal_places=1,\n\n        title='Random Values',\n        horizontal_indentation=6\n    )\n)\n```\n\n                                             Random Values\n        96.0┤        ╭╮    ╭──╭╮──╮               ╭──╮   ╭╮       ╭╮    ╭╮          ╭───────╮  ╭─╮\n        74.2┤  ╭╮    ││    │  ││  │               │  ╰╮ ╭╯│      ╭╯│   ╭╯╰╮        ╭╯──╯│   ╰╮╭╯ │\n        52.4┤ ╭╭╮╮  ╭╯╰╮  ╭╯ ╭╯│  ╰╮   ╭╮    ╭──╮╭╯   │╭╯ ╰╮   ╭─╯ ╰╮╭╮│  │       ╭╯│   │    ╰╯  ╰╮\n        30.7┤╭╯│╰╮╮╭╯  │  │  │ ╰╮  │   ││   ╭╯  ╰╯    ╰╯   │   │    ││││  ╰╮     ╭╯╭╯   ╰╮        │\n         8.9┼╯╭╯ │╰╯   │ ╭╯  │  │  │   ╭╮╮  │╭╮            ╰╮ ╭╯    ╭╯╰╮   │     │╭╯     │        │\n       -12.9┤╭╯  ╰╮    ╰╮│  ╭╯  │  │ ╭─╯╰╮╮╭╭╯│             │╭╯    ╭╯│││   ╭╮╮  ╭╯╯      │        ╰╮\n       -34.7┤│    │     ╭╮  │   ╰╮ ╰╭╯│  ╰╮╭╯ ╰╮     ╭───╮  ││    ╭╯ ╰╯╰╮ ╭╯│╰──│        ╰╮  ╭──╮ ╭│\n       -56.4┼╯    ╰─╮  ╭╯╰──╯    │ ╭╯╭╯   ││   ╰╮   ╭╯   ╰─╮╰╯  ╭─╯     ╰─╯ ╰╮ ╭╯         │ ╭╯  ╰─╯╰\n       -78.2┤       ╰──╯         │╭╯││    ╰╯    │ ╭─╯      ╰╮ ╭─╯            ╰╮│          │╭╯\n      -100.0┼──┬──┬──┬──┬──┬──┬──├╯─├╯─┬──┬──┬──├─╯┬──┬──┬──├─╯┬──┬──┬──┬──┬──├╯─┬──┬──┬──├╯─┬──┬──┬ \n            1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30\n\n\n## Acknowledgements\nCore sequence asciiization algorithm adopted from https://github.com/kroitor/asciichart/blob/master/asciichartpy/\n\n\n## License\n[MIT License](https://github.com/w2sv/asciiplot/blob/master/LICENSE)\n",
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
