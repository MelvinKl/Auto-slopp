# FileLinkReadModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This file link.  **Resource**: FileLink | [optional] 
**storage** | [**Link**](Link.md) | The storage resource of the linked file.  **Resource**: Storage | [optional] 
**container** | [**Link**](Link.md) | The container the origin file is linked to.  Can be one of the following **Resources**:  - WorkPackage | [optional] 
**creator** | [**Link**](Link.md) | The creator of the file link.  **Resource**: User | [optional] 
**delete** | [**Link**](Link.md) | The uri to delete the file link.  **Resource**: N/A | [optional] 
**status** | [**Link**](Link.md) | The urn of the user specific file link status on its storage. Can be one of:  - urn:openproject-org:api:v3:file-links:permission:ViewAllowed - urn:openproject-org:api:v3:file-links:permission:ViewNotAllowed - urn:openproject-org:api:v3:file-links:NotFound - urn:openproject-org:api:v3:file-links:Error  **Resource**: N/A | [optional] 
**origin_open** | [**Link**](Link.md) | The uri to open the origin file on the origin itself.  **Resource**: N/A | [optional] 
**static_origin_open** | [**Link**](Link.md) | A static uri to open the origin file on the storage. Responds with a redirect.  **Resource**: N/A | [optional] 
**origin_open_location** | [**Link**](Link.md) | The uri to open the location of origin file on the origin itself.  **Resource**: N/A | [optional] 
**static_origin_open_location** | [**Link**](Link.md) | A static uri to open the location of the origin file on the storage. Responds with a redirect.  **Resource**: N/A | [optional] 
**static_origin_download** | [**Link**](Link.md) | A static uri to generate a new download URL from the storage. Responds with a redirect.  **Resource**: N/A | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.file_link_read_model_links import FileLinkReadModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of FileLinkReadModelLinks from a JSON string
file_link_read_model_links_instance = FileLinkReadModelLinks.from_json(json)
# print the JSON string representation of the object
print(FileLinkReadModelLinks.to_json())

# convert the object into a dict
file_link_read_model_links_dict = file_link_read_model_links_instance.to_dict()
# create an instance of FileLinkReadModelLinks from a dict
file_link_read_model_links_from_dict = FileLinkReadModelLinks.from_dict(file_link_read_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


