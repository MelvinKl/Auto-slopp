# GridReadModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This grid.  **Resource**: Grid | 
**attachments** | [**Link**](Link.md) | The attachment collection of this grid.  **Resource**: AttachmentCollection | [optional] 
**add_attachment** | [**Link**](Link.md) | Link for adding an attachment to this grid. | [optional] 
**scope** | [**Link**](Link.md) | The location where this grid is used, usually represented as a relative URL. | 
**update_immediately** | [**Link**](Link.md) | Directly perform edits on this grid.  # Conditions  **Permission**: depends on the page the grid is defined for | [optional] 
**update** | [**Link**](Link.md) | Validate edits on the grid via a form resource before committing  # Conditions  **Permission**: depends on the page the grid is defined for | [optional] 
**delete** | [**Link**](Link.md) | Deletes this grid resource. | [optional] 

## Example

```python
from openproject_client.models.grid_read_model_links import GridReadModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of GridReadModelLinks from a JSON string
grid_read_model_links_instance = GridReadModelLinks.from_json(json)
# print the JSON string representation of the object
print(GridReadModelLinks.to_json())

# convert the object into a dict
grid_read_model_links_dict = grid_read_model_links_instance.to_dict()
# create an instance of GridReadModelLinks from a dict
grid_read_model_links_from_dict = GridReadModelLinks.from_dict(grid_read_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


