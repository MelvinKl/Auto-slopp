# RelationWriteModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**to** | [**Link**](Link.md) | The work package the relation ends in. Only available on relation creation, not on update.  **Resource**: WorkPackage  # Conditions  **Permission**: view work packages | [optional] 

## Example

```python
from openproject_client.models.relation_write_model_links import RelationWriteModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of RelationWriteModelLinks from a JSON string
relation_write_model_links_instance = RelationWriteModelLinks.from_json(json)
# print the JSON string representation of the object
print(RelationWriteModelLinks.to_json())

# convert the object into a dict
relation_write_model_links_dict = relation_write_model_links_instance.to_dict()
# create an instance of RelationWriteModelLinks from a dict
relation_write_model_links_from_dict = RelationWriteModelLinks.from_dict(relation_write_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


