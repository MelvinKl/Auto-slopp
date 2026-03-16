# WorkPackageModelAllOfLinksChildren

A visible child work package of the current work package.  **Resource**: WorkPackage  # Conditions  **Permission** view work packages

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
from auto_slopp.openproject.openapi_client.models.work_package_model_all_of_links_children import WorkPackageModelAllOfLinksChildren

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackageModelAllOfLinksChildren from a JSON string
work_package_model_all_of_links_children_instance = WorkPackageModelAllOfLinksChildren.from_json(json)
# print the JSON string representation of the object
print(WorkPackageModelAllOfLinksChildren.to_json())

# convert the object into a dict
work_package_model_all_of_links_children_dict = work_package_model_all_of_links_children_instance.to_dict()
# create an instance of WorkPackageModelAllOfLinksChildren from a dict
work_package_model_all_of_links_children_from_dict = WorkPackageModelAllOfLinksChildren.from_dict(work_package_model_all_of_links_children_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


