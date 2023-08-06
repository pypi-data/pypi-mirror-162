# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sneakpeek']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0', 'validators>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'sneakpeek',
    'version': '0.2.0',
    'description': 'A python module to generate link previews.',
    'long_description': '\n<div align="center">\n  <h1>\n    SneakPeek\n  </h1>\n  <h4>A python module and a minimalistic server to generate link previews.</h4>\n</div>\n\n[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)\n\n\n## What is supported\n\n- Any page which supports [Open Graph Protocol](https://ogp.me) (which most sane websites do)\n- Special handling for sites like\n\n\n## Installation\n\nRun the following to install\n\n```sh\npip install sneakpeek\n```\n\n\n## Usage as a Python Module\n\n### From a URL\n\n```sh\n>>> import sneakpeek\n>>> from pprint import pprint\n\n>>> link = sneakpeek.SneakPeek("https://www.youtube.com/watch?v=dQw4w9WgXcQ")\n>>> link.fetch()\n>>> link.is_valid()\nTrue\n>>> pprint(link)\n{\'description\': \'The official video for “Never Gonna Give You Up” by Rick \'\n                \'AstleyTaken from the album ‘Whenever You Need Somebody’ – \'\n                \'deluxe 2CD and digital deluxe out 6th May ...\',\n \'domain\': \'www.youtube.com\',\n \'image\': \'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg\',\n \'image:height\': \'720\',\n \'image:width\': \'1280\',\n \'scrape\': False,\n \'site_name\': \'YouTube\',\n \'title\': \'Rick Astley - Never Gonna Give You Up (Official Music Video)\',\n \'type\': \'video.other\',\n \'url\': \'https://www.youtube.com/watch?v=dQw4w9WgXcQ\',\n \'video:height\': \'720\',\n \'video:secure_url\': \'https://www.youtube.com/embed/dQw4w9WgXcQ\',\n \'video:tag\': \'never gonna give you up karaoke\',\n \'video:type\': \'text/html\',\n \'video:url\': \'https://www.youtube.com/embed/dQw4w9WgXcQ\',\n \'video:width\': \'1280\'}\n\n>>> link = sneakpeek.SneakPeek(url="https://codingcoffee.dev")\n>>> print(link)\n{\n    \'title\': \'Home\',\n    \'description\': \'Software Engineer, with over 3 years of professional working experience, with full stack development and system design. I like blogging about things which interest me, have a niche for optimizing and customizing things to the very last detail, this includes my text editor and operating system alike.\',\n    \'domain\': \'codingcoffee.dev\',\n    \'image\': \'https://codingcoffee.dev/src/images/avatar.png\',\n}\n\n>>> link = sneakpeek.SneakPeek(url="https://github.com/codingcoffee")\n>>> print(link)\n{\'_url\': \'https://github.com/codingcoffee\',\n \'description\': \'Automate anything and everything 🙋\\u200d♂️. codingCoffee has \'\n                \'68 repositories available. Follow their code on GitHub.\',\n \'image\': \'https://avatars.githubusercontent.com/u/13611153?v=4?s=400\',\n \'image:alt\': \'Automate anything and everything 🙋\\u200d♂️. codingCoffee has 68 \'\n              \'repositories available. Follow their code on GitHub.\',\n \'scrape\': False,\n \'site_name\': \'GitHub\',\n \'title\': \'codingCoffee - Overview\',\n \'type\': \'profile\',\n \'url\': \'https://github.com/codingCoffee\'}\n```\n\n### From HTML\n\n```\n>>> HTML = """\n... <html xmlns:og="http://ogp.me/ns#">\n... <head>\n... <title>The Rock (1996)</title>\n... <meta property="og:title" content="The Rock" />\n... <meta property="og:type" content="movie" />\n... <meta property="og:url" content="http://www.imdb.com/title/tt0117500/" />\n... <meta property="og:image" content="http://ia.media-imdb.com/images/rock.jpg" />\n... </head>\n... </html>\n... """\n>>> movie = opengraph.OpenGraph() # or you can instantiate as follows: opengraph.OpenGraph(html=HTML)\n>>> movie.parser(HTML)\n>>> movie.is_valid()\nTrue\n```\n\n\n## Usage as a Server\n\nA simple django server is used to serve the requests. Checkout the server folder for more details\n\n```\nsneekpeek serve\n```\n\n\n## Development\n\n```\npip install -U poetry\ngit clone https://github.com/codingcoffee/sneakpeek\ncd sneakpeek\npoetry install\n```\n\n\n## Running Tests\n\n```sh\npoetry run pytest\n```\n\n- Tested Websites\n  - [x] [YouTube](https://youtube.com)\n  - [x] [GitHub](https://github.com)\n  - [x] [LinkedIN](https://linkedin.com)\n  - [x] [Reddit](https://reddit.com)\n  - [x] [StackOverflow](https://stackoverflow.com)\n  - [x] [Business Insider](https://www.businessinsider.in)\n\n\n## TODO\n\n- [ ] [Twitter](https://twitter.com) (requires a twitter [API key](https://developer.twitter.com/))\n- [ ] [Instagram](https://instagram.com) (using [instagram-scraper](https://github.com/arc298/instagram-scraper))\n- [ ] CI/CD for tests\n\n\n## Contribution\n\nHave better suggestions to optimize the server image? Found some typos? Need special handling for a new website? Found a bug? Want to work on a TODO? Go ahead and send in a Pull Request or create an [Issue](https://github.com/codingcoffee/sneakpeek/issues)! Contributions of any kind welcome!\n\n\n## License\n\nThe code in this repository has been released under the [MIT License](https://opensource.org/licenses/MIT)\n\n\n## Attributions\n\n- Python [opengraph](https://github.com/erikriver/opengraph)\n\n',
    'author': 'Ameya Shenoy',
    'author_email': 'shenoy.ameya@gmail.com',
    'maintainer': 'Ameya Shenoy',
    'maintainer_email': 'shenoy.ameya@gmail.com',
    'url': 'https://github.com/codingcoffee/sneakpeek',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
