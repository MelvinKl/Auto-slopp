# PostModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**add_attachment** | [**Link**](Link.md) | Attach a file to the post  # Conditions  **Permission**: edit messages | [optional] [readonly] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.post_model_links import PostModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of PostModelLinks from a JSON string
post_model_links_instance = PostModelLinks.from_json(json)
# print the JSON string representation of the object
print(PostModelLinks.to_json())

# convert the object into a dict
post_model_links_dict = post_model_links_instance.to_dict()
# create an instance of PostModelLinks from a dict
post_model_links_from_dict = PostModelLinks.from_dict(post_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


