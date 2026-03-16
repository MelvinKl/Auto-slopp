# StorageReadModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This storage resource. Contains the user defined storage name as title.  **Resource**: Storage | 
**type** | [**Link**](Link.md) | The urn of the storage type. Currently Nextcloud and OneDrive storages are supported.  - urn:openproject-org:api:v3:storages:Nextcloud - urn:openproject-org:api:v3:storages:OneDrive  **Resource**: N/A | 
**authentication_method** | [**Link**](Link.md) | The urn of the authentication method. Currently only Nextcloud storages support this setting.  - urn:openproject-org:api:v3:storages:authenticationMethod:TwoWayOAuth2 (default) - urn:openproject-org:api:v3:storages:authenticationMethod:OAuth2SSO  **Resource**: N/A | [optional] 
**origin** | [**Link**](Link.md) | Web URI of the storage instance. This link is ignored, if the storage is hosted in a cloud and has no own URL, like file storages of type OneDrive.  **Resource**: N/A | [optional] 
**open** | [**Link**](Link.md) | URI of the file storage location, from where the user usually starts browsing files.  **Resource**: N/A | 
**authorization_state** | [**Link**](Link.md) | The urn of the storage connection state. Can be one of:  - urn:openproject-org:api:v3:storages:authorization:Connected - urn:openproject-org:api:v3:storages:authorization:FailedAuthorization - urn:openproject-org:api:v3:storages:authorization:Error  **Resource**: N/A | 
**authorize** | [**Link**](Link.md) | The link to the starting point of the authorization cycle for a configured storage provider.  # Conditions  &#x60;authorizationState&#x60; is:  - urn:openproject-org:api:v3:storages:authorization:FailedAuthorization  **Resource**: N/A | [optional] 
**oauth_application** | [**Link**](Link.md) | The OAuth 2 provider application linked to the storage.  # Conditions  - User has role &#x60;admin&#x60;  **Resource**: OAuthApplication | [optional] 
**oauth_client_credentials** | [**Link**](Link.md) | The OAuth 2 credentials resource linked to the storage.  # Conditions  - User has role &#x60;admin&#x60;  **Resource**: OAuthClientCredentials | [optional] 

## Example

```python
from openproject_client.models.storage_read_model_links import StorageReadModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of StorageReadModelLinks from a JSON string
storage_read_model_links_instance = StorageReadModelLinks.from_json(json)
# print the JSON string representation of the object
print(StorageReadModelLinks.to_json())

# convert the object into a dict
storage_read_model_links_dict = storage_read_model_links_instance.to_dict()
# create an instance of StorageReadModelLinks from a dict
storage_read_model_links_from_dict = StorageReadModelLinks.from_dict(storage_read_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


