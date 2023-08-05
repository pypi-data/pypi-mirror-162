from .entity import Entity


class EntityService:

    def __init__(self, client, url_pattern):
        self.client = client
        self.url_pattern = url_pattern

    def get_entity(self, **kwargs):
        url = self.url_pattern
        for key, value in kwargs.items():
            url = url.replace('{' + key + '}', str(value))

        return Entity(self.client, url)
