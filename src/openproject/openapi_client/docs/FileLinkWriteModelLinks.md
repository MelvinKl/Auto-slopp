# FileLinkWriteModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**storage** | [**Link**](Link.md) | The storage resource of the linked file.  **Resource**: Storage | 
**storage_url** | [**Link**](Link.md) | The storage url the file link references to.  **Resource**: N/A | 

## Example

```python
from openproject_client.models.file_link_write_model_links import FileLinkWriteModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of FileLinkWriteModelLinks from a JSON string
file_link_write_model_links_instance = FileLinkWriteModelLinks.from_json(json)
# print the JSON string representation of the object
print(FileLinkWriteModelLinks.to_json())

# convert the object into a dict
file_link_write_model_links_dict = file_link_write_model_links_instance.to_dict()
# create an instance of FileLinkWriteModelLinks from a dict
file_link_write_model_links_from_dict = FileLinkWriteModelLinks.from_dict(file_link_write_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


