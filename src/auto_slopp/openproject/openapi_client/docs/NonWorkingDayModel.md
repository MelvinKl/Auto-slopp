# NonWorkingDayModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**var_date** | **date** | Date of the non-working day. | 
**name** | **str** | Descriptive name for the non-working day. | 
**links** | [**NonWorkingDayModelLinks**](NonWorkingDayModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.non_working_day_model import NonWorkingDayModel

# TODO update the JSON string below
json = "{}"
# create an instance of NonWorkingDayModel from a JSON string
non_working_day_model_instance = NonWorkingDayModel.from_json(json)
# print the JSON string representation of the object
print(NonWorkingDayModel.to_json())

# convert the object into a dict
non_working_day_model_dict = non_working_day_model_instance.to_dict()
# create an instance of NonWorkingDayModel from a dict
non_working_day_model_from_dict = NonWorkingDayModel.from_dict(non_working_day_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


