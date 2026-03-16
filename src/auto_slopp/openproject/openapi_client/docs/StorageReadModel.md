# StorageReadModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Storage id | 
**type** | **str** |  | 
**name** | **str** | Storage name | 
**storage_audience** | **str** | The audience that the storage expects in tokens for requests to it, usually the storage&#39;s client ID at the identity provider.  This is only required for authentication through single-sign-on and so far only supported for provider type Nextcloud. | [optional] 
**token_exchange_scope** | **str** | The scope that will be requested when requesting a token for the storage through token exchange. Has no effect if no token exchange is performed.  This is only required for authentication through single-sign-on and so far only supported for provider type Nextcloud. | [optional] 
**tenant_id** | **str** | The tenant id of a file storage of type OneDrive.  Ignored if the provider type is not OneDrive. May be null if the storage is not configured completely. | [optional] 
**drive_id** | **str** | The drive id of a file storage of type OneDrive.  Ignored if the provider type is not OneDrive. May be null if the storage is not configured completely. | [optional] 
**has_application_password** | **bool** | Whether the storage has the application password to use for the Nextcloud storage.  Ignored if the provider type is not Nextcloud. | [optional] 
**forbidden_file_name_characters** | **str** | A string with all the characters forbidden to be used for file and folder names in the storage. Used by OpenProject to avoid creating files with unsupported names (e.g. when creating project folders).  Only supported for provider type Nextcloud so far. | [optional] 
**created_at** | **datetime** | Time of creation | [optional] 
**updated_at** | **datetime** | Time of the most recent change to the storage | [optional] 
**configured** | **bool** | Indication, if the storage is fully configured | [optional] 
**embedded** | [**StorageReadModelEmbedded**](StorageReadModelEmbedded.md) |  | [optional] 
**links** | [**StorageReadModelLinks**](StorageReadModelLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.storage_read_model import StorageReadModel

# TODO update the JSON string below
json = "{}"
# create an instance of StorageReadModel from a JSON string
storage_read_model_instance = StorageReadModel.from_json(json)
# print the JSON string representation of the object
print(StorageReadModel.to_json())

# convert the object into a dict
storage_read_model_dict = storage_read_model_instance.to_dict()
# create an instance of StorageReadModel from a dict
storage_read_model_from_dict = StorageReadModel.from_dict(storage_read_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


