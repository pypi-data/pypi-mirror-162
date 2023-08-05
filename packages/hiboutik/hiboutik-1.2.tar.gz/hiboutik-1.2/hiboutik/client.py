import os
import re
import base64

from .exception import HiboutikException
from .entity_service import EntityService
from .service import Service


class Client:

    def __init__(self, api_url=None, api_domain=None, api_username=None, api_token=None):
        self.url = None
        self.username = None
        self.token = None

        domain = os.getenv('HIBOUTIK_API_DOMAIN')
        if api_domain:
            domain = api_domain
        if domain:
            self.set_api_domain(domain)

        url = os.getenv('HIBOUTIK_API_URL')
        if api_url:
            url = api_url
        if url:
            self.set_api_url(url)

        self.username = os.getenv('HIBOUTIK_API_USERNAME')
        if api_username:
            self.set_api_url(api_username)

        self.token = os.getenv('HIBOUTIK_API_TOKEN')
        if api_token:
            self.set_api_token(api_token)

    @staticmethod
    def is_valid_hostname(hostname):
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1]
        allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))

    def set_api_domain(self, api_domain):
        if not self.is_valid_hostname(api_domain):
            raise HiboutikException('Use valid domain name')

        self.set_api_url('https://{0}'.format(api_domain))

    def set_api_url(self, api_url):
        self.url = api_url

        return self

    def set_api_username(self, api_username):
        self.username = api_username

        return self

    def set_api_token(self, api_token):
        self.token = api_token

        return self

    def get_api_url(self):
        return self.url

    def get_service(self, path):
        return Service(self, self.get_url_for_path(path))

    def get_entity_service(self, path_pattern):
        return EntityService(self, self.get_url_for_path(path_pattern))

    def get_authorization(self):
        if not self.username:
            raise HiboutikException('Not defined hiboutik API username')
        if not self.token:
            raise HiboutikException('Not defined hiboutik API token')

        base64string = base64.b64encode(bytes('%s:%s' % (self.username, self.token), 'ascii'))
        return "Basic %s" % base64string.decode('utf-8')

    def get_url_for_path(self, path):
        return '{0}/api{1}'.format(self.get_api_url(), path)

    def get_api_documentation_url(self):
        if not self.url:
            raise HiboutikException('Not defined hiboutik API Url')

        return 'https://{0}/docapi/json/'.format(self.url)
