# StorageFileUploadLinkModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | The resource link of the upload link resource.  As the upload link is a temporal object, and cannot be retrieved again, the self link usually is &#x60;urn:openproject-org:api:v3:storages:upload_link:no_link_provided&#x60;.  **Resource**: UploadLink | 
**destination** | [**Link**](Link.md) | The direct upload link.  **Resource**: N/A | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.storage_file_upload_link_model_links import StorageFileUploadLinkModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of StorageFileUploadLinkModelLinks from a JSON string
storage_file_upload_link_model_links_instance = StorageFileUploadLinkModelLinks.from_json(json)
# print the JSON string representation of the object
print(StorageFileUploadLinkModelLinks.to_json())

# convert the object into a dict
storage_file_upload_link_model_links_dict = storage_file_upload_link_model_links_instance.to_dict()
# create an instance of StorageFileUploadLinkModelLinks from a dict
storage_file_upload_link_model_links_from_dict = StorageFileUploadLinkModelLinks.from_dict(storage_file_upload_link_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


