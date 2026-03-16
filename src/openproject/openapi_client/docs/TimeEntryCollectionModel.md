# TimeEntryCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**TimeEntryCollectionModelAllOfLinks**](TimeEntryCollectionModelAllOfLinks.md) |  | 
**embedded** | [**TimeEntryCollectionModelAllOfEmbedded**](TimeEntryCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.time_entry_collection_model import TimeEntryCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of TimeEntryCollectionModel from a JSON string
time_entry_collection_model_instance = TimeEntryCollectionModel.from_json(json)
# print the JSON string representation of the object
print(TimeEntryCollectionModel.to_json())

# convert the object into a dict
time_entry_collection_model_dict = time_entry_collection_model_instance.to_dict()
# create an instance of TimeEntryCollectionModel from a dict
time_entry_collection_model_from_dict = TimeEntryCollectionModel.from_dict(time_entry_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


