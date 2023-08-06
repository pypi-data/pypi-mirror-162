# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dispmanx']

package_data = \
{'': ['*']}

extras_require = \
{'numpy': ['numpy<2']}

setup_kwargs = {
    'name': 'dispmanx',
    'version': '0.0.3',
    'description': "Libraty providing a buffer interface to your Raspberry Pi's GPU layer. Usable with pygame, PIL and other graphics libraries.",
    'long_description': '<h1 align="center">\n  <a href="https://dtcooper.github.io/python-dispmanx/">DispmanX Bindings for Python</a>\n</h1>\n\n<p align="center">\n  <a href="https://dtcooper.github.io/python-dispmanx/">Documentation</a> |\n  <a href="https://pypi.org/project/dispmanx/">Python Package Index</a>\n</p>\n\n## Usage\n\nInstall with pip,\n\n```bash\npip install dispmanx\n```\n\nThen try out this sample program using [pygame](https://www.pygame.org/docs/),\n\n```python\nfrom random import randint\nimport pygame\nfrom dispmanx import DispmanX\n\ndef random_color_with_alpha():\n    return tuple(randint(0, 0xFF) for _ in range(3)) + (randint(0x44, 0xFF),)\n\ndisplay = DispmanX(pixel_format="RGBA")\nsurface = pygame.image.frombuffer(display.buffer, display.size, display.pixel_format)\nclock = pygame.time.Clock()\n\nfor _ in range(20):\n    surface.fill(random_color_with_alpha())\n    display.update()\n    clock.tick(2)\n\n```\n\nNext stop: [the project\'s documentation](https://dtcooper.github.io/python-dispmanx/).\n\n## License\n\nThis project is licensed under the [MIT License](https://opensource.org/licenses/MIT)\n&mdash; see the [LICENSE](https://github.com/dtcooper/python-dispmanx/blob/main/LICENSE)\nfile for details.\n\n## Final Note\n\n**_...and remember kids, have fun!_**\n',
    'author': 'David Cooper',
    'author_email': 'david@dtcooper.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dtcooper/python-dispmanx',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
