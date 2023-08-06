# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['selenium_toolkit']

package_data = \
{'': ['*']}

install_requires = \
['selenium>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'selenium-toolkit',
    'version': '0.0.3',
    'description': 'this is not a awesome description',
    'long_description': "# selenium-toolkit\n\nThis library provides an easier way to use and interact with selenium driver. \n\nFeatures that currently selenium-toolkit can offer:\n\n- ✅️ **More legible selenium code**\n- ✅️ **Abstractions of selenium methods**\n- ✅️ **Helpful tools to use when interacting with browsers**\n\n\n\n## Install\n```\npip install selenium-toolkit\n```\n\n## Basic\n```python\nfrom selenium.webdriver import Chrome\nfrom selenium_toolkit import SeleniumToolKit\n\n# Create chomedriver instance\ndriver = Chrome()\n\n# Pass driver to SeleniumToolKit\nselenium_kit = SeleniumToolKit(driver=driver)\n\n# Use SeleniumToolKit to find a web element\nweb_element = selenium_kit.query_selector('.class1')\n\n# With returned web_element use click() method\nweb_element.click()\n```",
    'author': 'Jorge Vasconcelos',
    'author_email': 'john@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jorgepvasconcelos/webdriver-toolkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
