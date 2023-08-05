import unittest
from hiboutik.client import Client


class TestService(unittest.TestCase):

    def test_products_get(self):
        client = Client()
        service = client.get_service('/products/')
        response = service.get({'order_by': 'product_id', 'sort': 'ASC'})
        for item in response:
            self.assertIn('product_id', item)

    def test_products_post(self):
        client = Client()
        service = client.get_service('/products/')
        response = service.post({
            'product_price': 10.0
        })
        self.assertIn('product_id', response)

    def test_product_update(self):
        client = Client()
        entity_service = client.get_entity_service('/product/{product_id}/')
        entity = entity_service.get_entity(product_id=6)
        response = entity.put({
            'product_attribute': 'product_price',
            'new_value': 5.0
        })