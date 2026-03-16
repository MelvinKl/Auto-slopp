# RelationWriteModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** | The relation type. | 
**description** | **str** | A descriptive text for the relation. | [optional] 
**lag** | **int** | The lag in days between closing of &#x60;from&#x60; and start of &#x60;to&#x60; | [optional] 
**links** | [**RelationWriteModelLinks**](RelationWriteModelLinks.md) |  | 

## Example

```python
from openproject_client.models.relation_write_model import RelationWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of RelationWriteModel from a JSON string
relation_write_model_instance = RelationWriteModel.from_json(json)
# print the JSON string representation of the object
print(RelationWriteModel.to_json())

# convert the object into a dict
relation_write_model_dict = relation_write_model_instance.to_dict()
# create an instance of RelationWriteModel from a dict
relation_write_model_from_dict = RelationWriteModel.from_dict(relation_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


