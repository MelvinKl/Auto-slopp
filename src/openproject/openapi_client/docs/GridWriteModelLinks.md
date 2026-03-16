# GridWriteModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**scope** | [**Link**](Link.md) | The location where this grid is used, usually represented as a relative URL. | [optional] 

## Example

```python
from openproject_client.models.grid_write_model_links import GridWriteModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of GridWriteModelLinks from a JSON string
grid_write_model_links_instance = GridWriteModelLinks.from_json(json)
# print the JSON string representation of the object
print(GridWriteModelLinks.to_json())

# convert the object into a dict
grid_write_model_links_dict = grid_write_model_links_instance.to_dict()
# create an instance of GridWriteModelLinks from a dict
grid_write_model_links_from_dict = GridWriteModelLinks.from_dict(grid_write_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


