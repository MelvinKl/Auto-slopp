# RevisionModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This revision  **Resource**: Revision | [readonly] 
**project** | [**Link**](Link.md) | The project to which the revision belongs  **Resource**: Project | [readonly] 
**author** | [**Link**](Link.md) | The user that added this revision, if the authorName was mapped to a user in OpenProject  **Resource**: User | [optional] [readonly] 
**show_revision** | [**Link**](Link.md) | A URL to the repository view (outside APIv3) showing this revision  **Resource**: - | [readonly] 

## Example

```python
from openproject_client.models.revision_model_links import RevisionModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of RevisionModelLinks from a JSON string
revision_model_links_instance = RevisionModelLinks.from_json(json)
# print the JSON string representation of the object
print(RevisionModelLinks.to_json())

# convert the object into a dict
revision_model_links_dict = revision_model_links_instance.to_dict()
# create an instance of RevisionModelLinks from a dict
revision_model_links_from_dict = RevisionModelLinks.from_dict(revision_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


