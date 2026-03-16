# OAuthClientCredentialsWriteModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_id** | **str** | OAuth 2 client id | 
**client_secret** | **str** | OAuth 2 client secret | 

## Example

```python
from openproject_client.models.o_auth_client_credentials_write_model import OAuthClientCredentialsWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of OAuthClientCredentialsWriteModel from a JSON string
o_auth_client_credentials_write_model_instance = OAuthClientCredentialsWriteModel.from_json(json)
# print the JSON string representation of the object
print(OAuthClientCredentialsWriteModel.to_json())

# convert the object into a dict
o_auth_client_credentials_write_model_dict = o_auth_client_credentials_write_model_instance.to_dict()
# create an instance of OAuthClientCredentialsWriteModel from a dict
o_auth_client_credentials_write_model_from_dict = OAuthClientCredentialsWriteModel.from_dict(o_auth_client_credentials_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


