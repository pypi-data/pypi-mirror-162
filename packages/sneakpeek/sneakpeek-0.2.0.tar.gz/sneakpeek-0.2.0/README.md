
<div align="center">
  <h1>
    SneakPeek
  </h1>
  <h4>A python module and a minimalistic server to generate link previews.</h4>
</div>

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)


## What is supported

- Any page which supports [Open Graph Protocol](https://ogp.me) (which most sane websites do)
- Special handling for sites like


## Installation

Run the following to install

```sh
pip install sneakpeek
```


## Usage as a Python Module

### From a URL

```sh
>>> import sneakpeek
>>> from pprint import pprint

>>> link = sneakpeek.SneakPeek("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
>>> link.fetch()
>>> link.is_valid()
True
>>> pprint(link)
{'description': 'The official video for “Never Gonna Give You Up” by Rick '
                'AstleyTaken from the album ‘Whenever You Need Somebody’ – '
                'deluxe 2CD and digital deluxe out 6th May ...',
 'domain': 'www.youtube.com',
 'image': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
 'image:height': '720',
 'image:width': '1280',
 'scrape': False,
 'site_name': 'YouTube',
 'title': 'Rick Astley - Never Gonna Give You Up (Official Music Video)',
 'type': 'video.other',
 'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
 'video:height': '720',
 'video:secure_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
 'video:tag': 'never gonna give you up karaoke',
 'video:type': 'text/html',
 'video:url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
 'video:width': '1280'}

>>> link = sneakpeek.SneakPeek(url="https://codingcoffee.dev")
>>> print(link)
{
    'title': 'Home',
    'description': 'Software Engineer, with over 3 years of professional working experience, with full stack development and system design. I like blogging about things which interest me, have a niche for optimizing and customizing things to the very last detail, this includes my text editor and operating system alike.',
    'domain': 'codingcoffee.dev',
    'image': 'https://codingcoffee.dev/src/images/avatar.png',
}

>>> link = sneakpeek.SneakPeek(url="https://github.com/codingcoffee")
>>> print(link)
{'_url': 'https://github.com/codingcoffee',
 'description': 'Automate anything and everything 🙋\u200d♂️. codingCoffee has '
                '68 repositories available. Follow their code on GitHub.',
 'image': 'https://avatars.githubusercontent.com/u/13611153?v=4?s=400',
 'image:alt': 'Automate anything and everything 🙋\u200d♂️. codingCoffee has 68 '
              'repositories available. Follow their code on GitHub.',
 'scrape': False,
 'site_name': 'GitHub',
 'title': 'codingCoffee - Overview',
 'type': 'profile',
 'url': 'https://github.com/codingCoffee'}
```

### From HTML

```
>>> HTML = """
... <html xmlns:og="http://ogp.me/ns#">
... <head>
... <title>The Rock (1996)</title>
... <meta property="og:title" content="The Rock" />
... <meta property="og:type" content="movie" />
... <meta property="og:url" content="http://www.imdb.com/title/tt0117500/" />
... <meta property="og:image" content="http://ia.media-imdb.com/images/rock.jpg" />
... </head>
... </html>
... """
>>> movie = opengraph.OpenGraph() # or you can instantiate as follows: opengraph.OpenGraph(html=HTML)
>>> movie.parser(HTML)
>>> movie.is_valid()
True
```


## Usage as a Server

A simple django server is used to serve the requests. Checkout the server folder for more details

```
sneekpeek serve
```


## Development

```
pip install -U poetry
git clone https://github.com/codingcoffee/sneakpeek
cd sneakpeek
poetry install
```


## Running Tests

```sh
poetry run pytest
```

- Tested Websites
  - [x] [YouTube](https://youtube.com)
  - [x] [GitHub](https://github.com)
  - [x] [LinkedIN](https://linkedin.com)
  - [x] [Reddit](https://reddit.com)
  - [x] [StackOverflow](https://stackoverflow.com)
  - [x] [Business Insider](https://www.businessinsider.in)


## TODO

- [ ] [Twitter](https://twitter.com) (requires a twitter [API key](https://developer.twitter.com/))
- [ ] [Instagram](https://instagram.com) (using [instagram-scraper](https://github.com/arc298/instagram-scraper))
- [ ] CI/CD for tests


## Contribution

Have better suggestions to optimize the server image? Found some typos? Need special handling for a new website? Found a bug? Want to work on a TODO? Go ahead and send in a Pull Request or create an [Issue](https://github.com/codingcoffee/sneakpeek/issues)! Contributions of any kind welcome!


## License

The code in this repository has been released under the [MIT License](https://opensource.org/licenses/MIT)


## Attributions

- Python [opengraph](https://github.com/erikriver/opengraph)

