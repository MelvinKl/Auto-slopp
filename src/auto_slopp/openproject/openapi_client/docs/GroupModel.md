# GroupModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | The principal&#39;s unique identifier. | 
**name** | **str** | The principal&#39;s display name, layout depends on instance settings. | 
**created_at** | **datetime** | Time of creation | [optional] 
**updated_at** | **datetime** | Time of the most recent change to the principal | [optional] 
**links** | [**GroupModelAllOfLinks**](GroupModelAllOfLinks.md) |  | 
**embedded** | [**GroupModelAllOfEmbedded**](GroupModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.group_model import GroupModel

# TODO update the JSON string below
json = "{}"
# create an instance of GroupModel from a JSON string
group_model_instance = GroupModel.from_json(json)
# print the JSON string representation of the object
print(GroupModel.to_json())

# convert the object into a dict
group_model_dict = group_model_instance.to_dict()
# create an instance of GroupModel from a dict
group_model_from_dict = GroupModel.from_dict(group_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


