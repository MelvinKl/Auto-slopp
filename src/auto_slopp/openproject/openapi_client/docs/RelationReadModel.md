# RelationReadModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**id** | **int** | Relation ID | [optional] 
**name** | **str** | The internationalised name of this type of relation | [optional] 
**type** | **str** | The relation type. | [optional] 
**reverse_type** | **str** | The type of relation from the perspective of the related work package. | [optional] 
**description** | **str** | A descriptive text for the relation. | [optional] 
**lag** | **int** | The lag in days between closing of &#x60;from&#x60; and start of &#x60;to&#x60; | [optional] 
**embedded** | [**RelationReadModelEmbedded**](RelationReadModelEmbedded.md) |  | [optional] 
**links** | [**RelationReadModelLinks**](RelationReadModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.relation_read_model import RelationReadModel

# TODO update the JSON string below
json = "{}"
# create an instance of RelationReadModel from a JSON string
relation_read_model_instance = RelationReadModel.from_json(json)
# print the JSON string representation of the object
print(RelationReadModel.to_json())

# convert the object into a dict
relation_read_model_dict = relation_read_model_instance.to_dict()
# create an instance of RelationReadModel from a dict
relation_read_model_from_dict = RelationReadModel.from_dict(relation_read_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


