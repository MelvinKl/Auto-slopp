# RelationReadModelEmbedded


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_from** | [**WorkPackageModel**](WorkPackageModel.md) |  | [optional] 
**to** | [**WorkPackageModel**](WorkPackageModel.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.relation_read_model_embedded import RelationReadModelEmbedded

# TODO update the JSON string below
json = "{}"
# create an instance of RelationReadModelEmbedded from a JSON string
relation_read_model_embedded_instance = RelationReadModelEmbedded.from_json(json)
# print the JSON string representation of the object
print(RelationReadModelEmbedded.to_json())

# convert the object into a dict
relation_read_model_embedded_dict = relation_read_model_embedded_instance.to_dict()
# create an instance of RelationReadModelEmbedded from a dict
relation_read_model_embedded_from_dict = RelationReadModelEmbedded.from_dict(relation_read_model_embedded_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


