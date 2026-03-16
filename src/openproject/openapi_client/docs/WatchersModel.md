# WatchersModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**WatchersModelAllOfLinks**](WatchersModelAllOfLinks.md) |  | 
**embedded** | [**WatchersModelAllOfEmbedded**](WatchersModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.watchers_model import WatchersModel

# TODO update the JSON string below
json = "{}"
# create an instance of WatchersModel from a JSON string
watchers_model_instance = WatchersModel.from_json(json)
# print the JSON string representation of the object
print(WatchersModel.to_json())

# convert the object into a dict
watchers_model_dict = watchers_model_instance.to_dict()
# create an instance of WatchersModel from a dict
watchers_model_from_dict = WatchersModel.from_dict(watchers_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


