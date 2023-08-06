# fshelper
FreshService API usage helper version: "0.2.0"

## Features
### Assets Endpoint v0.2.0
  Added an endpoint for working with assets

## Usage
*Example:*
```python
credential = Credential('MY_API_KEY', 'X')
with RequestService(credential, "mydomain") as request_service:
    asset_end_point = AssetsEndPoint(request_service)
    _assets = asset_end_point.get_all("include=type_fields") # gets the type_fields in the response data
    assets = []
    for asset_list in _assets:
        assets.extend(asset_list)
    licensed_assets = [asset for asset in assets if asset.get("assigned_on") is not None]
print(f"{len(licensed_assets)} assets found")
```

### Credentials for the FreshService API
The `fshelper.Credential` class is meant to help gather the basic authentication information for the FreshService API.
Provide your FreshService API key as the username and `X` as the password to the constructor.

https://api.freshservice.com/#authentication

### RequestService
Wrapper for the `requests` package to create an authenticated requests `Session`.   
Takes a `Credential` object and the company's FreshService domain (the part prior to `freshservice.com`).
Use this as a context manager or call the `RequestService.new_session()` method in a try, except, finally block with
`RequestService.session.close()` in the finally block.


### Endpoints
Different classes to work with different FreshService API endpoints.
