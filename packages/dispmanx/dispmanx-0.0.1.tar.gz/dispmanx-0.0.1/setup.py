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
    'version': '0.0.1',
    'description': "Libraty providing a buffer interface to your Raspberry Pi's GPU layer. Usable with pygame, PIL and other graphics libraries.",
    'long_description': '<h1 align="center">\n  <a href="https://dtcooper.github.io/python-dispmanx/">DispmanX Bindings for Python</a>\n</h1>\n\n<p align="center">\n  <a href="https://dtcooper.github.io/python-dispmanx/">Documentation</a> |\n  <a href="https://pypi.org/project/dispmanx/">Python Package Index</a>\n</p>\n\nThis is a Python library for interacting with the Raspberry Pi\'s DispmanX video\nAPI. Some use cases for this are,\n\n  * Directly writing to the lowlevel graphics layer of your Pi with relatively\n    high performance (for Python). There\'s no need to install X11.\n  * Small [pygame][pygame] or [Pillow][pillow]-based applications can be overlayed\n    onto the screen, with full support for transparency.\n\nThis library uses [ctypes][ctypes] to directly interact with your Raspberry Pi\'s\n`bcm_host.so` library.\n\n## Usage\n\nSee the [Quickstart section in the docs][quickstart].\n\n## TODO List\n\n- [x] Publish package to [PyPI][pypi]\n- [ ] Add API docs using [MkDocs][mkdocs], [Material for MkDocs][mkdocs-material],\n    and [mkdocstrings][mkdocstrings]\n- [ ] Allow multiple layers\n- [ ] Support additional pixel types\n- [ ] Support custom dimensions and offsets – API supports it, but requires weird\n    multiples of 16 or 32, [as documented here](picamera-overlay-docs). This\n    requires testing, because anecdotally it seems to work with smaller multiples.\n- [ ] Test run over SSH onto my home pi\n\n\n[ctypes]: https://docs.python.org/3/library/ctypes.html\n[mkdocs-material]: https://squidfunk.github.io/mkdocs-material/\n[mkdocs]: https://www.mkdocs.org/\n[mkdocstrings]: https://mkdocstrings.github.io/\n[picamera-overlay-docs]: https://picamera.readthedocs.io/en/release-1.13/api_renderers.html#picamera.PiOverlayRenderer\n[pillow]: https://pillow.readthedocs.io/\n[pygame]: https://www.pygame.org/docs/\n[pypi]: https://pypi.org/\n[quickstart]: https://dtcooper.github.io/python-dispmanx/#quickstart\n',
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
