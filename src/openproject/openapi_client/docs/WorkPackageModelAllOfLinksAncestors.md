# WorkPackageModelAllOfLinksAncestors

A visible ancestor work package of the current work package.  **Resource**: WorkPackage  # Conditions  **Permission** view work packages

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

## Example

```python
from openproject_client.models.work_package_model_all_of_links_ancestors import WorkPackageModelAllOfLinksAncestors

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackageModelAllOfLinksAncestors from a JSON string
work_package_model_all_of_links_ancestors_instance = WorkPackageModelAllOfLinksAncestors.from_json(json)
# print the JSON string representation of the object
print(WorkPackageModelAllOfLinksAncestors.to_json())

# convert the object into a dict
work_package_model_all_of_links_ancestors_dict = work_package_model_all_of_links_ancestors_instance.to_dict()
# create an instance of WorkPackageModelAllOfLinksAncestors from a dict
work_package_model_all_of_links_ancestors_from_dict = WorkPackageModelAllOfLinksAncestors.from_dict(work_package_model_all_of_links_ancestors_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


