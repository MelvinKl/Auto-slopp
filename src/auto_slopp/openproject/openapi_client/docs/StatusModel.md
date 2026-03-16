# StatusModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**id** | **int** | Status id | [optional] 
**name** | **str** | Status name | [optional] 
**is_closed** | **bool** | Indicates, whether work package of this status are considered closed | [optional] 
**color** | **str** | The color of the status | [optional] 
**is_default** | **bool** | True, if this status is the default status for new work packages | [optional] 
**is_readonly** | **bool** | Indicates, whether work package of this status are readonly | [optional] 
**excluded_from_totals** | **bool** | Indicates, whether work package of this status are excluded from totals of &#x60;Work&#x60;, &#x60;Remaining work&#x60;, and &#x60;% Complete&#x60; in a hierarchy. | [optional] 
**default_done_ratio** | **int** | The percentageDone being applied when changing to this status | [optional] 
**position** | **int** | Sort index of the status | [optional] 
**links** | [**StatusModelLinks**](StatusModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.status_model import StatusModel

# TODO update the JSON string below
json = "{}"
# create an instance of StatusModel from a JSON string
status_model_instance = StatusModel.from_json(json)
# print the JSON string representation of the object
print(StatusModel.to_json())

# convert the object into a dict
status_model_dict = status_model_instance.to_dict()
# create an instance of StatusModel from a dict
status_model_from_dict = StatusModel.from_dict(status_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


