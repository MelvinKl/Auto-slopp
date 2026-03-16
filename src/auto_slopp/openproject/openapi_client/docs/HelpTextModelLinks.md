# HelpTextModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This help text resource.  **Resource**: HelpText | 
**edit_text** | [**Link**](Link.md) | Edit the help text entry.  **Resource**: text/html | 
**attachments** | [**Link**](Link.md) | The attachment collection of this help text.  **Resource**: AttachmentCollection | 
**add_attachment** | [**Link**](Link.md) | Add an attachment to the help text. | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.help_text_model_links import HelpTextModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of HelpTextModelLinks from a JSON string
help_text_model_links_instance = HelpTextModelLinks.from_json(json)
# print the JSON string representation of the object
print(HelpTextModelLinks.to_json())

# convert the object into a dict
help_text_model_links_dict = help_text_model_links_instance.to_dict()
# create an instance of HelpTextModelLinks from a dict
help_text_model_links_from_dict = HelpTextModelLinks.from_dict(help_text_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


