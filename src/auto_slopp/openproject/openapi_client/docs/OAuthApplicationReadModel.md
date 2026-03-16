# OAuthApplicationReadModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**type** | **str** |  | 
**name** | **str** | The name of the OAuth 2 application | 
**client_id** | **str** | OAuth 2 client id | 
**client_secret** | **str** | OAuth 2 client secret. This is only returned when creating a new OAuth application. | [optional] 
**confidential** | **bool** | true, if OAuth 2 credentials are confidential, false, if no secret is stored | 
**created_at** | **datetime** | The time the OAuth 2 Application was created at | [optional] 
**updated_at** | **datetime** | The time the OAuth 2 Application was last updated | [optional] 
**scopes** | **List[str]** | An array of the scopes of the OAuth 2 Application | [optional] 
**links** | [**OAuthApplicationReadModelLinks**](OAuthApplicationReadModelLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.o_auth_application_read_model import OAuthApplicationReadModel

# TODO update the JSON string below
json = "{}"
# create an instance of OAuthApplicationReadModel from a JSON string
o_auth_application_read_model_instance = OAuthApplicationReadModel.from_json(json)
# print the JSON string representation of the object
print(OAuthApplicationReadModel.to_json())

# convert the object into a dict
o_auth_application_read_model_dict = o_auth_application_read_model_instance.to_dict()
# create an instance of OAuthApplicationReadModel from a dict
o_auth_application_read_model_from_dict = OAuthApplicationReadModel.from_dict(o_auth_application_read_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


