# OAuthClientCredentialsReadModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This OAuth Client Credentials object  **Resource**: OAuthClientCredentials | 
**integration** | [**Link**](Link.md) | The resource that integrates this OAuth client credentials. Currently, only &#x60;Storage&#x60; resources are able to contain OAuth client credentials.  **Resource**: Storage | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.o_auth_client_credentials_read_model_links import OAuthClientCredentialsReadModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of OAuthClientCredentialsReadModelLinks from a JSON string
o_auth_client_credentials_read_model_links_instance = OAuthClientCredentialsReadModelLinks.from_json(json)
# print the JSON string representation of the object
print(OAuthClientCredentialsReadModelLinks.to_json())

# convert the object into a dict
o_auth_client_credentials_read_model_links_dict = o_auth_client_credentials_read_model_links_instance.to_dict()
# create an instance of OAuthClientCredentialsReadModelLinks from a dict
o_auth_client_credentials_read_model_links_from_dict = OAuthClientCredentialsReadModelLinks.from_dict(o_auth_client_credentials_read_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


