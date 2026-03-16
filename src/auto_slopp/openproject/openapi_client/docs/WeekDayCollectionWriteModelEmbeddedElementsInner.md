# WeekDayCollectionWriteModelEmbeddedElementsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**working** | **bool** | &#x60;true&#x60; for a working day. &#x60;false&#x60; for a weekend day. | 
**links** | [**WeekDaySelfLinkModel**](WeekDaySelfLinkModel.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.week_day_collection_write_model_embedded_elements_inner import WeekDayCollectionWriteModelEmbeddedElementsInner

# TODO update the JSON string below
json = "{}"
# create an instance of WeekDayCollectionWriteModelEmbeddedElementsInner from a JSON string
week_day_collection_write_model_embedded_elements_inner_instance = WeekDayCollectionWriteModelEmbeddedElementsInner.from_json(json)
# print the JSON string representation of the object
print(WeekDayCollectionWriteModelEmbeddedElementsInner.to_json())

# convert the object into a dict
week_day_collection_write_model_embedded_elements_inner_dict = week_day_collection_write_model_embedded_elements_inner_instance.to_dict()
# create an instance of WeekDayCollectionWriteModelEmbeddedElementsInner from a dict
week_day_collection_write_model_embedded_elements_inner_from_dict = WeekDayCollectionWriteModelEmbeddedElementsInner.from_dict(week_day_collection_write_model_embedded_elements_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


