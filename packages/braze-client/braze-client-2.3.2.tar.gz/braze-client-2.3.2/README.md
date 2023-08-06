# braze-client
A Python client for the Braze REST API

[![Build Status](https://travis-ci.com/dtatarkin/braze-client.svg?branch=master)](https://travis-ci.com/dtatarkin/braze-client)
[![Coverage](https://codecov.io/gh/dtatarkin/braze-client/branch/master/graph/badge.svg)](https://codecov.io/gh/dtatarkin/braze-client)

### How to install

Make sure you have Python 2.7+ or 3.6+ installed and run:

```
$ git clone https://github.com/dtatarkin/braze-client
$ cd braze-client
$ python setup.py install
```

### How to use

```python
from braze.client import BrazeClient
client = BrazeClient(api_key='YOUR_API_KEY', use_auth_header=True)

r = client.user_track(
    attributes=[{
        'external_id': '1',
        'first_name': 'First name',
        'last_name': 'Last name',
        'email': 'email@example.com',
        'status': 'Active',
        # And other fields ...
    }],
    events=None,
    purchases=None,
)
if r['success']:
    # do our magic here
    print('Success!')
    print(r)
else:
    print(r['client_error'])
    print(r['errors'])

```
For more examples, check `examples.py`.

### How to test

To run the unit tests, make sure you have the [tox](https://tox.readthedocs.io/en/latest/) module installed 
and run the following from the repository root directory:

`$ tox`
