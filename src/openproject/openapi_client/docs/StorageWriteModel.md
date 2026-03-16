# StorageWriteModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Storage name, if not provided, falls back to a default. | [optional] 
**storage_audience** | **str** | The audience that the storage expects in tokens for requests to it, usually the storage&#39;s client ID at the identity provider.  This is only required for authentication through single-sign-on and so far only supported for provider type Nextcloud. | [optional] 
**token_exchange_scope** | **str** | The scope that will be requested when requesting a token for the storage through token exchange. Has no effect if no token exchange is performed.  This is only required for authentication through single-sign-on and so far only supported for provider type Nextcloud. | [optional] 
**application_password** | **str** | The application password to use for the Nextcloud storage. Ignored if the provider type is not Nextcloud.  If a string is provided, the password is set and automatic management is enabled for the storage. If null is provided, the password is unset and automatic management is disabled for the storage. | [optional] 
**forbidden_file_name_characters** | **str** | A string with all the characters forbidden to be used for file and folder names in the storage. Used by OpenProject to avoid creating files with unsupported names (e.g. when creating project folders).  Only supported for provider type Nextcloud so far. | [optional] 
**links** | [**StorageWriteModelLinks**](StorageWriteModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.storage_write_model import StorageWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of StorageWriteModel from a JSON string
storage_write_model_instance = StorageWriteModel.from_json(json)
# print the JSON string representation of the object
print(StorageWriteModel.to_json())

# convert the object into a dict
storage_write_model_dict = storage_write_model_instance.to_dict()
# create an instance of StorageWriteModel from a dict
storage_write_model_from_dict = StorageWriteModel.from_dict(storage_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


