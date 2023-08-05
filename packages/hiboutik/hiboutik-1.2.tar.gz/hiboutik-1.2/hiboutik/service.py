import json

from urllib.request import Request, urlopen
from urllib.parse import urlencode


class Service:

    def __init__(self, client, url):
        self.url = url
        self.client = client

    def _request(self, method, query_parameters=None, post_data=None):
        url = self.url
        if query_parameters:
            url = '{0}?{1}'.format(url, urlencode(query_parameters))

        data = None
        if post_data:
            data = urlencode(post_data).encode('utf-8')
        request = Request(url, method=method, data=data)
        request.add_header("Authorization", self.client.get_authorization())
        response = urlopen(request)
        content = response.read()
        return json.loads(content)

    def get(self, parameters=None):
        return self._request('GET', query_parameters=parameters)

    def delete(self):
        return self._request('DELETE')

    def post(self, data=None):
        return self._request('POST', post_data=data)

    def put(self, data=None):
        return self._request('PUT', post_data=data)
