# QueryModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Query id | [optional] [readonly] 
**name** | **str** | Query name | [optional] [readonly] 
**filters** | [**List[QueryFilterInstanceModel]**](QueryFilterInstanceModel.md) | A set of QueryFilters which will be applied to the work packages to determine the resulting work packages | [optional] 
**sums** | **bool** | Should sums (of supported properties) be shown? | [optional] [readonly] 
**timeline_visible** | **bool** | Should the timeline mode be shown? | [optional] [readonly] 
**timeline_labels** | **List[str]** | Which labels are shown in the timeline, empty when default | [optional] [readonly] 
**timeline_zoom_level** | **str** | Which zoom level should the timeline be rendered in? | [optional] [readonly] 
**timestamps** | **List[object]** | Timestamps to filter by when showing changed attributes on work packages. | [optional] 
**highlighting_mode** | **str** | Which highlighting mode should the table have? | [optional] [readonly] 
**show_hierarchies** | **bool** | Should the hierarchy mode be enabled? | [optional] [readonly] 
**hidden** | **bool** | Should the query be hidden from the query list? | [optional] [readonly] 
**public** | **bool** | Can users besides the owner see the query? | [optional] [readonly] 
**starred** | **bool** | Should the query be highlighted to the user? | [optional] [readonly] 
**created_at** | **datetime** | Time of creation | [readonly] 
**updated_at** | **datetime** | Time of the most recent change to the query | [readonly] 
**links** | [**QueryModelLinks**](QueryModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.query_model import QueryModel

# TODO update the JSON string below
json = "{}"
# create an instance of QueryModel from a JSON string
query_model_instance = QueryModel.from_json(json)
# print the JSON string representation of the object
print(QueryModel.to_json())

# convert the object into a dict
query_model_dict = query_model_instance.to_dict()
# create an instance of QueryModel from a dict
query_model_from_dict = QueryModel.from_dict(query_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


