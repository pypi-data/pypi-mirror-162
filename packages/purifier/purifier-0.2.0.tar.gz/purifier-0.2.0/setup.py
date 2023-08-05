# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['purifier']
install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0',
 'cloudscraper>=1.2.60,<2.0.0',
 'jq>=1.2.2,<2.0.0',
 'jsonfinder>=0.4.2,<0.5.0',
 'lxml>=4.9.1,<5.0.0',
 'parsy>=1.4.0,<2.0.0',
 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'purifier',
    'version': '0.2.0',
    'description': '',
    'long_description': '# Purifier\n\nA simple scraping library.\n\nIt allows you to easily create simple and concise scrapers, even when the input\nis quite messy.\n\n\n## Example usage\n\nExtract titles and URLs of articles from Hacker News:\n\n```python\nfrom purifier import request, html, xpath, maps, fields, one\n\nscraper = (\n    request()\n    | html()\n    | xpath(\'//a[@class="titlelink"]\')\n    | maps(\n        fields(\n            title=xpath("text()") | one(),\n            url=xpath("@href") | one(),\n        )\n    )\n)\n\nresult = scraper.scrape("https://news.ycombinator.com")\n```\n```python\nresult == [\n     {\n         "title": "Why Is the Web So Monotonous? Google",\n         "url": "https://reasonablypolymorphic.com/blog/monotonous-web/index.html",\n     },\n     {\n         "title": "Old jokes",\n         "url": "https://dynomight.net/old-jokes/",\n     },\n     ...\n]\n```\n\n\n## Tutorial\n\nThe simplest possible scraper consists of a single action:\n\n```python\nscraper = request()\n```\n```python\nresult == (\n    \'<html lang="en" op="news"><head><meta name="referrer" content="origin">...\'\n)\n```\n\nAs you can see, this scraper returns the HTTP response as a string. To do\nsomething useful with it, connect it to another scraper:\n\n```python\nscraper = request() | html()\n```\n```python\nresult == <Element html at 0x7f1be2193e00>\n```\n\n`|` ("pipe") takes output of one action and passes it to the next one. The\n`html` action parses the HTML, so you can then query it with `xpath`:\n\n```python\nscraper = (\n    request()\n    | html()\n    | xpath(\'//a[@class="titlelink"]/text()\')\n)\n```\n```python\nresult == [\n    "C99 doesn\'t need function bodies, or \'VLAs are Turing complete\'",\n    "Quaise Energy is working to create geothermal wells",\n    ...\n]\n```\n\nAlternatively, instead of using "/text()" at the end of the XPath, you could use\n`maps` with `xpath` and `one`:\n\n```python\nscraper = (\n    request()\n    | html()\n    | xpath(\'//a[@class="titlelink"]\')\n    | maps(xpath(\'text()\') | one())\n)\n```\n```python\nresult == [\n    "Why Is the Web So Monotonous? Google",\n    "Old jokes",\n    ...\n]\n```\n\n`maps` ("map scraper") applies a scraper to each element of its input, which can\nbe really powerful at times. For example, combine it with `fields`, and the\nresult will look a bit different:\n\n```python\nscraper = (\n    request()\n    | html()\n    | xpath(\'//a[@class="titlelink"]\')\n    | maps(\n        fields(title=xpath(\'text()\') | one())\n    )\n)\n```\n```python\nresult == [\n    {"title": "Why Is the Web So Monotonous? Google"},\n    {"title": "Old jokes"},\n    ...\n]\n```\n\n`fields` constructs a dictionary, allowing you to name things and also to\nextract multiple different things from a single input:\n\n```python\nscraper = (\n    request()\n    | html()\n    | xpath(\'//a[@class="titlelink"]\')\n    | maps(\n        fields(\n            title=xpath(\'text()\') | one(),\n            url=xpath(\'@href\') | one(),\n        )\n    )\n)\n```\n```python\nresult == [\n     {\n         "title": "Why Is the Web So Monotonous? Google",\n         "url": "https://reasonablypolymorphic.com/blog/monotonous-web/index.html",\n     },\n     {\n         "title": "Old jokes",\n         "url": "https://dynomight.net/old-jokes/",\n     },\n     ...\n]\n```',
    'author': 'Gleb Akhmerov',
    'author_email': 'nontrivial-analysis@proton.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
