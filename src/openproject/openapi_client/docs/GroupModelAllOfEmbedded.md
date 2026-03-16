# GroupModelAllOfEmbedded


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**members** | [**List[UserModel]**](UserModel.md) | Embedded list of members. | [optional] 

## Example

```python
from openproject_client.models.group_model_all_of_embedded import GroupModelAllOfEmbedded

# TODO update the JSON string below
json = "{}"
# create an instance of GroupModelAllOfEmbedded from a JSON string
group_model_all_of_embedded_instance = GroupModelAllOfEmbedded.from_json(json)
# print the JSON string representation of the object
print(GroupModelAllOfEmbedded.to_json())

# convert the object into a dict
group_model_all_of_embedded_dict = group_model_all_of_embedded_instance.to_dict()
# create an instance of GroupModelAllOfEmbedded from a dict
group_model_all_of_embedded_from_dict = GroupModelAllOfEmbedded.from_dict(group_model_all_of_embedded_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


