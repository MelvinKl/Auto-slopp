# DayModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**var_date** | **date** | Date of the day. | 
**name** | **str** | Descriptive name for the day. | 
**working** | **bool** | &#x60;true&#x60; for a working day, &#x60;false&#x60; otherwise. | 
**links** | [**DayModelLinks**](DayModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.day_model import DayModel

# TODO update the JSON string below
json = "{}"
# create an instance of DayModel from a JSON string
day_model_instance = DayModel.from_json(json)
# print the JSON string representation of the object
print(DayModel.to_json())

# convert the object into a dict
day_model_dict = day_model_instance.to_dict()
# create an instance of DayModel from a dict
day_model_from_dict = DayModel.from_dict(day_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


