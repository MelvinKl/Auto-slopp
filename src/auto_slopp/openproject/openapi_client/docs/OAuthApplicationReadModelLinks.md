# OAuthApplicationReadModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This OAuth application  **Resource**: OAuthApplication | 
**owner** | [**Link**](Link.md) | The user that created the OAuth application.  **Resource**: User | 
**integration** | [**Link**](Link.md) | The resource that integrates this OAuth application into itself. Currently, only &#x60;Storage&#x60; resources are able to create and maintain own OAuth application.  **Resource**: Storage | [optional] 
**redirect_uri** | [**List[Link]**](Link.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.o_auth_application_read_model_links import OAuthApplicationReadModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of OAuthApplicationReadModelLinks from a JSON string
o_auth_application_read_model_links_instance = OAuthApplicationReadModelLinks.from_json(json)
# print the JSON string representation of the object
print(OAuthApplicationReadModelLinks.to_json())

# convert the object into a dict
o_auth_application_read_model_links_dict = o_auth_application_read_model_links_instance.to_dict()
# create an instance of OAuthApplicationReadModelLinks from a dict
o_auth_application_read_model_links_from_dict = OAuthApplicationReadModelLinks.from_dict(o_auth_application_read_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


