# HelpTextCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**HelpTextCollectionModelAllOfLinks**](HelpTextCollectionModelAllOfLinks.md) |  | 
**embedded** | [**HelpTextCollectionModelAllOfEmbedded**](HelpTextCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.help_text_collection_model import HelpTextCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelpTextCollectionModel from a JSON string
help_text_collection_model_instance = HelpTextCollectionModel.from_json(json)
# print the JSON string representation of the object
print(HelpTextCollectionModel.to_json())

# convert the object into a dict
help_text_collection_model_dict = help_text_collection_model_instance.to_dict()
# create an instance of HelpTextCollectionModel from a dict
help_text_collection_model_from_dict = HelpTextCollectionModel.from_dict(help_text_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


