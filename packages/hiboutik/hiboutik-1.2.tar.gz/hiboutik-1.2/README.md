# Hiboutik API Client 

## Installation 

```shell
pip install hiboutik
```


## Configuration

### Get your credentials

In your Hiboutk interface, go to Parameters > API to find your credentials.

### Set credential in application

You can pass configuration with environment params:

```.ini
HIBOUTIK_API_DOMAIN=my.domain.com
or
HIBOUTIK_API_URL=https://my.domain.com

HIBOUTIK_API_USERNAME=
HIBOUTIK_API_TOKEN=
```

Or you can pass configuration directly in Client instance

```python
from hiboutik import Client

client = Client(
    api_domain='my.domain.com',
    # or api_url='https://my.domain.com',
    api_username='',
    api_token=''
)
```

### Usage

After instance your client, you get Service for your API (you can show all APIs in https://YOUR_DOMAIN/docapi/json/):

### General usage

```python
from hiboutik import Client

client = Client()
service = client.get_service('/products/')

# Get products
response = service.get({'order_by': 'product_id', 'sort': 'ASC'})
for product in response:
    print(product['product_id'])

# Create new product
response = service.post({'product_price': 10.0})
print(response['product_id'])

```

### Entity usage

```python
from hiboutik import Client

client = Client()
entity_service = client.get_entity_service('/product/{product_id}/')

# Instance service for entity
entity = entity_service.get_entity(6)

# Update entity
entity.put({
    'product_attribute': 'product_price',
    'new_value': 5.0
})

entity_service = client.get_entity_service('/brands/{brand_id}')
entity = entity_service.get_entity(1)
entity.delete()

```
