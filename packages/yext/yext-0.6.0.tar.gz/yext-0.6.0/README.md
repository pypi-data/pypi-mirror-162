# Yext API Client for Python
This library contains utilities for interacting with the Yext API in Python.

## 💡 Getting Started

First, install Yext Python API Client via the [pip](https://pip.pypa.io/en/stable/installing) package manager:
```bash
pip install --upgrade 'yext'
```

Then, create entities in your Knowledge Graph:
```python
from yext import YextClient

client = YextClient('<your_api_key>')
profile = {
    'meta': {
        'id': 'entity_id',
        'countryCode': 'US'
    },
    'name': 'What is Yext Answers?',
    'answer': 'A revolutionary search product.'
}
entity_type = 'faq'

client.create_entity(entity_type, profile)
```
