# Connect
```python
from seven2one import *
client = TechStack(host, user, password)

# More parameters
client = TechStack(host, user, password, copyGraphQLString=True, logLevel="INFO")
```

# Basic read operations

```python
client.inventories()
client.items('appartments', references=True)
client.inventoryProperties('appartments')
client.propertyList('appartments', references=True, dataTypes=True)
```

# Write operations

## Create inventory
```python
properties = [
   {
        'dataType': 'DATE_TIME_OFFSET',
        'name': 'fieldDATETIMEOFFSET',
        'nullable': True
    },
    {
        'dataType': 'BOOLEAN',
        'name': 'fieldBOOLEAN',
        'nullable': True
    }
]


client.createInventory('testInventory', properties)
```
## Add (basic) items
```python
items =  [
        {
        "fieldSTRING": "bla",
        "fieldDECIMAL": 0,
        "fieldLONG": 0,
        "fieldINT": 0,
        "fieldBOOLEAN": True,
        "fieldDATETIME":  "2021-09-14T00:00:00.000Z",
        "fieldDATETIMEOFFSET": "2021-09-14T00:00:00.000Z"
    }
]

addBasicItems('testInventory', items)

```