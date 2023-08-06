# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['collagraph',
 'collagraph.cgx',
 'collagraph.renderers',
 'collagraph.renderers.pyside',
 'collagraph.renderers.pyside.objects']

package_data = \
{'': ['*']}

install_requires = \
['observ>=0.9.3']

extras_require = \
{'pygfx': ['pygfx>=0.1.9'],
 'pyside:python_version < "3.11"': ['pyside6_essentials>=6.3,<7.0']}

setup_kwargs = {
    'name': 'collagraph',
    'version': '0.5.0',
    'description': 'Reactive user interfaces',
    'long_description': '[![PyPI version](https://badge.fury.io/py/collagraph.svg)](https://badge.fury.io/py/collagraph)\n[![CI status](https://github.com/fork-tongue/collagraph/workflows/CI/badge.svg)](https://github.com/fork-tongue/collagraph/actions)\n\n# Collagraph 📓\n\nReactive user interfaces.\n\n> The word [Collagraphy](https://en.wikipedia.org/wiki/Collagraphy) is derived from the Greek word _koll_ or _kolla_, meaning glue, and graph, meaning the activity of drawing.\n\nInspired by Vue and React.\n\n\n## Features\n\nWrite your Python interfaces in a declarative manner with plain render functions, component classes or even single-file components using Vue-like syntax, but with Python!\n\n* Reactivity (made possible by leveraging [observ](https://github.com/fork-tongue/observ))\n* Function components\n* Class components with local state and life-cycle methods/hooks\n* Single-file components with Vue-like syntax (`.cgx` files)\n* Custom renderers\n\nHere is an example that shows a simple counter, made with a function component:\n\n```python\nfrom PySide6 import QtWidgets\nfrom observ import reactive\nimport collagraph as cg\n\n# Declare some reactive state\nstate = reactive({"count": 0})\n\n# Define function that adjusts the state\ndef bump():\n    state["count"] += 1\n\n# Declare how the state should be rendered\ndef Counter(props):\n    return cg.h(\n        "widget",\n        {},\n        cg.h("label", {"text": f"Count: {props[\'count\']}"}),\n        cg.h("button", {"text": "Bump", "on_clicked": bump}),\n    )\n\n# Create a Collagraph instance with a PySide renderer \n# and register with the Qt event loop\ngui = cg.Collagraph(\n    renderer=cg.PySideRenderer(),\n    event_loop_type=cg.EventLoopType.QT,\n)\n# Render the function component into a container \n# (in this case the app but can be another widget)\napp = QtWidgets.QApplication()\ngui.render(cg.h(Counter, state), app)\napp.exec()\n```\n\nFor more examples, please take a look at the [examples folder](examples).\n\nCurrently there are two renderers:\n\n* [PysideRenderer](collagraph/renderers/pyside_renderer.py): for rendering PySide6 applications\n* [PygfxRenderer](collagraph/renderers/pygfx_renderer.py): for rendering 3D graphic scenes with [Pygfx](https://github.com/pygfx/pygfx)\n\nIt is possible to create a custom Renderer using the [Renderer](collagraph/renderers/__init__.py) interface, to render to other UI frameworks, for instance wxPython, or even the browser DOM.\n',
    'author': 'Berend Klein Haneveld',
    'author_email': 'berendkleinhaneveld@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fork-tongue/collagraph',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)
