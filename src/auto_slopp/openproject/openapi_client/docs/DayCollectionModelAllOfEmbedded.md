# DayCollectionModelAllOfEmbedded


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**elements** | [**List[DayModel]**](DayModel.md) | The array of days. Each day has a name and a working status indicating if it is a working or a non-working day. | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.day_collection_model_all_of_embedded import DayCollectionModelAllOfEmbedded

# TODO update the JSON string below
json = "{}"
# create an instance of DayCollectionModelAllOfEmbedded from a JSON string
day_collection_model_all_of_embedded_instance = DayCollectionModelAllOfEmbedded.from_json(json)
# print the JSON string representation of the object
print(DayCollectionModelAllOfEmbedded.to_json())

# convert the object into a dict
day_collection_model_all_of_embedded_dict = day_collection_model_all_of_embedded_instance.to_dict()
# create an instance of DayCollectionModelAllOfEmbedded from a dict
day_collection_model_all_of_embedded_from_dict = DayCollectionModelAllOfEmbedded.from_dict(day_collection_model_all_of_embedded_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


