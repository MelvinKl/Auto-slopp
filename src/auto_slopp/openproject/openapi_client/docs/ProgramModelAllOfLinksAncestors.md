# ProgramModelAllOfLinksAncestors

A collection of links to the ancestor workspace.  **Resource**: Workspace

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
from auto_slopp.openproject.openapi_client.models.program_model_all_of_links_ancestors import ProgramModelAllOfLinksAncestors

# TODO update the JSON string below
json = "{}"
# create an instance of ProgramModelAllOfLinksAncestors from a JSON string
program_model_all_of_links_ancestors_instance = ProgramModelAllOfLinksAncestors.from_json(json)
# print the JSON string representation of the object
print(ProgramModelAllOfLinksAncestors.to_json())

# convert the object into a dict
program_model_all_of_links_ancestors_dict = program_model_all_of_links_ancestors_instance.to_dict()
# create an instance of ProgramModelAllOfLinksAncestors from a dict
program_model_all_of_links_ancestors_from_dict = ProgramModelAllOfLinksAncestors.from_dict(program_model_all_of_links_ancestors_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


