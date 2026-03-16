# PriorityCollectionModelAllOfLinksSelf


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**href** | **str** | URL to the referenced resource (might be relative) | 
**title** | **str** | Representative label for the resource | [optional] 
**templated** | **bool** | If true the href contains parts that need to be replaced by the client | [optional] [default to False]
**method** | **str** | The HTTP verb to use when requesting the resource | [optional] [default to 'GET']
**payload** | **object** | The payload to send in the request to achieve the desired result | [optional] 
**identifier** | **str** | An optional unique identifier to the link object | [optional] 
**type** | **str** | The MIME-Type of the returned resource. | [optional] 
**var_self** | [**Link**](Link.md) | This priority collection  **Resource**: PriorityCollectionModel | [optional] 

## Example

```python
from openproject_client.models.priority_collection_model_all_of_links_self import PriorityCollectionModelAllOfLinksSelf

# TODO update the JSON string below
json = "{}"
# create an instance of PriorityCollectionModelAllOfLinksSelf from a JSON string
priority_collection_model_all_of_links_self_instance = PriorityCollectionModelAllOfLinksSelf.from_json(json)
# print the JSON string representation of the object
print(PriorityCollectionModelAllOfLinksSelf.to_json())

# convert the object into a dict
priority_collection_model_all_of_links_self_dict = priority_collection_model_all_of_links_self_instance.to_dict()
# create an instance of PriorityCollectionModelAllOfLinksSelf from a dict
priority_collection_model_all_of_links_self_from_dict = PriorityCollectionModelAllOfLinksSelf.from_dict(priority_collection_model_all_of_links_self_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


