# StorageWriteModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**origin** | [**Link**](Link.md) | The storage&#39;s host URL.  **Resource**: N/A | 
**type** | [**Link**](Link.md) | The urn of the storage type. Currently Nextcloud and OneDrive storages are supported.  - urn:openproject-org:api:v3:storages:Nextcloud - urn:openproject-org:api:v3:storages:OneDrive  **Resource**: N/A | 
**authentication_method** | [**Link**](Link.md) | The urn of the authentication method. Currently only Nextcloud storages support this setting.  - urn:openproject-org:api:v3:storages:authenticationMethod:TwoWayOAuth2 (default) - urn:openproject-org:api:v3:storages:authenticationMethod:OAuth2SSO  **Resource**: N/A | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.storage_write_model_links import StorageWriteModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of StorageWriteModelLinks from a JSON string
storage_write_model_links_instance = StorageWriteModelLinks.from_json(json)
# print the JSON string representation of the object
print(StorageWriteModelLinks.to_json())

# convert the object into a dict
storage_write_model_links_dict = storage_write_model_links_instance.to_dict()
# create an instance of StorageWriteModelLinks from a dict
storage_write_model_links_from_dict = StorageWriteModelLinks.from_dict(storage_write_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


