# auto-slopp.openproject.openapi-client
You're looking at the current **stable** documentation of the OpenProject APIv3. If you're interested in the current development version, please go to [github.com/opf](https://github.com/opf/openproject/tree/dev/docs/api/apiv3).  ## Introduction  The documentation for the APIv3 is written according to the [OpenAPI 3.1 Specification](https://swagger.io/specification/). You can either view the static version of this documentation on the [website](https://www.openproject.org/docs/api/introduction/) or the interactive version, rendered with [OpenAPI Explorer](https://github.com/Rhosys/openapi-explorer/blob/main/README.md), in your OpenProject installation under `/api/docs`. In the latter you can try out the various API endpoints directly interacting with our OpenProject data. Moreover you can access the specification source itself under `/api/v3/spec.json` and `/api/v3/spec.yml` (e.g. [here](https://community.openproject.org/api/v3/spec.yml)).  The APIv3 is a hypermedia REST API, a shorthand for \"Hypermedia As The Engine Of Application State\" (HATEOAS). This means that each endpoint of this API will have links to other resources or actions defined in the resulting body.  These related resources and actions for any given resource will be context sensitive. For example, only actions that the authenticated user can take are being rendered. This can be used to dynamically identify actions that the user might take for any given response.  As an example, if you fetch a work package through the [Work Package endpoint](https://www.openproject.org/docs/api/endpoints/work-packages/), the `update` link will only be present when the user you authenticated has been granted a permission to update the work package in the assigned project.  ## HAL+JSON  HAL is a simple format that gives a consistent and easy way to hyperlink between resources in your API. Read more in the following specification: [https://tools.ietf.org/html/draft-kelly-json-hal-08](https://tools.ietf.org/html/draft-kelly-json-hal-08)  **OpenProject API implementation of HAL+JSON format** enriches JSON and introduces a few meta properties:  - `_type` - specifies the type of the resource (e.g.: WorkPackage, Project) - `_links` - contains all related resource and action links available for the resource - `_embedded` - contains all embedded objects  HAL does not guarantee that embedded resources are embedded in their full representation, they might as well be partially represented (e.g. some properties can be left out). However in this API you have the guarantee that whenever a resource is **embedded**, it is embedded in its **full representation**.  ## API response structure  All API responses contain a single HAL+JSON object, even collections of objects are technically represented by a single HAL+JSON object that itself contains its members. More details on collections can be found in the [Collections Section](https://www.openproject.org/docs/api/collections/).  ## Authentication  The API supports the following authentication schemes:  * Session-based authentication * API tokens     * passed as Bearer token     * passed via Basic auth * OAuth 2.0     * using built-in authorization server     * using an external authorization server (RFC 9068)  Depending on the settings of the OpenProject instance many resources can be accessed without being authenticated. In case the instance requires authentication on all requests the client will receive an **HTTP 401** status code in response to any request.  Otherwise unauthenticated clients have all the permissions of the anonymous user.  ### Session-based authentication  This means you have to login to OpenProject via the Web-Interface to be authenticated in the API. This method is well-suited for clients acting within the browser, like the Angular-Client built into OpenProject.  In this case, you always need to pass the HTTP header `X-Requested-With \"XMLHttpRequest\"` for authentication.  ### API token as bearer token  Users can authenticate towards the API v3 using an API token as a bearer token.  For example:  ```shell API_KEY=opapi-2519132cdf62dcf5a66fd96394672079f9e9cad1 curl -H \"Authorization: Bearer $API_KEY\" https://community.openproject.org/api/v3/users/42 ```  Users can generate API tokens on their account page.  ### API token through Basic Auth  API tokens can also be used with basic auth, using the user name `apikey` (NOT your login) and the API token as the password.  For example:  ```shell API_KEY=opapi-2519132cdf62dcf5a66fd96394672079f9e9cad1 curl -u apikey:$API_KEY https://community.openproject.org/api/v3/users/42 ```  ### OAuth 2.0 authentication  OpenProject allows authentication and authorization with OAuth2 with *Authorization code flow*, as well as *Client credentials* operation modes.  To get started, you first need to register an application in the OpenProject OAuth administration section of your installation. This will save an entry for your application with a client unique identifier (`client_id`) and an accompanying secret key (`client_secret`).  You can then use one the following guides to perform the supported OAuth 2.0 flows:  - [Authorization code flow](https://oauth.net/2/grant-types/authorization-code)  - [Authorization code flow with PKCE](https://doorkeeper.gitbook.io/guides/ruby-on-rails/pkce-flow), recommended for clients unable to keep the client_secret confidential  - [Client credentials](https://oauth.net/2/grant-types/client-credentials/) - Requires an application to be bound to an impersonating user for non-public access  ### OAuth 2.0 using an external authorization server  There is a possibility to use JSON Web Tokens (JWT) generated by an OIDC provider configured in OpenProject as a bearer token to do authenticated requests against the API. The following requirements must be met:  - OIDC provider must be configured in OpenProject with **jwks_uri** - JWT must be signed using RSA algorithm - JWT **iss** claim must be equal to OIDC provider **issuer** - JWT **aud** claim must contain the OpenProject **client ID** used at the OIDC provider - JWT **scope** claim must include a valid scope to access the desired API (e.g. `api_v3` for APIv3) - JWT must be actual (neither expired or too early to be used) - JWT must be passed in Authorization header like: `Authorization: Bearer {jwt}` - User from **sub** claim must be linked to OpenProject before (e.g. by logging in), otherwise it will be not authenticated  In more general terms, OpenProject should be compliant to [RFC 9068](https://www.rfc-editor.org/rfc/rfc9068) when validating access tokens.  ### Why not username and password?  The simplest way to do basic auth would be to use a user's username and password naturally. However, OpenProject already has supported API keys in the past for the API v2, though not through basic auth.  Using **username and password** directly would have some advantages:  * It is intuitive for the user who then just has to provide those just as they would when logging into OpenProject.  * No extra logic for token management necessary.  On the other hand using **API keys** has some advantages too, which is why we went for that:  * If compromised while saved on an insecure client the user only has to regenerate the API key instead of changing their password, too.  * They are naturally long and random which makes them invulnerable to dictionary attacks and harder to crack in general.  Most importantly users may not actually have a password to begin with. Specifically when they have registered through an OpenID Connect provider.  ## Cross-Origin Resource Sharing (CORS)  By default, the OpenProject API is _not_ responding with any CORS headers. If you want to allow cross-domain AJAX calls against your OpenProject instance, you need to enable CORS headers being returned.  Please see [our API settings documentation](https://www.openproject.org/docs/system-admin-guide/api-and-webhooks/) on how to selectively enable CORS.  ## Allowed HTTP methods  - `GET` - Get a single resource or collection of resources  - `POST` - Create a new resource or perform  - `PATCH` - Update a resource  - `DELETE` - Delete a resource  ## Compression  Responses are compressed if requested by the client. Currently [gzip](https://www.gzip.org/) and [deflate](https://tools.ietf.org/html/rfc1951) are supported. The client signals the desired compression by setting the [`Accept-Encoding` header](https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.3). If no `Accept-Encoding` header is send, `Accept-Encoding: identity` is assumed which will result in the API responding uncompressed.

The `auto_slopp.openproject.openapi_client` package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: 3
- Package version: 1.0.0
- Generator version: 7.21.0-SNAPSHOT
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

## Requirements.

Python 3.9+

## Installation & Usage

This python library package is generated without supporting files like setup.py or requirements files

To be able to use it, you will need these dependencies in your own package that uses this library:

* urllib3 >= 2.1.0, < 3.0.0
* python-dateutil >= 2.8.2
* pydantic >= 2.11
* typing-extensions >= 4.7.1

## Getting Started

In your own code, to use this library to connect and interact with auto-slopp.openproject.openapi-client,
you can run the following:

```python

import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)


# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ActionsCapabilitiesApi(api_client)
    filters = '[{ \"id\": { \"operator\": \"=\", \"values\": [\"memberships/create\"] }\" }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + id: Returns only the action having the id or all actions except those having the id(s). (optional)
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + *No sort supported yet* (optional) (default to '[["id", "asc"]]')

    try:
        # List actions
        api_response = api_instance.list_actions(filters=filters, sort_by=sort_by)
        print("The response of ActionsCapabilitiesApi->list_actions:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ActionsCapabilitiesApi->list_actions: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://openproject.melvin.beer*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*ActionsCapabilitiesApi* | [**list_actions**](auto_slopp/openproject/openapi_client/docs/ActionsCapabilitiesApi.md#list_actions) | **GET** /api/v3/actions | List actions
*ActionsCapabilitiesApi* | [**list_capabilities**](auto_slopp/openproject/openapi_client/docs/ActionsCapabilitiesApi.md#list_capabilities) | **GET** /api/v3/capabilities | List capabilities
*ActionsCapabilitiesApi* | [**view_action**](auto_slopp/openproject/openapi_client/docs/ActionsCapabilitiesApi.md#view_action) | **GET** /api/v3/actions/{id} | View action
*ActionsCapabilitiesApi* | [**view_capabilities**](auto_slopp/openproject/openapi_client/docs/ActionsCapabilitiesApi.md#view_capabilities) | **GET** /api/v3/capabilities/{id} | View capabilities
*ActionsCapabilitiesApi* | [**view_global_context**](auto_slopp/openproject/openapi_client/docs/ActionsCapabilitiesApi.md#view_global_context) | **GET** /api/v3/capabilities/context/global | View global context
*ActivitiesApi* | [**create_activity_attachment**](auto_slopp/openproject/openapi_client/docs/ActivitiesApi.md#create_activity_attachment) | **POST** /api/v3/activities/{id}/attachments | Add attachment to activity
*ActivitiesApi* | [**get_activity**](auto_slopp/openproject/openapi_client/docs/ActivitiesApi.md#get_activity) | **GET** /api/v3/activities/{id} | Get an activity
*ActivitiesApi* | [**list_activity_attachments**](auto_slopp/openproject/openapi_client/docs/ActivitiesApi.md#list_activity_attachments) | **GET** /api/v3/activities/{id}/attachments | List attachments by activity
*ActivitiesApi* | [**list_activity_emoji_reactions**](auto_slopp/openproject/openapi_client/docs/ActivitiesApi.md#list_activity_emoji_reactions) | **GET** /api/v3/activities/{id}/emoji_reactions | List emoji reactions by activity
*ActivitiesApi* | [**list_work_package_activities_emoji_reactions**](auto_slopp/openproject/openapi_client/docs/ActivitiesApi.md#list_work_package_activities_emoji_reactions) | **GET** /api/v3/work_packages/{id}/activities_emoji_reactions | List emoji reactions by work package activities
*ActivitiesApi* | [**toggle_activity_emoji_reaction**](auto_slopp/openproject/openapi_client/docs/ActivitiesApi.md#toggle_activity_emoji_reaction) | **PATCH** /api/v3/activities/{id}/emoji_reactions | Toggle emoji reaction for an activity
*ActivitiesApi* | [**update_activity**](auto_slopp/openproject/openapi_client/docs/ActivitiesApi.md#update_activity) | **PATCH** /api/v3/activities/{id} | Update activity
*AttachmentsApi* | [**add_attachment_to_meeting**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#add_attachment_to_meeting) | **POST** /api/v3/meetings/{id}/attachments | Add attachment to meeting
*AttachmentsApi* | [**add_attachment_to_post**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#add_attachment_to_post) | **POST** /api/v3/posts/{id}/attachments | Add attachment to post
*AttachmentsApi* | [**add_attachment_to_wiki_page**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#add_attachment_to_wiki_page) | **POST** /api/v3/wiki_pages/{id}/attachments | Add attachment to wiki page
*AttachmentsApi* | [**create_activity_attachment**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#create_activity_attachment) | **POST** /api/v3/activities/{id}/attachments | Add attachment to activity
*AttachmentsApi* | [**create_attachment**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#create_attachment) | **POST** /api/v3/attachments | Create Attachment
*AttachmentsApi* | [**create_work_package_attachment**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#create_work_package_attachment) | **POST** /api/v3/work_packages/{id}/attachments | Create work package attachment
*AttachmentsApi* | [**delete_attachment**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#delete_attachment) | **DELETE** /api/v3/attachments/{id} | Delete attachment
*AttachmentsApi* | [**list_activity_attachments**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#list_activity_attachments) | **GET** /api/v3/activities/{id}/attachments | List attachments by activity
*AttachmentsApi* | [**list_attachments_by_meeting**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#list_attachments_by_meeting) | **GET** /api/v3/meetings/{id}/attachments | List attachments by meeting
*AttachmentsApi* | [**list_attachments_by_post**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#list_attachments_by_post) | **GET** /api/v3/posts/{id}/attachments | List attachments by post
*AttachmentsApi* | [**list_attachments_by_wiki_page**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#list_attachments_by_wiki_page) | **GET** /api/v3/wiki_pages/{id}/attachments | List attachments by wiki page
*AttachmentsApi* | [**list_work_package_attachments**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#list_work_package_attachments) | **GET** /api/v3/work_packages/{id}/attachments | List attachments by work package
*AttachmentsApi* | [**view_attachment**](auto_slopp/openproject/openapi_client/docs/AttachmentsApi.md#view_attachment) | **GET** /api/v3/attachments/{id} | View attachment
*BudgetsApi* | [**view_budget**](auto_slopp/openproject/openapi_client/docs/BudgetsApi.md#view_budget) | **GET** /api/v3/budgets/{id} | view Budget
*BudgetsApi* | [**view_budgets_of_a_project**](auto_slopp/openproject/openapi_client/docs/BudgetsApi.md#view_budgets_of_a_project) | **GET** /api/v3/projects/{id}/budgets | view Budgets of a Project
*CategoriesApi* | [**list_categories_of_a_project**](auto_slopp/openproject/openapi_client/docs/CategoriesApi.md#list_categories_of_a_project) | **GET** /api/v3/projects/{id}/categories | List categories of a project
*CategoriesApi* | [**list_categories_of_a_workspace**](auto_slopp/openproject/openapi_client/docs/CategoriesApi.md#list_categories_of_a_workspace) | **GET** /api/v3/workspaces/{id}/categories | List categories of a workspace
*CategoriesApi* | [**view_category**](auto_slopp/openproject/openapi_client/docs/CategoriesApi.md#view_category) | **GET** /api/v3/categories/{id} | View Category
*CollectionsApi* | [**view_aggregated_result**](auto_slopp/openproject/openapi_client/docs/CollectionsApi.md#view_aggregated_result) | **GET** /api/v3/examples | view aggregated result
*ConfigurationApi* | [**view_configuration**](auto_slopp/openproject/openapi_client/docs/ConfigurationApi.md#view_configuration) | **GET** /api/v3/configuration | View configuration
*ConfigurationApi* | [**view_project_configuration**](auto_slopp/openproject/openapi_client/docs/ConfigurationApi.md#view_project_configuration) | **GET** /api/v3/projects/{id}/configuration | View project configuration
*CustomOptionsApi* | [**view_custom_option**](auto_slopp/openproject/openapi_client/docs/CustomOptionsApi.md#view_custom_option) | **GET** /api/v3/custom_options/{id} | View Custom Option
*CustomActionsApi* | [**execute_custom_action**](auto_slopp/openproject/openapi_client/docs/CustomActionsApi.md#execute_custom_action) | **POST** /api/v3/custom_actions/{id}/execute | Execute custom action
*CustomActionsApi* | [**get_custom_action**](auto_slopp/openproject/openapi_client/docs/CustomActionsApi.md#get_custom_action) | **GET** /api/v3/custom_actions/{id} | Get a custom action
*DocumentsApi* | [**list_documents**](auto_slopp/openproject/openapi_client/docs/DocumentsApi.md#list_documents) | **GET** /api/v3/documents | List Documents
*DocumentsApi* | [**update_document**](auto_slopp/openproject/openapi_client/docs/DocumentsApi.md#update_document) | **PATCH** /api/v3/documents/{id} | Update document
*DocumentsApi* | [**view_document**](auto_slopp/openproject/openapi_client/docs/DocumentsApi.md#view_document) | **GET** /api/v3/documents/{id} | View document
*EmojiReactionsApi* | [**list_activity_emoji_reactions**](auto_slopp/openproject/openapi_client/docs/EmojiReactionsApi.md#list_activity_emoji_reactions) | **GET** /api/v3/activities/{id}/emoji_reactions | List emoji reactions by activity
*EmojiReactionsApi* | [**list_work_package_activities_emoji_reactions**](auto_slopp/openproject/openapi_client/docs/EmojiReactionsApi.md#list_work_package_activities_emoji_reactions) | **GET** /api/v3/work_packages/{id}/activities_emoji_reactions | List emoji reactions by work package activities
*EmojiReactionsApi* | [**toggle_activity_emoji_reaction**](auto_slopp/openproject/openapi_client/docs/EmojiReactionsApi.md#toggle_activity_emoji_reaction) | **PATCH** /api/v3/activities/{id}/emoji_reactions | Toggle emoji reaction for an activity
*FavoritesApi* | [**favorite_project**](auto_slopp/openproject/openapi_client/docs/FavoritesApi.md#favorite_project) | **POST** /api/v3/projects/{id}/favorite | Favorite Project
*FavoritesApi* | [**favorite_workspace**](auto_slopp/openproject/openapi_client/docs/FavoritesApi.md#favorite_workspace) | **POST** /api/v3/workspaces/{id}/favorite | Favorite Workspace
*FavoritesApi* | [**unfavorite_project**](auto_slopp/openproject/openapi_client/docs/FavoritesApi.md#unfavorite_project) | **DELETE** /api/v3/projects/{id}/favorite | Unfavorite Project
*FavoritesApi* | [**unfavorite_workspace**](auto_slopp/openproject/openapi_client/docs/FavoritesApi.md#unfavorite_workspace) | **DELETE** /api/v3/workspaces/{id}/favorite | Unfavorite Workspace
*FileLinksApi* | [**get_project_storage**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#get_project_storage) | **GET** /api/v3/project_storages/{id} | Gets a project storage
*FileLinksApi* | [**list_project_storages**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#list_project_storages) | **GET** /api/v3/project_storages | Gets a list of project storages
*FileLinksApi* | [**open_project_storage**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#open_project_storage) | **GET** /api/v3/project_storages/{id}/open | Open the project storage
*FileLinksApi* | [**open_storage**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#open_storage) | **GET** /api/v3/storages/{id}/open | Open the storage
*FileLinksApi* | [**create_storage**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#create_storage) | **POST** /api/v3/storages | Creates a storage.
*FileLinksApi* | [**create_storage_folder**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#create_storage_folder) | **POST** /api/v3/storages/{id}/folders | Creation of a new folder
*FileLinksApi* | [**create_storage_oauth_credentials**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#create_storage_oauth_credentials) | **POST** /api/v3/storages/{id}/oauth_client_credentials | Creates an oauth client credentials object for a storage.
*FileLinksApi* | [**create_work_package_file_link**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#create_work_package_file_link) | **POST** /api/v3/work_packages/{id}/file_links | Creates file links.
*FileLinksApi* | [**delete_file_link**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#delete_file_link) | **DELETE** /api/v3/file_links/{id} | Removes a file link.
*FileLinksApi* | [**delete_storage**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#delete_storage) | **DELETE** /api/v3/storages/{id} | Delete a storage
*FileLinksApi* | [**download_file_link**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#download_file_link) | **GET** /api/v3/file_links/{id}/download | Creates a download uri of the linked file.
*FileLinksApi* | [**get_storage**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#get_storage) | **GET** /api/v3/storages/{id} | Get a storage
*FileLinksApi* | [**get_storage_files**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#get_storage_files) | **GET** /api/v3/storages/{id}/files | Gets files of a storage.
*FileLinksApi* | [**list_storages**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#list_storages) | **GET** /api/v3/storages | Get Storages
*FileLinksApi* | [**list_work_package_file_links**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#list_work_package_file_links) | **GET** /api/v3/work_packages/{id}/file_links | Gets all file links of a work package
*FileLinksApi* | [**open_file_link**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#open_file_link) | **GET** /api/v3/file_links/{id}/open | Creates an opening uri of the linked file.
*FileLinksApi* | [**prepare_storage_file_upload**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#prepare_storage_file_upload) | **POST** /api/v3/storages/{id}/files/prepare_upload | Preparation of a direct upload of a file to the given storage.
*FileLinksApi* | [**update_storage**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#update_storage) | **PATCH** /api/v3/storages/{id} | Update a storage
*FileLinksApi* | [**view_file_link**](auto_slopp/openproject/openapi_client/docs/FileLinksApi.md#view_file_link) | **GET** /api/v3/file_links/{id} | Gets a file link.
*FormsApi* | [**show_or_validate_form**](auto_slopp/openproject/openapi_client/docs/FormsApi.md#show_or_validate_form) | **POST** /api/v3/example/form | show or validate form
*GridsApi* | [**create_grid**](auto_slopp/openproject/openapi_client/docs/GridsApi.md#create_grid) | **POST** /api/v3/grids | Create a grid
*GridsApi* | [**get_grid**](auto_slopp/openproject/openapi_client/docs/GridsApi.md#get_grid) | **GET** /api/v3/grids/{id} | Get a grid
*GridsApi* | [**grid_create_form**](auto_slopp/openproject/openapi_client/docs/GridsApi.md#grid_create_form) | **POST** /api/v3/grids/form | Grid Create Form
*GridsApi* | [**grid_update_form**](auto_slopp/openproject/openapi_client/docs/GridsApi.md#grid_update_form) | **POST** /api/v3/grids/{id}/form | Grid Update Form
*GridsApi* | [**list_grids**](auto_slopp/openproject/openapi_client/docs/GridsApi.md#list_grids) | **GET** /api/v3/grids | List grids
*GridsApi* | [**update_grid**](auto_slopp/openproject/openapi_client/docs/GridsApi.md#update_grid) | **PATCH** /api/v3/grids/{id} | Update a grid
*GroupsApi* | [**create_group**](auto_slopp/openproject/openapi_client/docs/GroupsApi.md#create_group) | **POST** /api/v3/groups | Create group
*GroupsApi* | [**delete_group**](auto_slopp/openproject/openapi_client/docs/GroupsApi.md#delete_group) | **DELETE** /api/v3/groups/{id} | Delete group
*GroupsApi* | [**get_group**](auto_slopp/openproject/openapi_client/docs/GroupsApi.md#get_group) | **GET** /api/v3/groups/{id} | Get group
*GroupsApi* | [**list_groups**](auto_slopp/openproject/openapi_client/docs/GroupsApi.md#list_groups) | **GET** /api/v3/groups | List groups
*GroupsApi* | [**update_group**](auto_slopp/openproject/openapi_client/docs/GroupsApi.md#update_group) | **PATCH** /api/v3/groups/{id} | Update group
*HelpTextsApi* | [**get_help_text**](auto_slopp/openproject/openapi_client/docs/HelpTextsApi.md#get_help_text) | **GET** /api/v3/help_texts/{id} | Get help text
*HelpTextsApi* | [**list_help_texts**](auto_slopp/openproject/openapi_client/docs/HelpTextsApi.md#list_help_texts) | **GET** /api/v3/help_texts | List help texts
*MeetingsApi* | [**view_meeting**](auto_slopp/openproject/openapi_client/docs/MeetingsApi.md#view_meeting) | **GET** /api/v3/meetings/{id} | View Meeting Page
*MembershipsApi* | [**create_membership**](auto_slopp/openproject/openapi_client/docs/MembershipsApi.md#create_membership) | **POST** /api/v3/memberships | Create a membership
*MembershipsApi* | [**delete_membership**](auto_slopp/openproject/openapi_client/docs/MembershipsApi.md#delete_membership) | **DELETE** /api/v3/memberships/{id} | Delete membership
*MembershipsApi* | [**form_create_membership**](auto_slopp/openproject/openapi_client/docs/MembershipsApi.md#form_create_membership) | **POST** /api/v3/memberships/form | Form create membership
*MembershipsApi* | [**form_update_membership**](auto_slopp/openproject/openapi_client/docs/MembershipsApi.md#form_update_membership) | **POST** /api/v3/memberships/{id}/form | Form update membership
*MembershipsApi* | [**get_membership**](auto_slopp/openproject/openapi_client/docs/MembershipsApi.md#get_membership) | **GET** /api/v3/memberships/{id} | Get a membership
*MembershipsApi* | [**get_membership_schema**](auto_slopp/openproject/openapi_client/docs/MembershipsApi.md#get_membership_schema) | **GET** /api/v3/memberships/schema | Schema membership
*MembershipsApi* | [**get_memberships_available_projects**](auto_slopp/openproject/openapi_client/docs/MembershipsApi.md#get_memberships_available_projects) | **GET** /api/v3/memberships/available_projects | Available projects for memberships
*MembershipsApi* | [**list_memberships**](auto_slopp/openproject/openapi_client/docs/MembershipsApi.md#list_memberships) | **GET** /api/v3/memberships | List memberships
*MembershipsApi* | [**update_membership**](auto_slopp/openproject/openapi_client/docs/MembershipsApi.md#update_membership) | **PATCH** /api/v3/memberships/{id} | Update membership
*NewsApi* | [**create_news**](auto_slopp/openproject/openapi_client/docs/NewsApi.md#create_news) | **POST** /api/v3/news | Create News
*NewsApi* | [**delete_news**](auto_slopp/openproject/openapi_client/docs/NewsApi.md#delete_news) | **DELETE** /api/v3/news/{id} | Delete news
*NewsApi* | [**list_news**](auto_slopp/openproject/openapi_client/docs/NewsApi.md#list_news) | **GET** /api/v3/news | List News
*NewsApi* | [**update_news**](auto_slopp/openproject/openapi_client/docs/NewsApi.md#update_news) | **PATCH** /api/v3/news/{id} | Update news
*NewsApi* | [**view_news**](auto_slopp/openproject/openapi_client/docs/NewsApi.md#view_news) | **GET** /api/v3/news/{id} | View news
*NotificationsApi* | [**list_notifications**](auto_slopp/openproject/openapi_client/docs/NotificationsApi.md#list_notifications) | **GET** /api/v3/notifications | Get notification collection
*NotificationsApi* | [**read_notification**](auto_slopp/openproject/openapi_client/docs/NotificationsApi.md#read_notification) | **POST** /api/v3/notifications/{id}/read_ian | Read notification
*NotificationsApi* | [**read_notifications**](auto_slopp/openproject/openapi_client/docs/NotificationsApi.md#read_notifications) | **POST** /api/v3/notifications/read_ian | Read all notifications
*NotificationsApi* | [**unread_notification**](auto_slopp/openproject/openapi_client/docs/NotificationsApi.md#unread_notification) | **POST** /api/v3/notifications/{id}/unread_ian | Unread notification
*NotificationsApi* | [**unread_notifications**](auto_slopp/openproject/openapi_client/docs/NotificationsApi.md#unread_notifications) | **POST** /api/v3/notifications/unread_ian | Unread all notifications
*NotificationsApi* | [**view_notification**](auto_slopp/openproject/openapi_client/docs/NotificationsApi.md#view_notification) | **GET** /api/v3/notifications/{id} | Get the notification
*NotificationsApi* | [**view_notification_detail**](auto_slopp/openproject/openapi_client/docs/NotificationsApi.md#view_notification_detail) | **GET** /api/v3/notifications/{notification_id}/details/{id} | Get a notification detail
*OAuth2Api* | [**get_oauth_application**](auto_slopp/openproject/openapi_client/docs/OAuth2Api.md#get_oauth_application) | **GET** /api/v3/oauth_applications/{id} | Get the oauth application.
*OAuth2Api* | [**get_oauth_client_credentials**](auto_slopp/openproject/openapi_client/docs/OAuth2Api.md#get_oauth_client_credentials) | **GET** /api/v3/oauth_client_credentials/{id} | Get the oauth client credentials object.
*PortfoliosApi* | [**delete_portfolio**](auto_slopp/openproject/openapi_client/docs/PortfoliosApi.md#delete_portfolio) | **DELETE** /api/v3/portfolios/{id} | Delete Portfolio
*PortfoliosApi* | [**list_portfolios**](auto_slopp/openproject/openapi_client/docs/PortfoliosApi.md#list_portfolios) | **GET** /api/v3/portfolios | List portfolios
*PortfoliosApi* | [**portfolio_update_form**](auto_slopp/openproject/openapi_client/docs/PortfoliosApi.md#portfolio_update_form) | **POST** /api/v3/portfolios/{id}/form | Portfolio update form
*PortfoliosApi* | [**update_portfolio**](auto_slopp/openproject/openapi_client/docs/PortfoliosApi.md#update_portfolio) | **PATCH** /api/v3/portfolios/{id} | Update Portfolio
*PortfoliosApi* | [**view_portfolio**](auto_slopp/openproject/openapi_client/docs/PortfoliosApi.md#view_portfolio) | **GET** /api/v3/portfolios/{id} | View portfolio
*PostsApi* | [**view_post**](auto_slopp/openproject/openapi_client/docs/PostsApi.md#view_post) | **GET** /api/v3/posts/{id} | View Post
*PreviewingApi* | [**preview_markdown_document**](auto_slopp/openproject/openapi_client/docs/PreviewingApi.md#preview_markdown_document) | **POST** /api/v3/render/markdown | Preview Markdown document
*PreviewingApi* | [**preview_plain_document**](auto_slopp/openproject/openapi_client/docs/PreviewingApi.md#preview_plain_document) | **POST** /api/v3/render/plain | Preview plain document
*PrincipalsApi* | [**create_placeholder_user**](auto_slopp/openproject/openapi_client/docs/PrincipalsApi.md#create_placeholder_user) | **POST** /api/v3/placeholder_users | Create placeholder user
*PrincipalsApi* | [**create_user**](auto_slopp/openproject/openapi_client/docs/PrincipalsApi.md#create_user) | **POST** /api/v3/users | Create User
*PrincipalsApi* | [**delete_placeholder_user**](auto_slopp/openproject/openapi_client/docs/PrincipalsApi.md#delete_placeholder_user) | **DELETE** /api/v3/placeholder_users/{id} | Delete placeholder user
*PrincipalsApi* | [**delete_user**](auto_slopp/openproject/openapi_client/docs/PrincipalsApi.md#delete_user) | **DELETE** /api/v3/users/{id} | Delete user
*PrincipalsApi* | [**list_placeholder_users**](auto_slopp/openproject/openapi_client/docs/PrincipalsApi.md#list_placeholder_users) | **GET** /api/v3/placeholder_users | List placehoder users
*PrincipalsApi* | [**list_principals**](auto_slopp/openproject/openapi_client/docs/PrincipalsApi.md#list_principals) | **GET** /api/v3/principals | List principals
*PrincipalsApi* | [**list_users**](auto_slopp/openproject/openapi_client/docs/PrincipalsApi.md#list_users) | **GET** /api/v3/users | List Users
*PrincipalsApi* | [**update_placeholder_user**](auto_slopp/openproject/openapi_client/docs/PrincipalsApi.md#update_placeholder_user) | **PATCH** /api/v3/placeholder_users/{id} | Update placeholder user
*PrincipalsApi* | [**update_user**](auto_slopp/openproject/openapi_client/docs/PrincipalsApi.md#update_user) | **PATCH** /api/v3/users/{id} | Update user
*PrincipalsApi* | [**view_placeholder_user**](auto_slopp/openproject/openapi_client/docs/PrincipalsApi.md#view_placeholder_user) | **GET** /api/v3/placeholder_users/{id} | View placeholder user
*PrincipalsApi* | [**view_user**](auto_slopp/openproject/openapi_client/docs/PrincipalsApi.md#view_user) | **GET** /api/v3/users/{id} | View user
*PrioritiesApi* | [**list_all_priorities**](auto_slopp/openproject/openapi_client/docs/PrioritiesApi.md#list_all_priorities) | **GET** /api/v3/priorities | List all Priorities
*PrioritiesApi* | [**view_priority**](auto_slopp/openproject/openapi_client/docs/PrioritiesApi.md#view_priority) | **GET** /api/v3/priorities/{id} | View Priority
*ProgramsApi* | [**delete_program**](auto_slopp/openproject/openapi_client/docs/ProgramsApi.md#delete_program) | **DELETE** /api/v3/programs/{id} | Delete Program
*ProgramsApi* | [**list_programs**](auto_slopp/openproject/openapi_client/docs/ProgramsApi.md#list_programs) | **GET** /api/v3/programs | List programs
*ProgramsApi* | [**program_update_form**](auto_slopp/openproject/openapi_client/docs/ProgramsApi.md#program_update_form) | **POST** /api/v3/programs/{id}/form | Program update form
*ProgramsApi* | [**update_program**](auto_slopp/openproject/openapi_client/docs/ProgramsApi.md#update_program) | **PATCH** /api/v3/programs/{id} | Update Program
*ProgramsApi* | [**view_program**](auto_slopp/openproject/openapi_client/docs/ProgramsApi.md#view_program) | **GET** /api/v3/programs/{id} | View program
*ProjectPhaseDefinitionsApi* | [**get_project_phase_definition**](auto_slopp/openproject/openapi_client/docs/ProjectPhaseDefinitionsApi.md#get_project_phase_definition) | **GET** /api/v3/project_phase_definitions/{id} | Get a project phase definition
*ProjectPhaseDefinitionsApi* | [**list_project_phase_definitions**](auto_slopp/openproject/openapi_client/docs/ProjectPhaseDefinitionsApi.md#list_project_phase_definitions) | **GET** /api/v3/project_phase_definitions | List project phase definitions
*ProjectPhasesApi* | [**get_project_phase**](auto_slopp/openproject/openapi_client/docs/ProjectPhasesApi.md#get_project_phase) | **GET** /api/v3/project_phases/{id} | Get a project phase
*ProjectsApi* | [**create_project**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#create_project) | **POST** /api/v3/projects | Create project
*ProjectsApi* | [**create_project_copy**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#create_project_copy) | **POST** /api/v3/projects/{id}/copy | Create project copy
*ProjectsApi* | [**delete_project**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#delete_project) | **DELETE** /api/v3/projects/{id} | Delete Project
*ProjectsApi* | [**favorite_project**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#favorite_project) | **POST** /api/v3/projects/{id}/favorite | Favorite Project
*ProjectsApi* | [**list_available_parent_project_candidates**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#list_available_parent_project_candidates) | **GET** /api/v3/projects/available_parent_projects | List available parent project candidates
*ProjectsApi* | [**list_projects**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#list_projects) | **GET** /api/v3/projects | List projects
*ProjectsApi* | [**list_projects_with_version**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#list_projects_with_version) | **GET** /api/v3/versions/{id}/projects | List projects having version
*ProjectsApi* | [**list_workspaces_with_version**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#list_workspaces_with_version) | **GET** /api/v3/versions/{id}/workspaces | List workspaces having version
*ProjectsApi* | [**project_copy_form**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#project_copy_form) | **POST** /api/v3/projects/{id}/copy/form | Project copy form
*ProjectsApi* | [**project_create_form**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#project_create_form) | **POST** /api/v3/projects/form | Project create form
*ProjectsApi* | [**project_update_form**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#project_update_form) | **POST** /api/v3/projects/{id}/form | Project update form
*ProjectsApi* | [**unfavorite_project**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#unfavorite_project) | **DELETE** /api/v3/projects/{id}/favorite | Unfavorite Project
*ProjectsApi* | [**update_project**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#update_project) | **PATCH** /api/v3/projects/{id} | Update Project
*ProjectsApi* | [**view_project**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#view_project) | **GET** /api/v3/projects/{id} | View project
*ProjectsApi* | [**view_project_configuration**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#view_project_configuration) | **GET** /api/v3/projects/{id}/configuration | View project configuration
*ProjectsApi* | [**view_project_schema**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#view_project_schema) | **GET** /api/v3/projects/schema | View project schema
*ProjectsApi* | [**view_project_status**](auto_slopp/openproject/openapi_client/docs/ProjectsApi.md#view_project_status) | **GET** /api/v3/project_statuses/{id} | View project status
*QueriesApi* | [**available_projects_for_query**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#available_projects_for_query) | **GET** /api/v3/queries/available_projects | Available projects for query
*QueriesApi* | [**create_query**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#create_query) | **POST** /api/v3/queries | Create query
*QueriesApi* | [**delete_query**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#delete_query) | **DELETE** /api/v3/queries/{id} | Delete query
*QueriesApi* | [**edit_query**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#edit_query) | **PATCH** /api/v3/queries/{id} | Edit Query
*QueriesApi* | [**list_queries**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#list_queries) | **GET** /api/v3/queries | List queries
*QueriesApi* | [**query_create_form**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#query_create_form) | **POST** /api/v3/queries/form | Query Create Form
*QueriesApi* | [**query_update_form**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#query_update_form) | **POST** /api/v3/queries/{id}/form | Query Update Form
*QueriesApi* | [**star_query**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#star_query) | **PATCH** /api/v3/queries/{id}/star | Star query
*QueriesApi* | [**unstar_query**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#unstar_query) | **PATCH** /api/v3/queries/{id}/unstar | Unstar query
*QueriesApi* | [**view_default_query**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#view_default_query) | **GET** /api/v3/queries/default | View default query
*QueriesApi* | [**view_default_query_for_project**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#view_default_query_for_project) | **GET** /api/v3/projects/{id}/queries/default | View default query for project
*QueriesApi* | [**view_default_query_for_workspace**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#view_default_query_for_workspace) | **GET** /api/v3/workspaces/{id}/queries/default | View default query for workspace
*QueriesApi* | [**view_query**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#view_query) | **GET** /api/v3/queries/{id} | View query
*QueriesApi* | [**view_schema_for_global_queries**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#view_schema_for_global_queries) | **GET** /api/v3/queries/schema | View schema for global queries
*QueriesApi* | [**view_schema_for_project_queries**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#view_schema_for_project_queries) | **GET** /api/v3/projects/{id}/queries/schema | View schema for project queries
*QueriesApi* | [**view_schema_for_workspace_queries**](auto_slopp/openproject/openapi_client/docs/QueriesApi.md#view_schema_for_workspace_queries) | **GET** /api/v3/workspace/{id}/queries/schema | View schema for workspace queries
*QueryColumnsApi* | [**view_query_column**](auto_slopp/openproject/openapi_client/docs/QueryColumnsApi.md#view_query_column) | **GET** /api/v3/queries/columns/{id} | View Query Column
*QueryFilterInstanceSchemaApi* | [**list_query_filter_instance_schemas**](auto_slopp/openproject/openapi_client/docs/QueryFilterInstanceSchemaApi.md#list_query_filter_instance_schemas) | **GET** /api/v3/queries/filter_instance_schemas | List Query Filter Instance Schemas
*QueryFilterInstanceSchemaApi* | [**list_query_filter_instance_schemas_for_project**](auto_slopp/openproject/openapi_client/docs/QueryFilterInstanceSchemaApi.md#list_query_filter_instance_schemas_for_project) | **GET** /api/v3/projects/{id}/queries/filter_instance_schemas | List Query Filter Instance Schemas for Project
*QueryFilterInstanceSchemaApi* | [**list_query_filter_instance_schemas_for_workspace**](auto_slopp/openproject/openapi_client/docs/QueryFilterInstanceSchemaApi.md#list_query_filter_instance_schemas_for_workspace) | **GET** /api/v3/workspace/{id}/queries/filter_instance_schemas | List Query Filter Instance Schemas for Workspace
*QueryFilterInstanceSchemaApi* | [**view_query_filter_instance_schema**](auto_slopp/openproject/openapi_client/docs/QueryFilterInstanceSchemaApi.md#view_query_filter_instance_schema) | **GET** /api/v3/queries/filter_instance_schemas/{id} | View Query Filter Instance Schema
*QueryFiltersApi* | [**view_query_filter**](auto_slopp/openproject/openapi_client/docs/QueryFiltersApi.md#view_query_filter) | **GET** /api/v3/queries/filters/{id} | View Query Filter
*QueryOperatorsApi* | [**view_query_operator**](auto_slopp/openproject/openapi_client/docs/QueryOperatorsApi.md#view_query_operator) | **GET** /api/v3/queries/operators/{id} | View Query Operator
*QuerySortBysApi* | [**view_query_sort_by**](auto_slopp/openproject/openapi_client/docs/QuerySortBysApi.md#view_query_sort_by) | **GET** /api/v3/queries/sort_bys/{id} | View Query Sort By
*RelationsApi* | [**create_relation**](auto_slopp/openproject/openapi_client/docs/RelationsApi.md#create_relation) | **POST** /api/v3/work_packages/{id}/relations | Create relation
*RelationsApi* | [**delete_relation**](auto_slopp/openproject/openapi_client/docs/RelationsApi.md#delete_relation) | **DELETE** /api/v3/relations/{id} | Delete Relation
*RelationsApi* | [**get_relation**](auto_slopp/openproject/openapi_client/docs/RelationsApi.md#get_relation) | **GET** /api/v3/relations/{id} | Get Relation
*RelationsApi* | [**list_relations**](auto_slopp/openproject/openapi_client/docs/RelationsApi.md#list_relations) | **GET** /api/v3/relations | List Relations
*RelationsApi* | [**update_relation**](auto_slopp/openproject/openapi_client/docs/RelationsApi.md#update_relation) | **PATCH** /api/v3/relations/{id} | Update Relation
*RemindersApi* | [**create_work_package_reminder**](auto_slopp/openproject/openapi_client/docs/RemindersApi.md#create_work_package_reminder) | **POST** /api/v3/work_packages/{work_package_id}/reminders | Create a work package reminder
*RemindersApi* | [**delete_reminder**](auto_slopp/openproject/openapi_client/docs/RemindersApi.md#delete_reminder) | **DELETE** /api/v3/reminders/{id} | Delete a reminder
*RemindersApi* | [**list_reminders**](auto_slopp/openproject/openapi_client/docs/RemindersApi.md#list_reminders) | **GET** /api/v3/reminders | List all active reminders
*RemindersApi* | [**list_work_package_reminders**](auto_slopp/openproject/openapi_client/docs/RemindersApi.md#list_work_package_reminders) | **GET** /api/v3/work_packages/{work_package_id}/reminders | List work package reminders
*RemindersApi* | [**update_reminder**](auto_slopp/openproject/openapi_client/docs/RemindersApi.md#update_reminder) | **PATCH** /api/v3/reminders/{id} | Update a reminder
*RevisionsApi* | [**view_revision**](auto_slopp/openproject/openapi_client/docs/RevisionsApi.md#view_revision) | **GET** /api/v3/revisions/{id} | View revision
*RolesApi* | [**list_roles**](auto_slopp/openproject/openapi_client/docs/RolesApi.md#list_roles) | **GET** /api/v3/roles | List roles
*RolesApi* | [**view_role**](auto_slopp/openproject/openapi_client/docs/RolesApi.md#view_role) | **GET** /api/v3/roles/{id} | View role
*RootApi* | [**view_root**](auto_slopp/openproject/openapi_client/docs/RootApi.md#view_root) | **GET** /api/v3 | View root
*SchemasApi* | [**view_the_schema**](auto_slopp/openproject/openapi_client/docs/SchemasApi.md#view_the_schema) | **GET** /api/v3/example/schema | view the schema
*StatusesApi* | [**get_status**](auto_slopp/openproject/openapi_client/docs/StatusesApi.md#get_status) | **GET** /api/v3/statuses/{id} | Get a work package status
*StatusesApi* | [**list_statuses**](auto_slopp/openproject/openapi_client/docs/StatusesApi.md#list_statuses) | **GET** /api/v3/statuses | List the collection of all statuses
*TimeEntriesApi* | [**available_projects_for_time_entries**](auto_slopp/openproject/openapi_client/docs/TimeEntriesApi.md#available_projects_for_time_entries) | **GET** /api/v3/time_entries/available_projects | Available projects for time entries
*TimeEntriesApi* | [**time_entry_create_form**](auto_slopp/openproject/openapi_client/docs/TimeEntriesApi.md#time_entry_create_form) | **POST** /api/v3/time_entries/form | Time entry create form
*TimeEntriesApi* | [**time_entry_update_form**](auto_slopp/openproject/openapi_client/docs/TimeEntriesApi.md#time_entry_update_form) | **POST** /api/v3/time_entries/{id}/form | Time entry update form
*TimeEntriesApi* | [**update_time_entry**](auto_slopp/openproject/openapi_client/docs/TimeEntriesApi.md#update_time_entry) | **PATCH** /api/v3/time_entries/{id} | update time entry
*TimeEntriesApi* | [**view_time_entry_schema**](auto_slopp/openproject/openapi_client/docs/TimeEntriesApi.md#view_time_entry_schema) | **GET** /api/v3/time_entries/schema | View time entry schema
*TimeEntriesApi* | [**create_time_entry**](auto_slopp/openproject/openapi_client/docs/TimeEntriesApi.md#create_time_entry) | **POST** /api/v3/time_entries | Create time entry
*TimeEntriesApi* | [**delete_time_entry**](auto_slopp/openproject/openapi_client/docs/TimeEntriesApi.md#delete_time_entry) | **DELETE** /api/v3/time_entries/{id} | Delete time entry
*TimeEntriesApi* | [**get_time_entry**](auto_slopp/openproject/openapi_client/docs/TimeEntriesApi.md#get_time_entry) | **GET** /api/v3/time_entries/{id} | Get time entry
*TimeEntriesApi* | [**list_time_entries**](auto_slopp/openproject/openapi_client/docs/TimeEntriesApi.md#list_time_entries) | **GET** /api/v3/time_entries | List time entries
*TimeEntryActivitiesApi* | [**get_time_entries_activity**](auto_slopp/openproject/openapi_client/docs/TimeEntryActivitiesApi.md#get_time_entries_activity) | **GET** /api/v3/time_entries/activity/{id} | View time entries activity
*TypesApi* | [**list_all_types**](auto_slopp/openproject/openapi_client/docs/TypesApi.md#list_all_types) | **GET** /api/v3/types | List all Types
*TypesApi* | [**list_types_available_in_a_project**](auto_slopp/openproject/openapi_client/docs/TypesApi.md#list_types_available_in_a_project) | **GET** /api/v3/projects/{id}/types | List types available in a project
*TypesApi* | [**list_types_available_in_a_workspace**](auto_slopp/openproject/openapi_client/docs/TypesApi.md#list_types_available_in_a_workspace) | **GET** /api/v3/workspaces/{id}/types | List types available in a workspace
*TypesApi* | [**view_type**](auto_slopp/openproject/openapi_client/docs/TypesApi.md#view_type) | **GET** /api/v3/types/{id} | View Type
*UserPreferencesApi* | [**show_my_preferences**](auto_slopp/openproject/openapi_client/docs/UserPreferencesApi.md#show_my_preferences) | **GET** /api/v3/my_preferences | Show my preferences
*UserPreferencesApi* | [**update_user_preferences**](auto_slopp/openproject/openapi_client/docs/UserPreferencesApi.md#update_user_preferences) | **PATCH** /api/v3/my_preferences | Update my preferences
*UsersApi* | [**create_user**](auto_slopp/openproject/openapi_client/docs/UsersApi.md#create_user) | **POST** /api/v3/users | Create User
*UsersApi* | [**delete_user**](auto_slopp/openproject/openapi_client/docs/UsersApi.md#delete_user) | **DELETE** /api/v3/users/{id} | Delete user
*UsersApi* | [**list_users**](auto_slopp/openproject/openapi_client/docs/UsersApi.md#list_users) | **GET** /api/v3/users | List Users
*UsersApi* | [**lock_user**](auto_slopp/openproject/openapi_client/docs/UsersApi.md#lock_user) | **POST** /api/v3/users/{id}/lock | Lock user
*UsersApi* | [**unlock_user**](auto_slopp/openproject/openapi_client/docs/UsersApi.md#unlock_user) | **DELETE** /api/v3/users/{id}/lock | Unlock user
*UsersApi* | [**update_user**](auto_slopp/openproject/openapi_client/docs/UsersApi.md#update_user) | **PATCH** /api/v3/users/{id} | Update user
*UsersApi* | [**user_update_form**](auto_slopp/openproject/openapi_client/docs/UsersApi.md#user_update_form) | **POST** /api/v3/users/{id}/form | User update form
*UsersApi* | [**view_user**](auto_slopp/openproject/openapi_client/docs/UsersApi.md#view_user) | **GET** /api/v3/users/{id} | View user
*UsersApi* | [**view_user_schema**](auto_slopp/openproject/openapi_client/docs/UsersApi.md#view_user_schema) | **GET** /api/v3/users/schema | View user schema
*ValuesPropertyApi* | [**view_notification_detail**](auto_slopp/openproject/openapi_client/docs/ValuesPropertyApi.md#view_notification_detail) | **GET** /api/v3/notifications/{notification_id}/details/{id} | Get a notification detail
*ValuesPropertyApi* | [**view_values_schema**](auto_slopp/openproject/openapi_client/docs/ValuesPropertyApi.md#view_values_schema) | **GET** /api/v3/values/schema/{id} | View Values schema
*VersionsApi* | [**available_projects_for_versions**](auto_slopp/openproject/openapi_client/docs/VersionsApi.md#available_projects_for_versions) | **GET** /api/v3/versions/available_projects | Available projects for versions
*VersionsApi* | [**create_version**](auto_slopp/openproject/openapi_client/docs/VersionsApi.md#create_version) | **POST** /api/v3/versions | Create version
*VersionsApi* | [**delete_version**](auto_slopp/openproject/openapi_client/docs/VersionsApi.md#delete_version) | **DELETE** /api/v3/versions/{id} | Delete version
*VersionsApi* | [**get_version**](auto_slopp/openproject/openapi_client/docs/VersionsApi.md#get_version) | **GET** /api/v3/versions/{id} | Get version
*VersionsApi* | [**list_versions**](auto_slopp/openproject/openapi_client/docs/VersionsApi.md#list_versions) | **GET** /api/v3/versions | List versions
*VersionsApi* | [**list_versions_available_in_a_project**](auto_slopp/openproject/openapi_client/docs/VersionsApi.md#list_versions_available_in_a_project) | **GET** /api/v3/projects/{id}/versions | List versions available in a project
*VersionsApi* | [**list_versions_available_in_a_workspace**](auto_slopp/openproject/openapi_client/docs/VersionsApi.md#list_versions_available_in_a_workspace) | **GET** /api/v3/workspaces/{id}/versions | List versions available in a workspace
*VersionsApi* | [**update_version**](auto_slopp/openproject/openapi_client/docs/VersionsApi.md#update_version) | **PATCH** /api/v3/versions/{id} | Update Version
*VersionsApi* | [**version_create_form**](auto_slopp/openproject/openapi_client/docs/VersionsApi.md#version_create_form) | **POST** /api/v3/versions/form | Version create form
*VersionsApi* | [**version_update_form**](auto_slopp/openproject/openapi_client/docs/VersionsApi.md#version_update_form) | **POST** /api/v3/versions/{id}/form | Version update form
*VersionsApi* | [**view_version_schema**](auto_slopp/openproject/openapi_client/docs/VersionsApi.md#view_version_schema) | **GET** /api/v3/versions/schema | View version schema
*ViewsApi* | [**create_views**](auto_slopp/openproject/openapi_client/docs/ViewsApi.md#create_views) | **POST** /api/v3/views/{id} | Create view
*ViewsApi* | [**list_views**](auto_slopp/openproject/openapi_client/docs/ViewsApi.md#list_views) | **GET** /api/v3/views | List views
*ViewsApi* | [**view_view**](auto_slopp/openproject/openapi_client/docs/ViewsApi.md#view_view) | **GET** /api/v3/views/{id} | View view
*WikiPagesApi* | [**view_wiki_page**](auto_slopp/openproject/openapi_client/docs/WikiPagesApi.md#view_wiki_page) | **GET** /api/v3/wiki_pages/{id} | View Wiki Page
*WorkPackagesApi* | [**list_work_package_activities_emoji_reactions**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#list_work_package_activities_emoji_reactions) | **GET** /api/v3/work_packages/{id}/activities_emoji_reactions | List emoji reactions by work package activities
*WorkPackagesApi* | [**add_watcher**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#add_watcher) | **POST** /api/v3/work_packages/{id}/watchers | Add watcher
*WorkPackagesApi* | [**available_projects_for_work_package**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#available_projects_for_work_package) | **GET** /api/v3/work_packages/{id}/available_projects | Available projects for work package
*WorkPackagesApi* | [**available_watchers**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#available_watchers) | **GET** /api/v3/work_packages/{id}/available_watchers | Available watchers
*WorkPackagesApi* | [**comment_work_package**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#comment_work_package) | **POST** /api/v3/work_packages/{id}/activities | Comment work package
*WorkPackagesApi* | [**create_project_work_package**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#create_project_work_package) | **POST** /api/v3/projects/{id}/work_packages | Create work package in project
*WorkPackagesApi* | [**create_work_package**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#create_work_package) | **POST** /api/v3/work_packages | Create Work Package
*WorkPackagesApi* | [**create_work_package_file_link**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#create_work_package_file_link) | **POST** /api/v3/work_packages/{id}/file_links | Creates file links.
*WorkPackagesApi* | [**create_work_package_reminder**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#create_work_package_reminder) | **POST** /api/v3/work_packages/{work_package_id}/reminders | Create a work package reminder
*WorkPackagesApi* | [**create_workspace_work_package**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#create_workspace_work_package) | **POST** /api/v3/workspaces/{id}/work_packages | Create work package in workspace
*WorkPackagesApi* | [**delete_work_package**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#delete_work_package) | **DELETE** /api/v3/work_packages/{id} | Delete Work Package
*WorkPackagesApi* | [**form_create_work_package**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#form_create_work_package) | **POST** /api/v3/work_packages/form | Form for creating a Work Package
*WorkPackagesApi* | [**form_create_work_package_in_project**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#form_create_work_package_in_project) | **POST** /api/v3/projects/{id}/work_packages/form | Form for creating Work Packages in a Project
*WorkPackagesApi* | [**form_create_work_package_in_workspace**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#form_create_work_package_in_workspace) | **POST** /api/v3/workspaces/{id}/work_packages/form | Form for creating Work Packages in a Workspace
*WorkPackagesApi* | [**form_edit_work_package**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#form_edit_work_package) | **POST** /api/v3/work_packages/{id}/form | Form for editing a Work Package
*WorkPackagesApi* | [**get_project_work_package_collection**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#get_project_work_package_collection) | **GET** /api/v3/projects/{id}/work_packages | Get work packages of project
*WorkPackagesApi* | [**get_workspace_work_package_collection**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#get_workspace_work_package_collection) | **GET** /api/v3/workspaces/{id}/work_packages | Get work packages of workspace
*WorkPackagesApi* | [**list_available_relation_candidates**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#list_available_relation_candidates) | **GET** /api/v3/work_packages/{id}/available_relation_candidates | Available relation candidates
*WorkPackagesApi* | [**list_watchers**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#list_watchers) | **GET** /api/v3/work_packages/{id}/watchers | List watchers
*WorkPackagesApi* | [**list_work_package_activities**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#list_work_package_activities) | **GET** /api/v3/work_packages/{id}/activities | List work package activities
*WorkPackagesApi* | [**list_work_package_file_links**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#list_work_package_file_links) | **GET** /api/v3/work_packages/{id}/file_links | Gets all file links of a work package
*WorkPackagesApi* | [**list_work_package_reminders**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#list_work_package_reminders) | **GET** /api/v3/work_packages/{work_package_id}/reminders | List work package reminders
*WorkPackagesApi* | [**list_work_package_schemas**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#list_work_package_schemas) | **GET** /api/v3/work_packages/schemas | List Work Package Schemas
*WorkPackagesApi* | [**list_work_packages**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#list_work_packages) | **GET** /api/v3/work_packages | List work packages
*WorkPackagesApi* | [**project_available_assignees**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#project_available_assignees) | **GET** /api/v3/projects/{id}/available_assignees | Project Available assignees
*WorkPackagesApi* | [**remove_watcher**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#remove_watcher) | **DELETE** /api/v3/work_packages/{id}/watchers/{user_id} | Remove watcher
*WorkPackagesApi* | [**revisions**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#revisions) | **GET** /api/v3/work_packages/{id}/revisions | Revisions
*WorkPackagesApi* | [**update_work_package**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#update_work_package) | **PATCH** /api/v3/work_packages/{id} | Update a Work Package
*WorkPackagesApi* | [**view_work_package**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#view_work_package) | **GET** /api/v3/work_packages/{id} | View Work Package
*WorkPackagesApi* | [**view_work_package_schema**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#view_work_package_schema) | **GET** /api/v3/work_packages/schemas/{identifier} | View Work Package Schema
*WorkPackagesApi* | [**work_package_available_assignees**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#work_package_available_assignees) | **GET** /api/v3/work_packages/{id}/available_assignees | Work Package Available assignees
*WorkPackagesApi* | [**workspace_available_assignees**](auto_slopp/openproject/openapi_client/docs/WorkPackagesApi.md#workspace_available_assignees) | **GET** /api/v3/workspaces/{id}/available_assignees | Workspace Available assignees
*WorkScheduleApi* | [**create_non_working_day**](auto_slopp/openproject/openapi_client/docs/WorkScheduleApi.md#create_non_working_day) | **POST** /api/v3/days/non_working | Creates a non-working day (NOT IMPLEMENTED)
*WorkScheduleApi* | [**delete_non_working_day**](auto_slopp/openproject/openapi_client/docs/WorkScheduleApi.md#delete_non_working_day) | **DELETE** /api/v3/days/non_working/{date} | Removes a non-working day (NOT IMPLEMENTED)
*WorkScheduleApi* | [**list_days**](auto_slopp/openproject/openapi_client/docs/WorkScheduleApi.md#list_days) | **GET** /api/v3/days | Lists days
*WorkScheduleApi* | [**list_non_working_days**](auto_slopp/openproject/openapi_client/docs/WorkScheduleApi.md#list_non_working_days) | **GET** /api/v3/days/non_working | Lists all non working days
*WorkScheduleApi* | [**list_week_days**](auto_slopp/openproject/openapi_client/docs/WorkScheduleApi.md#list_week_days) | **GET** /api/v3/days/week | Lists week days
*WorkScheduleApi* | [**update_non_working_day**](auto_slopp/openproject/openapi_client/docs/WorkScheduleApi.md#update_non_working_day) | **PATCH** /api/v3/days/non_working/{date} | Update a non-working day attributes (NOT IMPLEMENTED)
*WorkScheduleApi* | [**update_week_day**](auto_slopp/openproject/openapi_client/docs/WorkScheduleApi.md#update_week_day) | **PATCH** /api/v3/days/week/{day} | Update a week day attributes (NOT IMPLEMENTED)
*WorkScheduleApi* | [**update_week_days**](auto_slopp/openproject/openapi_client/docs/WorkScheduleApi.md#update_week_days) | **PATCH** /api/v3/days/week | Update week days (NOT IMPLEMENTED)
*WorkScheduleApi* | [**view_day**](auto_slopp/openproject/openapi_client/docs/WorkScheduleApi.md#view_day) | **GET** /api/v3/days/{date} | View day
*WorkScheduleApi* | [**view_non_working_day**](auto_slopp/openproject/openapi_client/docs/WorkScheduleApi.md#view_non_working_day) | **GET** /api/v3/days/non_working/{date} | View a non-working day
*WorkScheduleApi* | [**view_week_day**](auto_slopp/openproject/openapi_client/docs/WorkScheduleApi.md#view_week_day) | **GET** /api/v3/days/week/{day} | View a week day
*WorkspaceApi* | [**list_workspace**](auto_slopp/openproject/openapi_client/docs/WorkspaceApi.md#list_workspace) | **GET** /api/v3/workspaces | List workspace
*WorkspacesApi* | [**favorite_workspace**](auto_slopp/openproject/openapi_client/docs/WorkspacesApi.md#favorite_workspace) | **POST** /api/v3/workspaces/{id}/favorite | Favorite Workspace
*WorkspacesApi* | [**list_types_available_in_a_workspace**](auto_slopp/openproject/openapi_client/docs/WorkspacesApi.md#list_types_available_in_a_workspace) | **GET** /api/v3/workspaces/{id}/types | List types available in a workspace
*WorkspacesApi* | [**unfavorite_workspace**](auto_slopp/openproject/openapi_client/docs/WorkspacesApi.md#unfavorite_workspace) | **DELETE** /api/v3/workspaces/{id}/favorite | Unfavorite Workspace
*WorkspacesApi* | [**view_workspace_schema**](auto_slopp/openproject/openapi_client/docs/WorkspacesApi.md#view_workspace_schema) | **GET** /api/v3/workspaces/schema | View workspace schema
*DefaultApi* | [**get_custom_field_item**](auto_slopp/openproject/openapi_client/docs/DefaultApi.md#get_custom_field_item) | **GET** /api/v3/custom_field_items/{id} | Get a custom field hierarchy item
*DefaultApi* | [**get_custom_field_item_branch**](auto_slopp/openproject/openapi_client/docs/DefaultApi.md#get_custom_field_item_branch) | **GET** /api/v3/custom_field_items/{id}/branch | Get a custom field hierarchy item&#39;s branch
*DefaultApi* | [**get_custom_field_items**](auto_slopp/openproject/openapi_client/docs/DefaultApi.md#get_custom_field_items) | **GET** /api/v3/custom_fields/{id}/items | Get the custom field hierarchy items


## Documentation For Models

 - [ActivityCommentWriteModel](auto_slopp/openproject/openapi_client/docs/ActivityCommentWriteModel.md)
 - [ActivityCommentWriteModelComment](auto_slopp/openproject/openapi_client/docs/ActivityCommentWriteModelComment.md)
 - [ActivityModel](auto_slopp/openproject/openapi_client/docs/ActivityModel.md)
 - [ActivityModelEmbedded](auto_slopp/openproject/openapi_client/docs/ActivityModelEmbedded.md)
 - [ActivityModelLinks](auto_slopp/openproject/openapi_client/docs/ActivityModelLinks.md)
 - [AddWatcherRequest](auto_slopp/openproject/openapi_client/docs/AddWatcherRequest.md)
 - [AttachmentModel](auto_slopp/openproject/openapi_client/docs/AttachmentModel.md)
 - [AttachmentModelDigest](auto_slopp/openproject/openapi_client/docs/AttachmentModelDigest.md)
 - [AttachmentModelLinks](auto_slopp/openproject/openapi_client/docs/AttachmentModelLinks.md)
 - [AttachmentsModel](auto_slopp/openproject/openapi_client/docs/AttachmentsModel.md)
 - [AttachmentsModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/AttachmentsModelAllOfEmbedded.md)
 - [AttachmentsModelAllOfEmbeddedElements](auto_slopp/openproject/openapi_client/docs/AttachmentsModelAllOfEmbeddedElements.md)
 - [AttachmentsModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/AttachmentsModelAllOfLinks.md)
 - [AvailableAssigneesModel](auto_slopp/openproject/openapi_client/docs/AvailableAssigneesModel.md)
 - [AvailableAssigneesModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/AvailableAssigneesModelAllOfEmbedded.md)
 - [AvailableAssigneesModelAllOfEmbeddedElements](auto_slopp/openproject/openapi_client/docs/AvailableAssigneesModelAllOfEmbeddedElements.md)
 - [AvailableAssigneesModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/AvailableAssigneesModelAllOfLinks.md)
 - [BudgetModel](auto_slopp/openproject/openapi_client/docs/BudgetModel.md)
 - [BudgetModelLinks](auto_slopp/openproject/openapi_client/docs/BudgetModelLinks.md)
 - [CategoriesByWorkspaceModel](auto_slopp/openproject/openapi_client/docs/CategoriesByWorkspaceModel.md)
 - [CategoriesByWorkspaceModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/CategoriesByWorkspaceModelAllOfEmbedded.md)
 - [CategoriesByWorkspaceModelAllOfEmbeddedElements](auto_slopp/openproject/openapi_client/docs/CategoriesByWorkspaceModelAllOfEmbeddedElements.md)
 - [CategoriesByWorkspaceModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/CategoriesByWorkspaceModelAllOfLinks.md)
 - [CategoryModel](auto_slopp/openproject/openapi_client/docs/CategoryModel.md)
 - [CategoryModelLinks](auto_slopp/openproject/openapi_client/docs/CategoryModelLinks.md)
 - [CollectionLinks](auto_slopp/openproject/openapi_client/docs/CollectionLinks.md)
 - [CollectionModel](auto_slopp/openproject/openapi_client/docs/CollectionModel.md)
 - [ConfigurationModel](auto_slopp/openproject/openapi_client/docs/ConfigurationModel.md)
 - [CreateViewsRequest](auto_slopp/openproject/openapi_client/docs/CreateViewsRequest.md)
 - [CreateViewsRequestLinks](auto_slopp/openproject/openapi_client/docs/CreateViewsRequestLinks.md)
 - [CreateViewsRequestLinksQuery](auto_slopp/openproject/openapi_client/docs/CreateViewsRequestLinksQuery.md)
 - [CreateWorkPackageReminderRequest](auto_slopp/openproject/openapi_client/docs/CreateWorkPackageReminderRequest.md)
 - [CustomActionModel](auto_slopp/openproject/openapi_client/docs/CustomActionModel.md)
 - [CustomActionModelLinks](auto_slopp/openproject/openapi_client/docs/CustomActionModelLinks.md)
 - [CustomOptionModel](auto_slopp/openproject/openapi_client/docs/CustomOptionModel.md)
 - [CustomOptionModelLinks](auto_slopp/openproject/openapi_client/docs/CustomOptionModelLinks.md)
 - [DayCollectionModel](auto_slopp/openproject/openapi_client/docs/DayCollectionModel.md)
 - [DayCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/DayCollectionModelAllOfEmbedded.md)
 - [DayCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/DayCollectionModelAllOfLinks.md)
 - [DayModel](auto_slopp/openproject/openapi_client/docs/DayModel.md)
 - [DayModelLinks](auto_slopp/openproject/openapi_client/docs/DayModelLinks.md)
 - [DocumentModel](auto_slopp/openproject/openapi_client/docs/DocumentModel.md)
 - [DocumentModelLinks](auto_slopp/openproject/openapi_client/docs/DocumentModelLinks.md)
 - [EmojiReactionModel](auto_slopp/openproject/openapi_client/docs/EmojiReactionModel.md)
 - [EmojiReactionModelLinks](auto_slopp/openproject/openapi_client/docs/EmojiReactionModelLinks.md)
 - [EmojiReactionsModel](auto_slopp/openproject/openapi_client/docs/EmojiReactionsModel.md)
 - [EmojiReactionsModelEmbedded](auto_slopp/openproject/openapi_client/docs/EmojiReactionsModelEmbedded.md)
 - [EmojiReactionsModelLinks](auto_slopp/openproject/openapi_client/docs/EmojiReactionsModelLinks.md)
 - [ErrorResponse](auto_slopp/openproject/openapi_client/docs/ErrorResponse.md)
 - [ErrorResponseEmbedded](auto_slopp/openproject/openapi_client/docs/ErrorResponseEmbedded.md)
 - [ErrorResponseEmbeddedDetails](auto_slopp/openproject/openapi_client/docs/ErrorResponseEmbeddedDetails.md)
 - [ExecuteCustomActionRequest](auto_slopp/openproject/openapi_client/docs/ExecuteCustomActionRequest.md)
 - [ExecuteCustomActionRequestLinks](auto_slopp/openproject/openapi_client/docs/ExecuteCustomActionRequestLinks.md)
 - [ExecuteCustomActionRequestLinksWorkPackage](auto_slopp/openproject/openapi_client/docs/ExecuteCustomActionRequestLinksWorkPackage.md)
 - [FileLinkCollectionReadModel](auto_slopp/openproject/openapi_client/docs/FileLinkCollectionReadModel.md)
 - [FileLinkCollectionReadModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/FileLinkCollectionReadModelAllOfEmbedded.md)
 - [FileLinkCollectionReadModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/FileLinkCollectionReadModelAllOfLinks.md)
 - [FileLinkCollectionWriteModel](auto_slopp/openproject/openapi_client/docs/FileLinkCollectionWriteModel.md)
 - [FileLinkCollectionWriteModelEmbedded](auto_slopp/openproject/openapi_client/docs/FileLinkCollectionWriteModelEmbedded.md)
 - [FileLinkOriginDataModel](auto_slopp/openproject/openapi_client/docs/FileLinkOriginDataModel.md)
 - [FileLinkReadModel](auto_slopp/openproject/openapi_client/docs/FileLinkReadModel.md)
 - [FileLinkReadModelEmbedded](auto_slopp/openproject/openapi_client/docs/FileLinkReadModelEmbedded.md)
 - [FileLinkReadModelLinks](auto_slopp/openproject/openapi_client/docs/FileLinkReadModelLinks.md)
 - [FileLinkWriteModel](auto_slopp/openproject/openapi_client/docs/FileLinkWriteModel.md)
 - [FileLinkWriteModelLinks](auto_slopp/openproject/openapi_client/docs/FileLinkWriteModelLinks.md)
 - [FileLinkWriteModelLinksOneOf](auto_slopp/openproject/openapi_client/docs/FileLinkWriteModelLinksOneOf.md)
 - [FileLinkWriteModelLinksOneOf1](auto_slopp/openproject/openapi_client/docs/FileLinkWriteModelLinksOneOf1.md)
 - [FileUploadFormMetadata](auto_slopp/openproject/openapi_client/docs/FileUploadFormMetadata.md)
 - [Formattable](auto_slopp/openproject/openapi_client/docs/Formattable.md)
 - [GridCollectionModel](auto_slopp/openproject/openapi_client/docs/GridCollectionModel.md)
 - [GridCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/GridCollectionModelAllOfEmbedded.md)
 - [GridReadModel](auto_slopp/openproject/openapi_client/docs/GridReadModel.md)
 - [GridReadModelLinks](auto_slopp/openproject/openapi_client/docs/GridReadModelLinks.md)
 - [GridWidgetModel](auto_slopp/openproject/openapi_client/docs/GridWidgetModel.md)
 - [GridWriteModel](auto_slopp/openproject/openapi_client/docs/GridWriteModel.md)
 - [GridWriteModelLinks](auto_slopp/openproject/openapi_client/docs/GridWriteModelLinks.md)
 - [GroupCollectionModel](auto_slopp/openproject/openapi_client/docs/GroupCollectionModel.md)
 - [GroupCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/GroupCollectionModelAllOfEmbedded.md)
 - [GroupCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/GroupCollectionModelAllOfLinks.md)
 - [GroupModel](auto_slopp/openproject/openapi_client/docs/GroupModel.md)
 - [GroupModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/GroupModelAllOfEmbedded.md)
 - [GroupModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/GroupModelAllOfLinks.md)
 - [GroupModelAllOfLinksMembers](auto_slopp/openproject/openapi_client/docs/GroupModelAllOfLinksMembers.md)
 - [GroupWriteModel](auto_slopp/openproject/openapi_client/docs/GroupWriteModel.md)
 - [GroupWriteModelLinks](auto_slopp/openproject/openapi_client/docs/GroupWriteModelLinks.md)
 - [HelpTextCollectionModel](auto_slopp/openproject/openapi_client/docs/HelpTextCollectionModel.md)
 - [HelpTextCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/HelpTextCollectionModelAllOfEmbedded.md)
 - [HelpTextCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/HelpTextCollectionModelAllOfLinks.md)
 - [HelpTextModel](auto_slopp/openproject/openapi_client/docs/HelpTextModel.md)
 - [HelpTextModelLinks](auto_slopp/openproject/openapi_client/docs/HelpTextModelLinks.md)
 - [HierarchyItemCollectionModel](auto_slopp/openproject/openapi_client/docs/HierarchyItemCollectionModel.md)
 - [HierarchyItemCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/HierarchyItemCollectionModelAllOfEmbedded.md)
 - [HierarchyItemCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/HierarchyItemCollectionModelAllOfLinks.md)
 - [HierarchyItemReadModel](auto_slopp/openproject/openapi_client/docs/HierarchyItemReadModel.md)
 - [HierarchyItemReadModelLinks](auto_slopp/openproject/openapi_client/docs/HierarchyItemReadModelLinks.md)
 - [Link](auto_slopp/openproject/openapi_client/docs/Link.md)
 - [ListAvailableParentProjectCandidatesModel](auto_slopp/openproject/openapi_client/docs/ListAvailableParentProjectCandidatesModel.md)
 - [ListAvailableParentProjectCandidatesModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/ListAvailableParentProjectCandidatesModelAllOfEmbedded.md)
 - [ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements](auto_slopp/openproject/openapi_client/docs/ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements.md)
 - [ListAvailableParentProjectCandidatesModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/ListAvailableParentProjectCandidatesModelAllOfLinks.md)
 - [ListReminders200Response](auto_slopp/openproject/openapi_client/docs/ListReminders200Response.md)
 - [ListReminders200ResponseEmbedded](auto_slopp/openproject/openapi_client/docs/ListReminders200ResponseEmbedded.md)
 - [MeetingModel](auto_slopp/openproject/openapi_client/docs/MeetingModel.md)
 - [MeetingModelLinks](auto_slopp/openproject/openapi_client/docs/MeetingModelLinks.md)
 - [MembershipCollectionModel](auto_slopp/openproject/openapi_client/docs/MembershipCollectionModel.md)
 - [MembershipCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/MembershipCollectionModelAllOfEmbedded.md)
 - [MembershipFormModel](auto_slopp/openproject/openapi_client/docs/MembershipFormModel.md)
 - [MembershipFormModelEmbedded](auto_slopp/openproject/openapi_client/docs/MembershipFormModelEmbedded.md)
 - [MembershipFormModelEmbeddedValidationError](auto_slopp/openproject/openapi_client/docs/MembershipFormModelEmbeddedValidationError.md)
 - [MembershipFormModelLinks](auto_slopp/openproject/openapi_client/docs/MembershipFormModelLinks.md)
 - [MembershipReadModel](auto_slopp/openproject/openapi_client/docs/MembershipReadModel.md)
 - [MembershipReadModelEmbedded](auto_slopp/openproject/openapi_client/docs/MembershipReadModelEmbedded.md)
 - [MembershipReadModelEmbeddedPrincipal](auto_slopp/openproject/openapi_client/docs/MembershipReadModelEmbeddedPrincipal.md)
 - [MembershipReadModelEmbeddedProject](auto_slopp/openproject/openapi_client/docs/MembershipReadModelEmbeddedProject.md)
 - [MembershipReadModelLinks](auto_slopp/openproject/openapi_client/docs/MembershipReadModelLinks.md)
 - [MembershipSchemaModel](auto_slopp/openproject/openapi_client/docs/MembershipSchemaModel.md)
 - [MembershipWriteModel](auto_slopp/openproject/openapi_client/docs/MembershipWriteModel.md)
 - [MembershipWriteModelLinks](auto_slopp/openproject/openapi_client/docs/MembershipWriteModelLinks.md)
 - [MembershipWriteModelMeta](auto_slopp/openproject/openapi_client/docs/MembershipWriteModelMeta.md)
 - [NewsCreateModel](auto_slopp/openproject/openapi_client/docs/NewsCreateModel.md)
 - [NewsCreateModelLinks](auto_slopp/openproject/openapi_client/docs/NewsCreateModelLinks.md)
 - [NewsModel](auto_slopp/openproject/openapi_client/docs/NewsModel.md)
 - [NewsModelLinks](auto_slopp/openproject/openapi_client/docs/NewsModelLinks.md)
 - [NonWorkingDayCollectionModel](auto_slopp/openproject/openapi_client/docs/NonWorkingDayCollectionModel.md)
 - [NonWorkingDayCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/NonWorkingDayCollectionModelAllOfEmbedded.md)
 - [NonWorkingDayCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/NonWorkingDayCollectionModelAllOfLinks.md)
 - [NonWorkingDayModel](auto_slopp/openproject/openapi_client/docs/NonWorkingDayModel.md)
 - [NonWorkingDayModelLinks](auto_slopp/openproject/openapi_client/docs/NonWorkingDayModelLinks.md)
 - [NotificationCollectionModel](auto_slopp/openproject/openapi_client/docs/NotificationCollectionModel.md)
 - [NotificationCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/NotificationCollectionModelAllOfEmbedded.md)
 - [NotificationCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/NotificationCollectionModelAllOfLinks.md)
 - [NotificationModel](auto_slopp/openproject/openapi_client/docs/NotificationModel.md)
 - [NotificationModelEmbedded](auto_slopp/openproject/openapi_client/docs/NotificationModelEmbedded.md)
 - [NotificationModelLinks](auto_slopp/openproject/openapi_client/docs/NotificationModelLinks.md)
 - [OAuthApplicationReadModel](auto_slopp/openproject/openapi_client/docs/OAuthApplicationReadModel.md)
 - [OAuthApplicationReadModelLinks](auto_slopp/openproject/openapi_client/docs/OAuthApplicationReadModelLinks.md)
 - [OAuthClientCredentialsReadModel](auto_slopp/openproject/openapi_client/docs/OAuthClientCredentialsReadModel.md)
 - [OAuthClientCredentialsReadModelLinks](auto_slopp/openproject/openapi_client/docs/OAuthClientCredentialsReadModelLinks.md)
 - [OAuthClientCredentialsWriteModel](auto_slopp/openproject/openapi_client/docs/OAuthClientCredentialsWriteModel.md)
 - [OffsetPaginatedCollectionLinks](auto_slopp/openproject/openapi_client/docs/OffsetPaginatedCollectionLinks.md)
 - [OffsetPaginatedCollectionModel](auto_slopp/openproject/openapi_client/docs/OffsetPaginatedCollectionModel.md)
 - [PaginatedCollectionModel](auto_slopp/openproject/openapi_client/docs/PaginatedCollectionModel.md)
 - [PaginatedCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/PaginatedCollectionModelAllOfLinks.md)
 - [PlaceholderUserCollectionModel](auto_slopp/openproject/openapi_client/docs/PlaceholderUserCollectionModel.md)
 - [PlaceholderUserCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/PlaceholderUserCollectionModelAllOfEmbedded.md)
 - [PlaceholderUserCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/PlaceholderUserCollectionModelAllOfLinks.md)
 - [PlaceholderUserCreateModel](auto_slopp/openproject/openapi_client/docs/PlaceholderUserCreateModel.md)
 - [PlaceholderUserModel](auto_slopp/openproject/openapi_client/docs/PlaceholderUserModel.md)
 - [PlaceholderUserModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/PlaceholderUserModelAllOfLinks.md)
 - [PortfolioCollectionModel](auto_slopp/openproject/openapi_client/docs/PortfolioCollectionModel.md)
 - [PortfolioCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/PortfolioCollectionModelAllOfEmbedded.md)
 - [PortfolioCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/PortfolioCollectionModelAllOfLinks.md)
 - [PortfolioModel](auto_slopp/openproject/openapi_client/docs/PortfolioModel.md)
 - [PortfolioModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/PortfolioModelAllOfLinks.md)
 - [PortfolioModelAllOfLinksAncestors](auto_slopp/openproject/openapi_client/docs/PortfolioModelAllOfLinksAncestors.md)
 - [PortfolioModelAllOfLinksStorages](auto_slopp/openproject/openapi_client/docs/PortfolioModelAllOfLinksStorages.md)
 - [PostModel](auto_slopp/openproject/openapi_client/docs/PostModel.md)
 - [PostModelLinks](auto_slopp/openproject/openapi_client/docs/PostModelLinks.md)
 - [PrincipalCollectionModel](auto_slopp/openproject/openapi_client/docs/PrincipalCollectionModel.md)
 - [PrincipalCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/PrincipalCollectionModelAllOfEmbedded.md)
 - [PrincipalCollectionModelAllOfEmbeddedElements](auto_slopp/openproject/openapi_client/docs/PrincipalCollectionModelAllOfEmbeddedElements.md)
 - [PrincipalModel](auto_slopp/openproject/openapi_client/docs/PrincipalModel.md)
 - [PrincipalModelLinks](auto_slopp/openproject/openapi_client/docs/PrincipalModelLinks.md)
 - [PriorityCollectionModel](auto_slopp/openproject/openapi_client/docs/PriorityCollectionModel.md)
 - [PriorityCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/PriorityCollectionModelAllOfEmbedded.md)
 - [PriorityCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/PriorityCollectionModelAllOfLinks.md)
 - [PriorityCollectionModelAllOfLinksSelf](auto_slopp/openproject/openapi_client/docs/PriorityCollectionModelAllOfLinksSelf.md)
 - [PriorityModel](auto_slopp/openproject/openapi_client/docs/PriorityModel.md)
 - [PriorityModelLinks](auto_slopp/openproject/openapi_client/docs/PriorityModelLinks.md)
 - [ProgramCollectionModel](auto_slopp/openproject/openapi_client/docs/ProgramCollectionModel.md)
 - [ProgramCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/ProgramCollectionModelAllOfEmbedded.md)
 - [ProgramCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/ProgramCollectionModelAllOfLinks.md)
 - [ProgramModel](auto_slopp/openproject/openapi_client/docs/ProgramModel.md)
 - [ProgramModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/ProgramModelAllOfLinks.md)
 - [ProgramModelAllOfLinksAncestors](auto_slopp/openproject/openapi_client/docs/ProgramModelAllOfLinksAncestors.md)
 - [ProgramModelAllOfLinksStorages](auto_slopp/openproject/openapi_client/docs/ProgramModelAllOfLinksStorages.md)
 - [ProjectCollectionModel](auto_slopp/openproject/openapi_client/docs/ProjectCollectionModel.md)
 - [ProjectCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/ProjectCollectionModelAllOfEmbedded.md)
 - [ProjectCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/ProjectCollectionModelAllOfLinks.md)
 - [ProjectConfigurationModel](auto_slopp/openproject/openapi_client/docs/ProjectConfigurationModel.md)
 - [ProjectModel](auto_slopp/openproject/openapi_client/docs/ProjectModel.md)
 - [ProjectModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/ProjectModelAllOfLinks.md)
 - [ProjectModelAllOfLinksAncestors](auto_slopp/openproject/openapi_client/docs/ProjectModelAllOfLinksAncestors.md)
 - [ProjectModelAllOfLinksStorages](auto_slopp/openproject/openapi_client/docs/ProjectModelAllOfLinksStorages.md)
 - [ProjectPhaseDefinitionCollectionModel](auto_slopp/openproject/openapi_client/docs/ProjectPhaseDefinitionCollectionModel.md)
 - [ProjectPhaseDefinitionCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/ProjectPhaseDefinitionCollectionModelAllOfEmbedded.md)
 - [ProjectPhaseDefinitionCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/ProjectPhaseDefinitionCollectionModelAllOfLinks.md)
 - [ProjectPhaseDefinitionModel](auto_slopp/openproject/openapi_client/docs/ProjectPhaseDefinitionModel.md)
 - [ProjectPhaseDefinitionModelLinks](auto_slopp/openproject/openapi_client/docs/ProjectPhaseDefinitionModelLinks.md)
 - [ProjectPhaseModel](auto_slopp/openproject/openapi_client/docs/ProjectPhaseModel.md)
 - [ProjectPhaseModelLinks](auto_slopp/openproject/openapi_client/docs/ProjectPhaseModelLinks.md)
 - [ProjectStorageCollectionModel](auto_slopp/openproject/openapi_client/docs/ProjectStorageCollectionModel.md)
 - [ProjectStorageCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/ProjectStorageCollectionModelAllOfEmbedded.md)
 - [ProjectStorageCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/ProjectStorageCollectionModelAllOfLinks.md)
 - [ProjectStorageModel](auto_slopp/openproject/openapi_client/docs/ProjectStorageModel.md)
 - [ProjectStorageModelLinks](auto_slopp/openproject/openapi_client/docs/ProjectStorageModelLinks.md)
 - [QueryColumnModel](auto_slopp/openproject/openapi_client/docs/QueryColumnModel.md)
 - [QueryCreateForm](auto_slopp/openproject/openapi_client/docs/QueryCreateForm.md)
 - [QueryFilterInstanceModel](auto_slopp/openproject/openapi_client/docs/QueryFilterInstanceModel.md)
 - [QueryFilterInstanceModelLinks](auto_slopp/openproject/openapi_client/docs/QueryFilterInstanceModelLinks.md)
 - [QueryFilterInstanceSchemaModel](auto_slopp/openproject/openapi_client/docs/QueryFilterInstanceSchemaModel.md)
 - [QueryFilterInstanceSchemaModelLinks](auto_slopp/openproject/openapi_client/docs/QueryFilterInstanceSchemaModelLinks.md)
 - [QueryFilterModel](auto_slopp/openproject/openapi_client/docs/QueryFilterModel.md)
 - [QueryModel](auto_slopp/openproject/openapi_client/docs/QueryModel.md)
 - [QueryModelLinks](auto_slopp/openproject/openapi_client/docs/QueryModelLinks.md)
 - [QueryOperatorModel](auto_slopp/openproject/openapi_client/docs/QueryOperatorModel.md)
 - [QuerySortByModel](auto_slopp/openproject/openapi_client/docs/QuerySortByModel.md)
 - [QueryUpdateForm](auto_slopp/openproject/openapi_client/docs/QueryUpdateForm.md)
 - [RelationCollectionModel](auto_slopp/openproject/openapi_client/docs/RelationCollectionModel.md)
 - [RelationCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/RelationCollectionModelAllOfEmbedded.md)
 - [RelationCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/RelationCollectionModelAllOfLinks.md)
 - [RelationReadModel](auto_slopp/openproject/openapi_client/docs/RelationReadModel.md)
 - [RelationReadModelEmbedded](auto_slopp/openproject/openapi_client/docs/RelationReadModelEmbedded.md)
 - [RelationReadModelLinks](auto_slopp/openproject/openapi_client/docs/RelationReadModelLinks.md)
 - [RelationWriteModel](auto_slopp/openproject/openapi_client/docs/RelationWriteModel.md)
 - [RelationWriteModelLinks](auto_slopp/openproject/openapi_client/docs/RelationWriteModelLinks.md)
 - [ReminderModel](auto_slopp/openproject/openapi_client/docs/ReminderModel.md)
 - [ReminderModelLinks](auto_slopp/openproject/openapi_client/docs/ReminderModelLinks.md)
 - [RevisionModel](auto_slopp/openproject/openapi_client/docs/RevisionModel.md)
 - [RevisionModelLinks](auto_slopp/openproject/openapi_client/docs/RevisionModelLinks.md)
 - [RoleModel](auto_slopp/openproject/openapi_client/docs/RoleModel.md)
 - [RoleModelLinks](auto_slopp/openproject/openapi_client/docs/RoleModelLinks.md)
 - [RootModel](auto_slopp/openproject/openapi_client/docs/RootModel.md)
 - [RootModelLinks](auto_slopp/openproject/openapi_client/docs/RootModelLinks.md)
 - [SchemaModel](auto_slopp/openproject/openapi_client/docs/SchemaModel.md)
 - [SchemaModelLinks](auto_slopp/openproject/openapi_client/docs/SchemaModelLinks.md)
 - [SchemaPropertyModel](auto_slopp/openproject/openapi_client/docs/SchemaPropertyModel.md)
 - [ShowOrValidateFormRequest](auto_slopp/openproject/openapi_client/docs/ShowOrValidateFormRequest.md)
 - [StatusCollectionModel](auto_slopp/openproject/openapi_client/docs/StatusCollectionModel.md)
 - [StatusCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/StatusCollectionModelAllOfEmbedded.md)
 - [StatusModel](auto_slopp/openproject/openapi_client/docs/StatusModel.md)
 - [StatusModelLinks](auto_slopp/openproject/openapi_client/docs/StatusModelLinks.md)
 - [StorageCollectionModel](auto_slopp/openproject/openapi_client/docs/StorageCollectionModel.md)
 - [StorageCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/StorageCollectionModelAllOfEmbedded.md)
 - [StorageCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/StorageCollectionModelAllOfLinks.md)
 - [StorageFileModel](auto_slopp/openproject/openapi_client/docs/StorageFileModel.md)
 - [StorageFileModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/StorageFileModelAllOfLinks.md)
 - [StorageFileUploadLinkModel](auto_slopp/openproject/openapi_client/docs/StorageFileUploadLinkModel.md)
 - [StorageFileUploadLinkModelLinks](auto_slopp/openproject/openapi_client/docs/StorageFileUploadLinkModelLinks.md)
 - [StorageFileUploadPreparationModel](auto_slopp/openproject/openapi_client/docs/StorageFileUploadPreparationModel.md)
 - [StorageFilesModel](auto_slopp/openproject/openapi_client/docs/StorageFilesModel.md)
 - [StorageFolderWriteModel](auto_slopp/openproject/openapi_client/docs/StorageFolderWriteModel.md)
 - [StorageReadModel](auto_slopp/openproject/openapi_client/docs/StorageReadModel.md)
 - [StorageReadModelEmbedded](auto_slopp/openproject/openapi_client/docs/StorageReadModelEmbedded.md)
 - [StorageReadModelLinks](auto_slopp/openproject/openapi_client/docs/StorageReadModelLinks.md)
 - [StorageWriteModel](auto_slopp/openproject/openapi_client/docs/StorageWriteModel.md)
 - [StorageWriteModelLinks](auto_slopp/openproject/openapi_client/docs/StorageWriteModelLinks.md)
 - [TimeEntryActivityModel](auto_slopp/openproject/openapi_client/docs/TimeEntryActivityModel.md)
 - [TimeEntryActivityModelEmbedded](auto_slopp/openproject/openapi_client/docs/TimeEntryActivityModelEmbedded.md)
 - [TimeEntryActivityModelLinks](auto_slopp/openproject/openapi_client/docs/TimeEntryActivityModelLinks.md)
 - [TimeEntryCollectionModel](auto_slopp/openproject/openapi_client/docs/TimeEntryCollectionModel.md)
 - [TimeEntryCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/TimeEntryCollectionModelAllOfEmbedded.md)
 - [TimeEntryCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/TimeEntryCollectionModelAllOfLinks.md)
 - [TimeEntryModel](auto_slopp/openproject/openapi_client/docs/TimeEntryModel.md)
 - [TimeEntryModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/TimeEntryModelAllOfLinks.md)
 - [ToggleActivityEmojiReactionRequest](auto_slopp/openproject/openapi_client/docs/ToggleActivityEmojiReactionRequest.md)
 - [TypeModel](auto_slopp/openproject/openapi_client/docs/TypeModel.md)
 - [TypeModelLinks](auto_slopp/openproject/openapi_client/docs/TypeModelLinks.md)
 - [TypesByWorkspaceModel](auto_slopp/openproject/openapi_client/docs/TypesByWorkspaceModel.md)
 - [TypesByWorkspaceModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/TypesByWorkspaceModelAllOfEmbedded.md)
 - [TypesByWorkspaceModelAllOfEmbeddedElements](auto_slopp/openproject/openapi_client/docs/TypesByWorkspaceModelAllOfEmbeddedElements.md)
 - [TypesByWorkspaceModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/TypesByWorkspaceModelAllOfLinks.md)
 - [UpdateDocumentRequest](auto_slopp/openproject/openapi_client/docs/UpdateDocumentRequest.md)
 - [UpdateDocumentRequestDescription](auto_slopp/openproject/openapi_client/docs/UpdateDocumentRequestDescription.md)
 - [UpdateReminderRequest](auto_slopp/openproject/openapi_client/docs/UpdateReminderRequest.md)
 - [UpdateUserPreferencesRequest](auto_slopp/openproject/openapi_client/docs/UpdateUserPreferencesRequest.md)
 - [UserCollectionModel](auto_slopp/openproject/openapi_client/docs/UserCollectionModel.md)
 - [UserCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/UserCollectionModelAllOfEmbedded.md)
 - [UserCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/UserCollectionModelAllOfLinks.md)
 - [UserCreateModel](auto_slopp/openproject/openapi_client/docs/UserCreateModel.md)
 - [UserModel](auto_slopp/openproject/openapi_client/docs/UserModel.md)
 - [UserModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/UserModelAllOfLinks.md)
 - [ValuesPropertyModel](auto_slopp/openproject/openapi_client/docs/ValuesPropertyModel.md)
 - [ValuesPropertyModelLinks](auto_slopp/openproject/openapi_client/docs/ValuesPropertyModelLinks.md)
 - [VersionCollectionModel](auto_slopp/openproject/openapi_client/docs/VersionCollectionModel.md)
 - [VersionCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/VersionCollectionModelAllOfEmbedded.md)
 - [VersionCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/VersionCollectionModelAllOfLinks.md)
 - [VersionReadModel](auto_slopp/openproject/openapi_client/docs/VersionReadModel.md)
 - [VersionReadModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/VersionReadModelAllOfLinks.md)
 - [VersionWriteModel](auto_slopp/openproject/openapi_client/docs/VersionWriteModel.md)
 - [VersionWriteModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/VersionWriteModelAllOfLinks.md)
 - [VersionsByWorkspaceModel](auto_slopp/openproject/openapi_client/docs/VersionsByWorkspaceModel.md)
 - [VersionsByWorkspaceModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/VersionsByWorkspaceModelAllOfEmbedded.md)
 - [VersionsByWorkspaceModelAllOfEmbeddedElements](auto_slopp/openproject/openapi_client/docs/VersionsByWorkspaceModelAllOfEmbeddedElements.md)
 - [VersionsByWorkspaceModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/VersionsByWorkspaceModelAllOfLinks.md)
 - [WatchersModel](auto_slopp/openproject/openapi_client/docs/WatchersModel.md)
 - [WatchersModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/WatchersModelAllOfEmbedded.md)
 - [WatchersModelAllOfEmbeddedElements](auto_slopp/openproject/openapi_client/docs/WatchersModelAllOfEmbeddedElements.md)
 - [WatchersModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/WatchersModelAllOfLinks.md)
 - [WeekDayCollectionModel](auto_slopp/openproject/openapi_client/docs/WeekDayCollectionModel.md)
 - [WeekDayCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/WeekDayCollectionModelAllOfEmbedded.md)
 - [WeekDayCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/WeekDayCollectionModelAllOfLinks.md)
 - [WeekDayCollectionWriteModel](auto_slopp/openproject/openapi_client/docs/WeekDayCollectionWriteModel.md)
 - [WeekDayCollectionWriteModelEmbedded](auto_slopp/openproject/openapi_client/docs/WeekDayCollectionWriteModelEmbedded.md)
 - [WeekDayCollectionWriteModelEmbeddedElementsInner](auto_slopp/openproject/openapi_client/docs/WeekDayCollectionWriteModelEmbeddedElementsInner.md)
 - [WeekDayModel](auto_slopp/openproject/openapi_client/docs/WeekDayModel.md)
 - [WeekDaySelfLinkModel](auto_slopp/openproject/openapi_client/docs/WeekDaySelfLinkModel.md)
 - [WeekDayWriteModel](auto_slopp/openproject/openapi_client/docs/WeekDayWriteModel.md)
 - [WikiPageModel](auto_slopp/openproject/openapi_client/docs/WikiPageModel.md)
 - [WikiPageModelLinks](auto_slopp/openproject/openapi_client/docs/WikiPageModelLinks.md)
 - [WorkPackageFormModel](auto_slopp/openproject/openapi_client/docs/WorkPackageFormModel.md)
 - [WorkPackageFormModelEmbedded](auto_slopp/openproject/openapi_client/docs/WorkPackageFormModelEmbedded.md)
 - [WorkPackageFormModelLinks](auto_slopp/openproject/openapi_client/docs/WorkPackageFormModelLinks.md)
 - [WorkPackageModel](auto_slopp/openproject/openapi_client/docs/WorkPackageModel.md)
 - [WorkPackageModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/WorkPackageModelAllOfLinks.md)
 - [WorkPackageModelAllOfLinksAncestors](auto_slopp/openproject/openapi_client/docs/WorkPackageModelAllOfLinksAncestors.md)
 - [WorkPackageModelAllOfLinksChildren](auto_slopp/openproject/openapi_client/docs/WorkPackageModelAllOfLinksChildren.md)
 - [WorkPackageModelAllOfLinksCustomActions](auto_slopp/openproject/openapi_client/docs/WorkPackageModelAllOfLinksCustomActions.md)
 - [WorkPackagePatchModel](auto_slopp/openproject/openapi_client/docs/WorkPackagePatchModel.md)
 - [WorkPackageSchemaModel](auto_slopp/openproject/openapi_client/docs/WorkPackageSchemaModel.md)
 - [WorkPackageSchemaModelLinks](auto_slopp/openproject/openapi_client/docs/WorkPackageSchemaModelLinks.md)
 - [WorkPackageWriteModel](auto_slopp/openproject/openapi_client/docs/WorkPackageWriteModel.md)
 - [WorkPackageWriteModelLinks](auto_slopp/openproject/openapi_client/docs/WorkPackageWriteModelLinks.md)
 - [WorkPackageWriteModelMeta](auto_slopp/openproject/openapi_client/docs/WorkPackageWriteModelMeta.md)
 - [WorkPackagesModel](auto_slopp/openproject/openapi_client/docs/WorkPackagesModel.md)
 - [WorkPackagesModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/WorkPackagesModelAllOfEmbedded.md)
 - [WorkPackagesModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/WorkPackagesModelAllOfLinks.md)
 - [WorkspaceCollectionModel](auto_slopp/openproject/openapi_client/docs/WorkspaceCollectionModel.md)
 - [WorkspaceCollectionModelAllOfEmbedded](auto_slopp/openproject/openapi_client/docs/WorkspaceCollectionModelAllOfEmbedded.md)
 - [WorkspaceCollectionModelAllOfEmbeddedElements](auto_slopp/openproject/openapi_client/docs/WorkspaceCollectionModelAllOfEmbeddedElements.md)
 - [WorkspaceCollectionModelAllOfLinks](auto_slopp/openproject/openapi_client/docs/WorkspaceCollectionModelAllOfLinks.md)
 - [WorkspacesSchemaModel](auto_slopp/openproject/openapi_client/docs/WorkspacesSchemaModel.md)
 - [WorkspacesSchemaModelAttributeGroupsInner](auto_slopp/openproject/openapi_client/docs/WorkspacesSchemaModelAttributeGroupsInner.md)
 - [WorkspacesSchemaModelLinks](auto_slopp/openproject/openapi_client/docs/WorkspacesSchemaModelLinks.md)
 - [WorkspacesSchemaModelLinksSelf](auto_slopp/openproject/openapi_client/docs/WorkspacesSchemaModelLinksSelf.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="BasicAuth"></a>
### BasicAuth

- **Type**: HTTP basic authentication


## Author




