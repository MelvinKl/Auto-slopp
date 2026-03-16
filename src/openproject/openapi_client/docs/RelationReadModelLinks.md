# RelationReadModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This relation  **Resource**: Relation  # Conditions  **Permission**: view work packages | [optional] 
**update_immediately** | [**Link**](Link.md) | Updates the relation between two work packages  # Conditions  **Permission**: manage work package relations | [optional] 
**delete** | [**Link**](Link.md) | Destroys the relation between the two work packages  # Conditions  **Permission**: manage work package relations | [optional] 
**var_from** | [**Link**](Link.md) | The emanating work package  **Resource**: WorkPackage  # Conditions  **Permission**: view work packages | [optional] 
**to** | [**Link**](Link.md) | The work package the relation ends in  **Resource**: WorkPackage  # Conditions  **Permission**: view work packages | [optional] 

## Example

```python
from openproject_client.models.relation_read_model_links import RelationReadModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of RelationReadModelLinks from a JSON string
relation_read_model_links_instance = RelationReadModelLinks.from_json(json)
# print the JSON string representation of the object
print(RelationReadModelLinks.to_json())

# convert the object into a dict
relation_read_model_links_dict = relation_read_model_links_instance.to_dict()
# create an instance of RelationReadModelLinks from a dict
relation_read_model_links_from_dict = RelationReadModelLinks.from_dict(relation_read_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


