# RevisionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Revision&#39;s id, assigned by OpenProject | [optional] [readonly] 
**identifier** | **str** | The raw SCM identifier of the revision (e.g. full SHA hash) | [readonly] 
**formatted_identifier** | **str** | The SCM identifier of the revision, formatted (e.g. shortened unambiguous SHA hash). May be identical to identifier in many cases | [readonly] 
**author_name** | **str** | The name of the author that committed this revision. Note that this name is retrieved from the repository and does not identify a user in OpenProject. | [readonly] 
**message** | [**Formattable**](Formattable.md) | The commit message of the revision | [readonly] 
**created_at** | **datetime** | The time this revision was committed to the repository | 
**links** | [**RevisionModelLinks**](RevisionModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.revision_model import RevisionModel

# TODO update the JSON string below
json = "{}"
# create an instance of RevisionModel from a JSON string
revision_model_instance = RevisionModel.from_json(json)
# print the JSON string representation of the object
print(RevisionModel.to_json())

# convert the object into a dict
revision_model_dict = revision_model_instance.to_dict()
# create an instance of RevisionModel from a dict
revision_model_from_dict = RevisionModel.from_dict(revision_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


