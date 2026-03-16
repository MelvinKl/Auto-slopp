# OAuthClientCredentialsReadModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**type** | **str** |  | 
**client_id** | **str** | OAuth 2 client id | 
**confidential** | **bool** | true, if OAuth 2 credentials are confidential, false, if no secret is stored | 
**created_at** | **datetime** | The time the OAuth client credentials were created at | [optional] 
**updated_at** | **datetime** | The time the OAuth client credentials were last updated | [optional] 
**links** | [**OAuthClientCredentialsReadModelLinks**](OAuthClientCredentialsReadModelLinks.md) |  | 

## Example

```python
from openproject_client.models.o_auth_client_credentials_read_model import OAuthClientCredentialsReadModel

# TODO update the JSON string below
json = "{}"
# create an instance of OAuthClientCredentialsReadModel from a JSON string
o_auth_client_credentials_read_model_instance = OAuthClientCredentialsReadModel.from_json(json)
# print the JSON string representation of the object
print(OAuthClientCredentialsReadModel.to_json())

# convert the object into a dict
o_auth_client_credentials_read_model_dict = o_auth_client_credentials_read_model_instance.to_dict()
# create an instance of OAuthClientCredentialsReadModel from a dict
o_auth_client_credentials_read_model_from_dict = OAuthClientCredentialsReadModel.from_dict(o_auth_client_credentials_read_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


