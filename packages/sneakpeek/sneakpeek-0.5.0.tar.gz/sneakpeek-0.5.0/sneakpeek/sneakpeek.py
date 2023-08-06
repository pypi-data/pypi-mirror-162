# encoding: utf-8

"""Module for SneakPeek."""

# standard imports
import json
import re
import urllib.request
from urllib.parse import urlparse

# third-party imports
import validators
from bs4 import BeautifulSoup


class SneakPeek(dict):
    """ """

    required_attrs = ["title", "type", "image", "url", "description"]

    def __init__(self, url=None, html=None, scrape=False, **kwargs):
        # If scrape == True, then will try to fetch missing attribtues
        # from the page's body
        self.domain = None
        self.scrape = scrape
        self.url = url

        self.title = ""
        self.type = ""
        self.image = ""
        self.description = ""

        self.error = None

        for k in kwargs.keys():
            self[k] = kwargs[k]

        if url:
            self.is_valid_url(url)
            self.domain = urlparse(self.url).netloc

        if html is not None:
            self.parse(html)

    def __setattr__(self, name, val):
        self[name] = val

    def __getattr__(self, name):
        return self[name]

    def is_valid_url(self, url=None):
        return validators.url(url)

    def fetch_and_parse_twitter(self):
        pass

    def fetch(self):
        """ """
        # TODO: use random user agent for every request - https://github.com/Luqman-Ud-Din/random_user_agent
        if self.domain == "twitter.com":
            self.fetch_and_parse_twitter()
            return
        req = urllib.request.Request(self.url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req) as raw:
                html = raw.read()
        except Exception as err:
            html = ""
            self.error = str(err)
            return
        return self.parse(html)

    def parse(self, html):
        """ """
        if isinstance(html, BeautifulSoup):
            doc = html
        else:
            doc = BeautifulSoup(html, "html.parser")
        try:
            ogs = doc.html.head.findAll(property=re.compile(r"^og"))
        except:
            self.error = "Parsing Error: Open Graph Meta Not Found"
            ogs = []
        for og in ogs:
            if og.has_attr("content"):
                self[og["property"][3:]] = og["content"]
        # Couldn't fetch all attrs from og tags, try scraping body
        if not self.is_valid() and self.scrape:
            for attr in self.required_attrs:
                if not self.valid_attr(attr):
                    try:
                        self[attr] = getattr(self, "scrape_%s" % attr)(doc)
                    except AttributeError:
                        pass

    def valid_attr(self, attr):
        return self.get(attr) and len(self[attr]) > 0

    def is_valid(self):
        return all([self.valid_attr(attr) for attr in self.required_attrs])

    def to_html(self):
        if not self.is_valid():
            return '<meta property="og:error" content="og metadata is not valid" />'

        meta = ""
        for key, value in self.iteritems():
            meta += '\n<meta property="og:%s" content="%s" />' % (key, value)
        meta += "\n"

        return meta

    def to_json(self):
        if not self.is_valid():
            return json.dumps({"error": "og metadata is not valid"})

        return json.dumps(self)

    def to_xml(self):
        pass

    def scrape_image(self, doc):
        images = [dict(img.attrs)["src"] for img in doc.html.body.findAll("img")]

        if images:
            return images[0]

        return ""

    def scrape_title(self, doc):
        try:
            return doc.html.head.title.text
        except:
            return ""

    def scrape_type(self, doc):
        try:
            return "other"
        except:
            return ""

    def scrape_url(self, doc):
        try:
            return self.url
        except:
            return ""

    def scrape_description(self, doc):
        try:
            tag = doc.html.head.findAll("meta", attrs={"name": "description"})
            result = "".join([t["content"] for t in tag])
            return result
        except:
            return ""
