# WorkPackagesModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**WorkPackagesModelAllOfLinks**](WorkPackagesModelAllOfLinks.md) |  | 
**embedded** | [**WorkPackagesModelAllOfEmbedded**](WorkPackagesModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.work_packages_model import WorkPackagesModel

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackagesModel from a JSON string
work_packages_model_instance = WorkPackagesModel.from_json(json)
# print the JSON string representation of the object
print(WorkPackagesModel.to_json())

# convert the object into a dict
work_packages_model_dict = work_packages_model_instance.to_dict()
# create an instance of WorkPackagesModel from a dict
work_packages_model_from_dict = WorkPackagesModel.from_dict(work_packages_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


