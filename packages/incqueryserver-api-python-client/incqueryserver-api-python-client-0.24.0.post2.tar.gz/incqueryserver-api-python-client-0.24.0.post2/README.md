# incqueryserver-api-python-client

This package offers an easy way to connect to a running IncQuery Server instance.

## Connect to a running IncQuery Server
```python
from iqs_api import connect
```
### No authentication
```python
iqs = connect("https://incqueryserver.url.com")
```
### OpenID Connect (OIDC)
```python
token = "token"

iqs = connect(
    address="https://incqueryserver.url.com",
    auth_header_name="Authorization",
    auth_header_value=f"Bearer {token}",
    use_auth_header=True
)
```
### Basic Authentication
```python
iqs = connect(
    address="https://incqueryserver.url.com",
    username="username",
    password="password"
)
```

## Issue API calls
**GET** request example:
```python
response = iqs.server_management.get_server_info()
```
---
**POST** request example:
```python
from iqs_client import models

response = iqs.demo.update_model_compartment_index(
    index_compartment=models.IndexCompartment(
        model_compartment="model_compartment_uri",
        indexes=["index1", "index2"]
    )
)
```

> **IMPORTANT**:  It is recommended to provide parameters as keyword arguments (opposed to positional) 

## Other options
### Configure self-signed certificate
```python
from iqs_client import Configuration

custom_config = Configuration()
custom_config.ssl_ca_cert = "path/to/cert.cer"

iqs = connect(
    address="https://incqueryserver.url.com",
    configuration=custom_config
)
```

### Disable SSL verification
```python
from iqs_client import Configuration

custom_config = Configuration()
custom_config.verify_ssl = False

iqs = connect(
    address="https://incqueryserver.url.com",
    configuration=custom_config
)
```
