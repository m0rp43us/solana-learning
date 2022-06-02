import cfscrape
import collections
import datetime
import requests
import spl.metadata as metadata


from cachecontrol import CacheControl
from cachecontrol.caches import FileCache
from spl.errors import NonSingletonResultException, NotDownloadableException


def api_call(url, clazz):
    def innerfunc(self, api_id):
        result = self.session.get(self.rootURL + url.format(api_id))
        result.raise_for_status()
        cum_result = result.json()
        if "X-Page-Count" in result.headers:
            while result.headers['X-Page-Count'] != result.headers['X-Page-Index']:
                cur_page = int(result.headers['X-Page-Index'])
                result = self.session.get(self.rootURL + url.format(api_id) + "?page={}".format(cur_page + 1))
                result.raise_for_status()
                cum_result += result.json()
        return clazz(self, cum_result)
    return innerfunc


class Resource(object):
    def __init__(self, spiget, json):
        if isinstance(json, collections.Sequence):
            raise NonSingletonResultException()
        self.id = json['id']
        self.name = json['name']
        self.tag = json['tag']
        self.update_date = datetime.datetime.fromtimestamp(json['updateDate'])
        self.author = spiget.author(json['author']['id'])

        self.versions = sorted(spiget.resource_versions(self.id), key=lambda v: v.release_date, reverse=True)
        self.current_version = [v for v in self.versions if v.id == json['version']['id']][0]

        self.category = spiget.category(json['category']['id'])

        self.tested_versions = json['testedVersions']

        self.external = json['external']

        self.file_size = ""
        if not self.external:
            self.file_size = json['file']['size']

    def download(self):
        if hasattr(self.current_version, 'url'):
            if not self.external:
                return requests.get("https://api.spiget.org/v2/resources/{}/download".format(self.id), stream=True)
            else:
                scraper = cfscrape.create_scraper()
                return scraper.get("https://www.spigotmc.org/{}".format(self.current_version.url), stream=True)
        else:
            raise NotDownloadableException()

    def for_json(self):
        return {
            'type': 'spl.spiget.Resource',
            'id': self.id,
            'name': self.name,
            'tag': self.tag,
            'updateDate': self.update_date.timestamp(),
            'author': {'id': self.author.id},
            'category': {'id': self.category.id},
            'versions': self.versions,
            'version': {'id': self.current_version.id},
            'testedVersions': self.tested_versions,
            'external': self.external,
            'file': {'size': self.file_size}
        }


class Author(object):
    def __init__(self, spiget, json):
        self.name = json['name']
        self.id = json['id']


class Category(object):
    def __init__(self, spiget, json):
        self.name = json['name']
        self.id = json['id']


def ListResult(clazz):
    class ListResultInner(object):
        def __init__(self, spiget, json):
            self.items = list(map(lambda v: clazz(self, v), json))

        def __getitem__(self, key):
            return self.items.__getitem__(key)

        def for_json(self):
            return self.items

    return ListResultInner


class Version(object):
    def __init__(self, spiget, json):
        self.id = json['id']
        self.name = json['name']
        self.release_date = datetime.datetime.fromtimestamp(json['releaseDate'])
        if 'url' in json:
            self.url = json['url']

    def __repr__(self, *args, **kwargs):
        return self.name

    def for_json(self):
        return {
            'type': 'spl.spiget.Version',
            'id': self.id,
            'name': self.name,
            'releaseDate': self.release_date.timestamp(),
            'url': self.url if hasattr(self, "url") else None
        }


class SearchResult(object):
    def __init__(self, spiget, json):
        self.name = json['name']
        self.tag = json['tag']
        self.id = json['id']


class SpiGet(object):
    def __init__(self):
        session = requests.Session()
        self.rootURL = "https://api.spiget.org/v2/"
        session.headers['User-Agent'] = "{} v{}".format(metadata.NAME, metadata.VERSION)

        self.session = CacheControl(
            session,
            cache=FileCache('.spl/cache')
        )

    author = api_call("authors/{}", Author)
    category = api_call("categories/{}", Category)

    resource_details = api_call("resources/{}", Resource)
    resource_versions = api_call("resources/{}/versions", ListResult(Version))

    resource_search = api_call("search/resources/{}", ListResult(SearchResult))
