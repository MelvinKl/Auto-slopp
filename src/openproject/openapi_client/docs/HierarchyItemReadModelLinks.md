# HierarchyItemReadModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This hierarchy item  **Resource**: HierarchyItem | 
**parent** | [**Link**](Link.md) | The hierarchy item that is the parent of the current hierarchy item  **Resource**: HierarchyItem | [optional] 
**children** | [**List[Link]**](Link.md) |  | 
**branch** | [**Link**](Link.md) | The branch of the hierarchy item, ordered from root to node.  **Resource**: HierarchyItemCollection | 

## Example

```python
from openproject_client.models.hierarchy_item_read_model_links import HierarchyItemReadModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of HierarchyItemReadModelLinks from a JSON string
hierarchy_item_read_model_links_instance = HierarchyItemReadModelLinks.from_json(json)
# print the JSON string representation of the object
print(HierarchyItemReadModelLinks.to_json())

# convert the object into a dict
hierarchy_item_read_model_links_dict = hierarchy_item_read_model_links_instance.to_dict()
# create an instance of HierarchyItemReadModelLinks from a dict
hierarchy_item_read_model_links_from_dict = HierarchyItemReadModelLinks.from_dict(hierarchy_item_read_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


