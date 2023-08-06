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
    'version': '0.2.11',
    'description': 'A simple scraping library.',
    'long_description': '# Purifier\n\nA simple scraping library.\n\nIt allows you to easily create simple and concise scrapers, even when the input\nis quite messy.\n\n\n## Example usage\n\nExtract titles and URLs of articles from Hacker News:\n\n```python\nfrom purifier import request, html, xpath, maps, fields, one\n\nscraper = (\n    request()\n    | html()\n    | xpath(\'//a[@class="titlelink"]\')\n    | maps(\n        fields(\n            title=xpath("text()") | one(),\n            url=xpath("@href") | one(),\n        )\n    )\n)\n\nresult = scraper.scrape("https://news.ycombinator.com")\n```\n```python\nresult == [\n     {\n         "title": "Why Is the Web So Monotonous? Google",\n         "url": "https://reasonablypolymorphic.com/blog/monotonous-web/index.html",\n     },\n     {\n         "title": "Old jokes",\n         "url": "https://dynomight.net/old-jokes/",\n     },\n     ...\n]\n```\n\n\n## Installation\n\n```\npip install purifier\n```\n\n\n## Docs\n\n- [Tutorial](https://github.com/gleb-akhmerov/purifier/blob/main/docs/Tutorial.md)\n- [Available scrapers](https://github.com/gleb-akhmerov/purifier/blob/main/docs/Available-scrapers.md) — API reference.\n',
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
