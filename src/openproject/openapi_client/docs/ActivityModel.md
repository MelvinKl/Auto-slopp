# ActivityModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**id** | **int** | Activity id | [optional] 
**version** | **int** | Activity version | [optional] 
**comment** | [**Formattable**](Formattable.md) |  | [optional] 
**details** | [**List[Formattable]**](Formattable.md) |  | [optional] 
**internal** | **bool** | Whether this activity is internal (only visible to users with view_internal_comments permission) | [optional] 
**created_at** | **datetime** | Time of creation | [optional] 
**updated_at** | **datetime** | Time of update | [optional] 
**embedded** | [**ActivityModelEmbedded**](ActivityModelEmbedded.md) |  | [optional] 
**links** | [**ActivityModelLinks**](ActivityModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.activity_model import ActivityModel

# TODO update the JSON string below
json = "{}"
# create an instance of ActivityModel from a JSON string
activity_model_instance = ActivityModel.from_json(json)
# print the JSON string representation of the object
print(ActivityModel.to_json())

# convert the object into a dict
activity_model_dict = activity_model_instance.to_dict()
# create an instance of ActivityModel from a dict
activity_model_from_dict = ActivityModel.from_dict(activity_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


