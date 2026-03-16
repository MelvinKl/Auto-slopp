# PrincipalModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | The principal&#39;s unique identifier. | 
**name** | **str** | The principal&#39;s display name, layout depends on instance settings. | 
**created_at** | **datetime** | Time of creation | [optional] 
**updated_at** | **datetime** | Time of the most recent change to the principal | [optional] 
**links** | [**PrincipalModelLinks**](PrincipalModelLinks.md) |  | 

## Example

```python
from openproject_client.models.principal_model import PrincipalModel

# TODO update the JSON string below
json = "{}"
# create an instance of PrincipalModel from a JSON string
principal_model_instance = PrincipalModel.from_json(json)
# print the JSON string representation of the object
print(PrincipalModel.to_json())

# convert the object into a dict
principal_model_dict = principal_model_instance.to_dict()
# create an instance of PrincipalModel from a dict
principal_model_from_dict = PrincipalModel.from_dict(principal_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


