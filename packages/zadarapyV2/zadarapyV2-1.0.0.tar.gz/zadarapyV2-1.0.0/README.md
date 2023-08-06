# zadarapyV2

## Requirements.

Python 2.7 and 3.4+

## Installation & Usage
### pip install

Clone the repo and from zadarapyV2 folder, run:

```sh
pip install -r requirements.txt
pip install .
```


Then import the package:
```python
import zadarapyV2
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python
import zadarapyV2
from zadarapyV2.vpsa import configuration as vpsa_configuration
from zadarapyV2.cc import configuration as cc_configuration

vpsa_conf = vpsa_configuration.Configuration()
cc_conf = cc_configuration.Configuration()

# Configure host ip + basePath
vpsa_conf.host='http://10.2.10.33/api'
cc_conf.host = 'https://10.16.1.50/api/v2'

# Configure API key authorization: api_key
vpsa_conf.api_key = {'X-Access-Key':'PPYW8KNXJA495-2'}

# create an instance of the API class
vpsa_api = vpsa.UsersApi(vpsa.ApiClient(vpsa_conf))

body = vpsa.Body115('john','john@mail.com')

try:
    api_response = vpsa_api.add_user(body=body)
    pprint(api_response)
    users_list = vpsa_api.list_users().response.users #users_list is list of users
except ApiException as e:
    print("Exception when calling add_user: %s\n" % e)

```
