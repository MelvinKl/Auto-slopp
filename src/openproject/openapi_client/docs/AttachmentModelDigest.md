# AttachmentModelDigest

A checksum for the files content

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**algorithm** | **str** | The algorithm used to generate the digest. | 
**hash** | **str** | The hexadecimal representation of the digested hash value. | 

## Example

```python
from openproject_client.models.attachment_model_digest import AttachmentModelDigest

# TODO update the JSON string below
json = "{}"
# create an instance of AttachmentModelDigest from a JSON string
attachment_model_digest_instance = AttachmentModelDigest.from_json(json)
# print the JSON string representation of the object
print(AttachmentModelDigest.to_json())

# convert the object into a dict
attachment_model_digest_dict = attachment_model_digest_instance.to_dict()
# create an instance of AttachmentModelDigest from a dict
attachment_model_digest_from_dict = AttachmentModelDigest.from_dict(attachment_model_digest_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


