# StorageReadModelEmbedded


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**oauth_application** | [**OAuthApplicationReadModel**](OAuthApplicationReadModel.md) |  | [optional] 
**oauth_client_credentials** | [**OAuthClientCredentialsReadModel**](OAuthClientCredentialsReadModel.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.storage_read_model_embedded import StorageReadModelEmbedded

# TODO update the JSON string below
json = "{}"
# create an instance of StorageReadModelEmbedded from a JSON string
storage_read_model_embedded_instance = StorageReadModelEmbedded.from_json(json)
# print the JSON string representation of the object
print(StorageReadModelEmbedded.to_json())

# convert the object into a dict
storage_read_model_embedded_dict = storage_read_model_embedded_instance.to_dict()
# create an instance of StorageReadModelEmbedded from a dict
storage_read_model_embedded_from_dict = StorageReadModelEmbedded.from_dict(storage_read_model_embedded_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


