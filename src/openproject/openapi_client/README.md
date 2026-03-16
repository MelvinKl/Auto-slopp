# openproject-client
You're looking at the current **stable** documentation of the OpenProject APIv3. If you're interested in the current
development version, please go to [github.com/opf](https://github.com/opf/openproject/tree/dev/docs/api/apiv3).

## Introduction

The documentation for the APIv3 is written according to the [OpenAPI 3.1 Specification](https://swagger.io/specification/).
You can either view the static version of this documentation on the [website](https://www.openproject.org/docs/api/introduction/)
or the interactive version, rendered with [OpenAPI Explorer](https://github.com/Rhosys/openapi-explorer/blob/main/README.md),
in your OpenProject installation under `/api/docs`.
In the latter you can try out the various API endpoints directly interacting with our OpenProject data.
Moreover you can access the specification source itself under `/api/v3/spec.json` and `/api/v3/spec.yml`
(e.g. [here](https://community.openproject.org/api/v3/spec.yml)).

The APIv3 is a hypermedia REST API, a shorthand for \"Hypermedia As The Engine Of Application State\" (HATEOAS).
This means that each endpoint of this API will have links to other resources or actions defined in the resulting body.

These related resources and actions for any given resource will be context sensitive. For example, only actions that the
authenticated user can take are being rendered. This can be used to dynamically identify actions that the user might take for any
given response.

As an example, if you fetch a work package through the [Work Package endpoint](https://www.openproject.org/docs/api/endpoints/work-packages/), the `update` link will only
be present when the user you authenticated has been granted a permission to update the work package in the assigned project.

## HAL+JSON

HAL is a simple format that gives a consistent and easy way to hyperlink between resources in your API.
Read more in the following specification: [https://tools.ietf.org/html/draft-kelly-json-hal-08](https://tools.ietf.org/html/draft-kelly-json-hal-08)

**OpenProject API implementation of HAL+JSON format** enriches JSON and introduces a few meta properties:

- `_type` - specifies the type of the resource (e.g.: WorkPackage, Project)
- `_links` - contains all related resource and action links available for the resource
- `_embedded` - contains all embedded objects

HAL does not guarantee that embedded resources are embedded in their full representation, they might as well be
partially represented (e.g. some properties can be left out).
However in this API you have the guarantee that whenever a resource is **embedded**, it is embedded in its **full representation**.

## API response structure

All API responses contain a single HAL+JSON object, even collections of objects are technically represented by
a single HAL+JSON object that itself contains its members. More details on collections can be found
in the [Collections Section](https://www.openproject.org/docs/api/collections/).

## Authentication

The API supports the following authentication schemes:

* Session-based authentication
* API tokens
    * passed as Bearer token
    * passed via Basic auth
* OAuth 2.0
    * using built-in authorization server
    * using an external authorization server (RFC 9068)

Depending on the settings of the OpenProject instance many resources can be accessed without being authenticated.
In case the instance requires authentication on all requests the client will receive an **HTTP 401** status code
in response to any request.

Otherwise unauthenticated clients have all the permissions of the anonymous user.

### Session-based authentication

This means you have to login to OpenProject via the Web-Interface to be authenticated in the API.
This method is well-suited for clients acting within the browser, like the Angular-Client built into OpenProject.

In this case, you always need to pass the HTTP header `X-Requested-With \"XMLHttpRequest\"` for authentication.

### API token as bearer token

Users can authenticate towards the API v3 using an API token as a bearer token.

For example:

```shell
API_KEY=opapi-2519132cdf62dcf5a66fd96394672079f9e9cad1
curl -H \"Authorization: Bearer $API_KEY\" https://community.openproject.org/api/v3/users/42
```

Users can generate API tokens on their account page.

### API token through Basic Auth

API tokens can also be used with basic auth, using the user name `apikey` (NOT your login) and the API token as the password.

For example:

```shell
API_KEY=opapi-2519132cdf62dcf5a66fd96394672079f9e9cad1
curl -u apikey:$API_KEY https://community.openproject.org/api/v3/users/42
```

### OAuth 2.0 authentication

OpenProject allows authentication and authorization with OAuth2 with *Authorization code flow*, as well as *Client credentials* operation modes.

To get started, you first need to register an application in the OpenProject OAuth administration section of your installation.
This will save an entry for your application with a client unique identifier (`client_id`) and an accompanying secret key (`client_secret`).

You can then use one the following guides to perform the supported OAuth 2.0 flows:

- [Authorization code flow](https://oauth.net/2/grant-types/authorization-code)

- [Authorization code flow with PKCE](https://doorkeeper.gitbook.io/guides/ruby-on-rails/pkce-flow), recommended for clients unable to keep the client_secret confidential

- [Client credentials](https://oauth.net/2/grant-types/client-credentials/) - Requires an application to be bound to an impersonating user for non-public access

### OAuth 2.0 using an external authorization server

There is a possibility to use JSON Web Tokens (JWT) generated by an OIDC provider configured in OpenProject as a bearer token to do authenticated requests against the API.
The following requirements must be met:

- OIDC provider must be configured in OpenProject with **jwks_uri**
- JWT must be signed using RSA algorithm
- JWT **iss** claim must be equal to OIDC provider **issuer**
- JWT **aud** claim must contain the OpenProject **client ID** used at the OIDC provider
- JWT **scope** claim must include a valid scope to access the desired API (e.g. `api_v3` for APIv3)
- JWT must be actual (neither expired or too early to be used)
- JWT must be passed in Authorization header like: `Authorization: Bearer {jwt}`
- User from **sub** claim must be linked to OpenProject before (e.g. by logging in), otherwise it will be not authenticated

In more general terms, OpenProject should be compliant to [RFC 9068](https://www.rfc-editor.org/rfc/rfc9068) when validating access tokens.

### Why not username and password?

The simplest way to do basic auth would be to use a user's username and password naturally.
However, OpenProject already has supported API keys in the past for the API v2, though not through basic auth.

Using **username and password** directly would have some advantages:

* It is intuitive for the user who then just has to provide those just as they would when logging into OpenProject.

* No extra logic for token management necessary.

On the other hand using **API keys** has some advantages too, which is why we went for that:

* If compromised while saved on an insecure client the user only has to regenerate the API key instead of changing their password, too.

* They are naturally long and random which makes them invulnerable to dictionary attacks and harder to crack in general.

Most importantly users may not actually have a password to begin with. Specifically when they have registered
through an OpenID Connect provider.

## Cross-Origin Resource Sharing (CORS)

By default, the OpenProject API is _not_ responding with any CORS headers.
If you want to allow cross-domain AJAX calls against your OpenProject instance, you need to enable CORS headers being returned.

Please see [our API settings documentation](https://www.openproject.org/docs/system-admin-guide/api-and-webhooks/) on
how to selectively enable CORS.

## Allowed HTTP methods

- `GET` - Get a single resource or collection of resources

- `POST` - Create a new resource or perform

- `PATCH` - Update a resource

- `DELETE` - Delete a resource

## Compression

Responses are compressed if requested by the client. Currently [gzip](https://www.gzip.org/) and [deflate](https://tools.ietf.org/html/rfc1951)
are supported. The client signals the desired compression by setting the [`Accept-Encoding` header](https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.3).
If no `Accept-Encoding` header is send, `Accept-Encoding: identity` is assumed which will result in the API responding uncompressed.

This Python package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: 3
- Package version: 1.0.0
- Generator version: 7.20.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

## Requirements.

Python 3.9+

## Installation & Usage
### pip install

If the python package is hosted on a repository, you can install directly using:

```sh
pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git`)

Then import the package:
```python
import openproject_client
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import openproject_client
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import openproject_client
from openproject_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = openproject_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = openproject_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)


# Enter a context with an instance of the API client
with openproject_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openproject_client.ActionsCapabilitiesApi(api_client)
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
*ActionsCapabilitiesApi* | [**list_actions**](docs/ActionsCapabilitiesApi.md#list_actions) | **GET** /api/v3/actions | List actions
*ActionsCapabilitiesApi* | [**list_capabilities**](docs/ActionsCapabilitiesApi.md#list_capabilities) | **GET** /api/v3/capabilities | List capabilities
*ActionsCapabilitiesApi* | [**view_action**](docs/ActionsCapabilitiesApi.md#view_action) | **GET** /api/v3/actions/{id} | View action
*ActionsCapabilitiesApi* | [**view_capabilities**](docs/ActionsCapabilitiesApi.md#view_capabilities) | **GET** /api/v3/capabilities/{id} | View capabilities
*ActionsCapabilitiesApi* | [**view_global_context**](docs/ActionsCapabilitiesApi.md#view_global_context) | **GET** /api/v3/capabilities/context/global | View global context
*ActivitiesApi* | [**create_activity_attachment**](docs/ActivitiesApi.md#create_activity_attachment) | **POST** /api/v3/activities/{id}/attachments | Add attachment to activity
*ActivitiesApi* | [**get_activity**](docs/ActivitiesApi.md#get_activity) | **GET** /api/v3/activities/{id} | Get an activity
*ActivitiesApi* | [**list_activity_attachments**](docs/ActivitiesApi.md#list_activity_attachments) | **GET** /api/v3/activities/{id}/attachments | List attachments by activity
*ActivitiesApi* | [**list_activity_emoji_reactions**](docs/ActivitiesApi.md#list_activity_emoji_reactions) | **GET** /api/v3/activities/{id}/emoji_reactions | List emoji reactions by activity
*ActivitiesApi* | [**list_work_package_activities_emoji_reactions**](docs/ActivitiesApi.md#list_work_package_activities_emoji_reactions) | **GET** /api/v3/work_packages/{id}/activities_emoji_reactions | List emoji reactions by work package activities
*ActivitiesApi* | [**toggle_activity_emoji_reaction**](docs/ActivitiesApi.md#toggle_activity_emoji_reaction) | **PATCH** /api/v3/activities/{id}/emoji_reactions | Toggle emoji reaction for an activity
*ActivitiesApi* | [**update_activity**](docs/ActivitiesApi.md#update_activity) | **PATCH** /api/v3/activities/{id} | Update activity
*AttachmentsApi* | [**add_attachment_to_meeting**](docs/AttachmentsApi.md#add_attachment_to_meeting) | **POST** /api/v3/meetings/{id}/attachments | Add attachment to meeting
*AttachmentsApi* | [**add_attachment_to_post**](docs/AttachmentsApi.md#add_attachment_to_post) | **POST** /api/v3/posts/{id}/attachments | Add attachment to post
*AttachmentsApi* | [**add_attachment_to_wiki_page**](docs/AttachmentsApi.md#add_attachment_to_wiki_page) | **POST** /api/v3/wiki_pages/{id}/attachments | Add attachment to wiki page
*AttachmentsApi* | [**create_activity_attachment**](docs/AttachmentsApi.md#create_activity_attachment) | **POST** /api/v3/activities/{id}/attachments | Add attachment to activity
*AttachmentsApi* | [**create_attachment**](docs/AttachmentsApi.md#create_attachment) | **POST** /api/v3/attachments | Create Attachment
*AttachmentsApi* | [**create_work_package_attachment**](docs/AttachmentsApi.md#create_work_package_attachment) | **POST** /api/v3/work_packages/{id}/attachments | Create work package attachment
*AttachmentsApi* | [**delete_attachment**](docs/AttachmentsApi.md#delete_attachment) | **DELETE** /api/v3/attachments/{id} | Delete attachment
*AttachmentsApi* | [**list_activity_attachments**](docs/AttachmentsApi.md#list_activity_attachments) | **GET** /api/v3/activities/{id}/attachments | List attachments by activity
*AttachmentsApi* | [**list_attachments_by_meeting**](docs/AttachmentsApi.md#list_attachments_by_meeting) | **GET** /api/v3/meetings/{id}/attachments | List attachments by meeting
*AttachmentsApi* | [**list_attachments_by_post**](docs/AttachmentsApi.md#list_attachments_by_post) | **GET** /api/v3/posts/{id}/attachments | List attachments by post
*AttachmentsApi* | [**list_attachments_by_wiki_page**](docs/AttachmentsApi.md#list_attachments_by_wiki_page) | **GET** /api/v3/wiki_pages/{id}/attachments | List attachments by wiki page
*AttachmentsApi* | [**list_work_package_attachments**](docs/AttachmentsApi.md#list_work_package_attachments) | **GET** /api/v3/work_packages/{id}/attachments | List attachments by work package
*AttachmentsApi* | [**view_attachment**](docs/AttachmentsApi.md#view_attachment) | **GET** /api/v3/attachments/{id} | View attachment
*BudgetsApi* | [**view_budget**](docs/BudgetsApi.md#view_budget) | **GET** /api/v3/budgets/{id} | view Budget
*BudgetsApi* | [**view_budgets_of_a_project**](docs/BudgetsApi.md#view_budgets_of_a_project) | **GET** /api/v3/projects/{id}/budgets | view Budgets of a Project
*CategoriesApi* | [**list_categories_of_a_project**](docs/CategoriesApi.md#list_categories_of_a_project) | **GET** /api/v3/projects/{id}/categories | List categories of a project
*CategoriesApi* | [**list_categories_of_a_workspace**](docs/CategoriesApi.md#list_categories_of_a_workspace) | **GET** /api/v3/workspaces/{id}/categories | List categories of a workspace
*CategoriesApi* | [**view_category**](docs/CategoriesApi.md#view_category) | **GET** /api/v3/categories/{id} | View Category
*CollectionsApi* | [**view_aggregated_result**](docs/CollectionsApi.md#view_aggregated_result) | **GET** /api/v3/examples | view aggregated result
*ConfigurationApi* | [**view_configuration**](docs/ConfigurationApi.md#view_configuration) | **GET** /api/v3/configuration | View configuration
*ConfigurationApi* | [**view_project_configuration**](docs/ConfigurationApi.md#view_project_configuration) | **GET** /api/v3/projects/{id}/configuration | View project configuration
*CustomOptionsApi* | [**view_custom_option**](docs/CustomOptionsApi.md#view_custom_option) | **GET** /api/v3/custom_options/{id} | View Custom Option
*CustomActionsApi* | [**execute_custom_action**](docs/CustomActionsApi.md#execute_custom_action) | **POST** /api/v3/custom_actions/{id}/execute | Execute custom action
*CustomActionsApi* | [**get_custom_action**](docs/CustomActionsApi.md#get_custom_action) | **GET** /api/v3/custom_actions/{id} | Get a custom action
*DocumentsApi* | [**list_documents**](docs/DocumentsApi.md#list_documents) | **GET** /api/v3/documents | List Documents
*DocumentsApi* | [**update_document**](docs/DocumentsApi.md#update_document) | **PATCH** /api/v3/documents/{id} | Update document
*DocumentsApi* | [**view_document**](docs/DocumentsApi.md#view_document) | **GET** /api/v3/documents/{id} | View document
*EmojiReactionsApi* | [**list_activity_emoji_reactions**](docs/EmojiReactionsApi.md#list_activity_emoji_reactions) | **GET** /api/v3/activities/{id}/emoji_reactions | List emoji reactions by activity
*EmojiReactionsApi* | [**list_work_package_activities_emoji_reactions**](docs/EmojiReactionsApi.md#list_work_package_activities_emoji_reactions) | **GET** /api/v3/work_packages/{id}/activities_emoji_reactions | List emoji reactions by work package activities
*EmojiReactionsApi* | [**toggle_activity_emoji_reaction**](docs/EmojiReactionsApi.md#toggle_activity_emoji_reaction) | **PATCH** /api/v3/activities/{id}/emoji_reactions | Toggle emoji reaction for an activity
*FavoritesApi* | [**favorite_project**](docs/FavoritesApi.md#favorite_project) | **POST** /api/v3/projects/{id}/favorite | Favorite Project
*FavoritesApi* | [**favorite_workspace**](docs/FavoritesApi.md#favorite_workspace) | **POST** /api/v3/workspaces/{id}/favorite | Favorite Workspace
*FavoritesApi* | [**unfavorite_project**](docs/FavoritesApi.md#unfavorite_project) | **DELETE** /api/v3/projects/{id}/favorite | Unfavorite Project
*FavoritesApi* | [**unfavorite_workspace**](docs/FavoritesApi.md#unfavorite_workspace) | **DELETE** /api/v3/workspaces/{id}/favorite | Unfavorite Workspace
*FileLinksApi* | [**get_project_storage**](docs/FileLinksApi.md#get_project_storage) | **GET** /api/v3/project_storages/{id} | Gets a project storage
*FileLinksApi* | [**list_project_storages**](docs/FileLinksApi.md#list_project_storages) | **GET** /api/v3/project_storages | Gets a list of project storages
*FileLinksApi* | [**open_project_storage**](docs/FileLinksApi.md#open_project_storage) | **GET** /api/v3/project_storages/{id}/open | Open the project storage
*FileLinksApi* | [**open_storage**](docs/FileLinksApi.md#open_storage) | **GET** /api/v3/storages/{id}/open | Open the storage
*FileLinksApi* | [**create_storage**](docs/FileLinksApi.md#create_storage) | **POST** /api/v3/storages | Creates a storage.
*FileLinksApi* | [**create_storage_folder**](docs/FileLinksApi.md#create_storage_folder) | **POST** /api/v3/storages/{id}/folders | Creation of a new folder
*FileLinksApi* | [**create_storage_oauth_credentials**](docs/FileLinksApi.md#create_storage_oauth_credentials) | **POST** /api/v3/storages/{id}/oauth_client_credentials | Creates an oauth client credentials object for a storage.
*FileLinksApi* | [**create_work_package_file_link**](docs/FileLinksApi.md#create_work_package_file_link) | **POST** /api/v3/work_packages/{id}/file_links | Creates file links.
*FileLinksApi* | [**delete_file_link**](docs/FileLinksApi.md#delete_file_link) | **DELETE** /api/v3/file_links/{id} | Removes a file link.
*FileLinksApi* | [**delete_storage**](docs/FileLinksApi.md#delete_storage) | **DELETE** /api/v3/storages/{id} | Delete a storage
*FileLinksApi* | [**download_file_link**](docs/FileLinksApi.md#download_file_link) | **GET** /api/v3/file_links/{id}/download | Creates a download uri of the linked file.
*FileLinksApi* | [**get_storage**](docs/FileLinksApi.md#get_storage) | **GET** /api/v3/storages/{id} | Get a storage
*FileLinksApi* | [**get_storage_files**](docs/FileLinksApi.md#get_storage_files) | **GET** /api/v3/storages/{id}/files | Gets files of a storage.
*FileLinksApi* | [**list_storages**](docs/FileLinksApi.md#list_storages) | **GET** /api/v3/storages | Get Storages
*FileLinksApi* | [**list_work_package_file_links**](docs/FileLinksApi.md#list_work_package_file_links) | **GET** /api/v3/work_packages/{id}/file_links | Gets all file links of a work package
*FileLinksApi* | [**open_file_link**](docs/FileLinksApi.md#open_file_link) | **GET** /api/v3/file_links/{id}/open | Creates an opening uri of the linked file.
*FileLinksApi* | [**prepare_storage_file_upload**](docs/FileLinksApi.md#prepare_storage_file_upload) | **POST** /api/v3/storages/{id}/files/prepare_upload | Preparation of a direct upload of a file to the given storage.
*FileLinksApi* | [**update_storage**](docs/FileLinksApi.md#update_storage) | **PATCH** /api/v3/storages/{id} | Update a storage
*FileLinksApi* | [**view_file_link**](docs/FileLinksApi.md#view_file_link) | **GET** /api/v3/file_links/{id} | Gets a file link.
*FormsApi* | [**show_or_validate_form**](docs/FormsApi.md#show_or_validate_form) | **POST** /api/v3/example/form | show or validate form
*GridsApi* | [**create_grid**](docs/GridsApi.md#create_grid) | **POST** /api/v3/grids | Create a grid
*GridsApi* | [**get_grid**](docs/GridsApi.md#get_grid) | **GET** /api/v3/grids/{id} | Get a grid
*GridsApi* | [**grid_create_form**](docs/GridsApi.md#grid_create_form) | **POST** /api/v3/grids/form | Grid Create Form
*GridsApi* | [**grid_update_form**](docs/GridsApi.md#grid_update_form) | **POST** /api/v3/grids/{id}/form | Grid Update Form
*GridsApi* | [**list_grids**](docs/GridsApi.md#list_grids) | **GET** /api/v3/grids | List grids
*GridsApi* | [**update_grid**](docs/GridsApi.md#update_grid) | **PATCH** /api/v3/grids/{id} | Update a grid
*GroupsApi* | [**create_group**](docs/GroupsApi.md#create_group) | **POST** /api/v3/groups | Create group
*GroupsApi* | [**delete_group**](docs/GroupsApi.md#delete_group) | **DELETE** /api/v3/groups/{id} | Delete group
*GroupsApi* | [**get_group**](docs/GroupsApi.md#get_group) | **GET** /api/v3/groups/{id} | Get group
*GroupsApi* | [**list_groups**](docs/GroupsApi.md#list_groups) | **GET** /api/v3/groups | List groups
*GroupsApi* | [**update_group**](docs/GroupsApi.md#update_group) | **PATCH** /api/v3/groups/{id} | Update group
*HelpTextsApi* | [**get_help_text**](docs/HelpTextsApi.md#get_help_text) | **GET** /api/v3/help_texts/{id} | Get help text
*HelpTextsApi* | [**list_help_texts**](docs/HelpTextsApi.md#list_help_texts) | **GET** /api/v3/help_texts | List help texts
*MeetingsApi* | [**view_meeting**](docs/MeetingsApi.md#view_meeting) | **GET** /api/v3/meetings/{id} | View Meeting Page
*MembershipsApi* | [**create_membership**](docs/MembershipsApi.md#create_membership) | **POST** /api/v3/memberships | Create a membership
*MembershipsApi* | [**delete_membership**](docs/MembershipsApi.md#delete_membership) | **DELETE** /api/v3/memberships/{id} | Delete membership
*MembershipsApi* | [**form_create_membership**](docs/MembershipsApi.md#form_create_membership) | **POST** /api/v3/memberships/form | Form create membership
*MembershipsApi* | [**form_update_membership**](docs/MembershipsApi.md#form_update_membership) | **POST** /api/v3/memberships/{id}/form | Form update membership
*MembershipsApi* | [**get_membership**](docs/MembershipsApi.md#get_membership) | **GET** /api/v3/memberships/{id} | Get a membership
*MembershipsApi* | [**get_membership_schema**](docs/MembershipsApi.md#get_membership_schema) | **GET** /api/v3/memberships/schema | Schema membership
*MembershipsApi* | [**get_memberships_available_projects**](docs/MembershipsApi.md#get_memberships_available_projects) | **GET** /api/v3/memberships/available_projects | Available projects for memberships
*MembershipsApi* | [**list_memberships**](docs/MembershipsApi.md#list_memberships) | **GET** /api/v3/memberships | List memberships
*MembershipsApi* | [**update_membership**](docs/MembershipsApi.md#update_membership) | **PATCH** /api/v3/memberships/{id} | Update membership
*NewsApi* | [**create_news**](docs/NewsApi.md#create_news) | **POST** /api/v3/news | Create News
*NewsApi* | [**delete_news**](docs/NewsApi.md#delete_news) | **DELETE** /api/v3/news/{id} | Delete news
*NewsApi* | [**list_news**](docs/NewsApi.md#list_news) | **GET** /api/v3/news | List News
*NewsApi* | [**update_news**](docs/NewsApi.md#update_news) | **PATCH** /api/v3/news/{id} | Update news
*NewsApi* | [**view_news**](docs/NewsApi.md#view_news) | **GET** /api/v3/news/{id} | View news
*NotificationsApi* | [**list_notifications**](docs/NotificationsApi.md#list_notifications) | **GET** /api/v3/notifications | Get notification collection
*NotificationsApi* | [**read_notification**](docs/NotificationsApi.md#read_notification) | **POST** /api/v3/notifications/{id}/read_ian | Read notification
*NotificationsApi* | [**read_notifications**](docs/NotificationsApi.md#read_notifications) | **POST** /api/v3/notifications/read_ian | Read all notifications
*NotificationsApi* | [**unread_notification**](docs/NotificationsApi.md#unread_notification) | **POST** /api/v3/notifications/{id}/unread_ian | Unread notification
*NotificationsApi* | [**unread_notifications**](docs/NotificationsApi.md#unread_notifications) | **POST** /api/v3/notifications/unread_ian | Unread all notifications
*NotificationsApi* | [**view_notification**](docs/NotificationsApi.md#view_notification) | **GET** /api/v3/notifications/{id} | Get the notification
*NotificationsApi* | [**view_notification_detail**](docs/NotificationsApi.md#view_notification_detail) | **GET** /api/v3/notifications/{notification_id}/details/{id} | Get a notification detail
*OAuth2Api* | [**get_oauth_application**](docs/OAuth2Api.md#get_oauth_application) | **GET** /api/v3/oauth_applications/{id} | Get the oauth application.
*OAuth2Api* | [**get_oauth_client_credentials**](docs/OAuth2Api.md#get_oauth_client_credentials) | **GET** /api/v3/oauth_client_credentials/{id} | Get the oauth client credentials object.
*PortfoliosApi* | [**delete_portfolio**](docs/PortfoliosApi.md#delete_portfolio) | **DELETE** /api/v3/portfolios/{id} | Delete Portfolio
*PortfoliosApi* | [**list_portfolios**](docs/PortfoliosApi.md#list_portfolios) | **GET** /api/v3/portfolios | List portfolios
*PortfoliosApi* | [**portfolio_update_form**](docs/PortfoliosApi.md#portfolio_update_form) | **POST** /api/v3/portfolios/{id}/form | Portfolio update form
*PortfoliosApi* | [**update_portfolio**](docs/PortfoliosApi.md#update_portfolio) | **PATCH** /api/v3/portfolios/{id} | Update Portfolio
*PortfoliosApi* | [**view_portfolio**](docs/PortfoliosApi.md#view_portfolio) | **GET** /api/v3/portfolios/{id} | View portfolio
*PostsApi* | [**view_post**](docs/PostsApi.md#view_post) | **GET** /api/v3/posts/{id} | View Post
*PreviewingApi* | [**preview_markdown_document**](docs/PreviewingApi.md#preview_markdown_document) | **POST** /api/v3/render/markdown | Preview Markdown document
*PreviewingApi* | [**preview_plain_document**](docs/PreviewingApi.md#preview_plain_document) | **POST** /api/v3/render/plain | Preview plain document
*PrincipalsApi* | [**create_placeholder_user**](docs/PrincipalsApi.md#create_placeholder_user) | **POST** /api/v3/placeholder_users | Create placeholder user
*PrincipalsApi* | [**create_user**](docs/PrincipalsApi.md#create_user) | **POST** /api/v3/users | Create User
*PrincipalsApi* | [**delete_placeholder_user**](docs/PrincipalsApi.md#delete_placeholder_user) | **DELETE** /api/v3/placeholder_users/{id} | Delete placeholder user
*PrincipalsApi* | [**delete_user**](docs/PrincipalsApi.md#delete_user) | **DELETE** /api/v3/users/{id} | Delete user
*PrincipalsApi* | [**list_placeholder_users**](docs/PrincipalsApi.md#list_placeholder_users) | **GET** /api/v3/placeholder_users | List placehoder users
*PrincipalsApi* | [**list_principals**](docs/PrincipalsApi.md#list_principals) | **GET** /api/v3/principals | List principals
*PrincipalsApi* | [**list_users**](docs/PrincipalsApi.md#list_users) | **GET** /api/v3/users | List Users
*PrincipalsApi* | [**update_placeholder_user**](docs/PrincipalsApi.md#update_placeholder_user) | **PATCH** /api/v3/placeholder_users/{id} | Update placeholder user
*PrincipalsApi* | [**update_user**](docs/PrincipalsApi.md#update_user) | **PATCH** /api/v3/users/{id} | Update user
*PrincipalsApi* | [**view_placeholder_user**](docs/PrincipalsApi.md#view_placeholder_user) | **GET** /api/v3/placeholder_users/{id} | View placeholder user
*PrincipalsApi* | [**view_user**](docs/PrincipalsApi.md#view_user) | **GET** /api/v3/users/{id} | View user
*PrioritiesApi* | [**list_all_priorities**](docs/PrioritiesApi.md#list_all_priorities) | **GET** /api/v3/priorities | List all Priorities
*PrioritiesApi* | [**view_priority**](docs/PrioritiesApi.md#view_priority) | **GET** /api/v3/priorities/{id} | View Priority
*ProgramsApi* | [**delete_program**](docs/ProgramsApi.md#delete_program) | **DELETE** /api/v3/programs/{id} | Delete Program
*ProgramsApi* | [**list_programs**](docs/ProgramsApi.md#list_programs) | **GET** /api/v3/programs | List programs
*ProgramsApi* | [**program_update_form**](docs/ProgramsApi.md#program_update_form) | **POST** /api/v3/programs/{id}/form | Program update form
*ProgramsApi* | [**update_program**](docs/ProgramsApi.md#update_program) | **PATCH** /api/v3/programs/{id} | Update Program
*ProgramsApi* | [**view_program**](docs/ProgramsApi.md#view_program) | **GET** /api/v3/programs/{id} | View program
*ProjectPhaseDefinitionsApi* | [**get_project_phase_definition**](docs/ProjectPhaseDefinitionsApi.md#get_project_phase_definition) | **GET** /api/v3/project_phase_definitions/{id} | Get a project phase definition
*ProjectPhaseDefinitionsApi* | [**list_project_phase_definitions**](docs/ProjectPhaseDefinitionsApi.md#list_project_phase_definitions) | **GET** /api/v3/project_phase_definitions | List project phase definitions
*ProjectPhasesApi* | [**get_project_phase**](docs/ProjectPhasesApi.md#get_project_phase) | **GET** /api/v3/project_phases/{id} | Get a project phase
*ProjectsApi* | [**create_project**](docs/ProjectsApi.md#create_project) | **POST** /api/v3/projects | Create project
*ProjectsApi* | [**create_project_copy**](docs/ProjectsApi.md#create_project_copy) | **POST** /api/v3/projects/{id}/copy | Create project copy
*ProjectsApi* | [**delete_project**](docs/ProjectsApi.md#delete_project) | **DELETE** /api/v3/projects/{id} | Delete Project
*ProjectsApi* | [**favorite_project**](docs/ProjectsApi.md#favorite_project) | **POST** /api/v3/projects/{id}/favorite | Favorite Project
*ProjectsApi* | [**list_available_parent_project_candidates**](docs/ProjectsApi.md#list_available_parent_project_candidates) | **GET** /api/v3/projects/available_parent_projects | List available parent project candidates
*ProjectsApi* | [**list_projects**](docs/ProjectsApi.md#list_projects) | **GET** /api/v3/projects | List projects
*ProjectsApi* | [**list_projects_with_version**](docs/ProjectsApi.md#list_projects_with_version) | **GET** /api/v3/versions/{id}/projects | List projects having version
*ProjectsApi* | [**list_workspaces_with_version**](docs/ProjectsApi.md#list_workspaces_with_version) | **GET** /api/v3/versions/{id}/workspaces | List workspaces having version
*ProjectsApi* | [**project_copy_form**](docs/ProjectsApi.md#project_copy_form) | **POST** /api/v3/projects/{id}/copy/form | Project copy form
*ProjectsApi* | [**project_create_form**](docs/ProjectsApi.md#project_create_form) | **POST** /api/v3/projects/form | Project create form
*ProjectsApi* | [**project_update_form**](docs/ProjectsApi.md#project_update_form) | **POST** /api/v3/projects/{id}/form | Project update form
*ProjectsApi* | [**unfavorite_project**](docs/ProjectsApi.md#unfavorite_project) | **DELETE** /api/v3/projects/{id}/favorite | Unfavorite Project
*ProjectsApi* | [**update_project**](docs/ProjectsApi.md#update_project) | **PATCH** /api/v3/projects/{id} | Update Project
*ProjectsApi* | [**view_project**](docs/ProjectsApi.md#view_project) | **GET** /api/v3/projects/{id} | View project
*ProjectsApi* | [**view_project_configuration**](docs/ProjectsApi.md#view_project_configuration) | **GET** /api/v3/projects/{id}/configuration | View project configuration
*ProjectsApi* | [**view_project_schema**](docs/ProjectsApi.md#view_project_schema) | **GET** /api/v3/projects/schema | View project schema
*ProjectsApi* | [**view_project_status**](docs/ProjectsApi.md#view_project_status) | **GET** /api/v3/project_statuses/{id} | View project status
*QueriesApi* | [**available_projects_for_query**](docs/QueriesApi.md#available_projects_for_query) | **GET** /api/v3/queries/available_projects | Available projects for query
*QueriesApi* | [**create_query**](docs/QueriesApi.md#create_query) | **POST** /api/v3/queries | Create query
*QueriesApi* | [**delete_query**](docs/QueriesApi.md#delete_query) | **DELETE** /api/v3/queries/{id} | Delete query
*QueriesApi* | [**edit_query**](docs/QueriesApi.md#edit_query) | **PATCH** /api/v3/queries/{id} | Edit Query
*QueriesApi* | [**list_queries**](docs/QueriesApi.md#list_queries) | **GET** /api/v3/queries | List queries
*QueriesApi* | [**query_create_form**](docs/QueriesApi.md#query_create_form) | **POST** /api/v3/queries/form | Query Create Form
*QueriesApi* | [**query_update_form**](docs/QueriesApi.md#query_update_form) | **POST** /api/v3/queries/{id}/form | Query Update Form
*QueriesApi* | [**star_query**](docs/QueriesApi.md#star_query) | **PATCH** /api/v3/queries/{id}/star | Star query
*QueriesApi* | [**unstar_query**](docs/QueriesApi.md#unstar_query) | **PATCH** /api/v3/queries/{id}/unstar | Unstar query
*QueriesApi* | [**view_default_query**](docs/QueriesApi.md#view_default_query) | **GET** /api/v3/queries/default | View default query
*QueriesApi* | [**view_default_query_for_project**](docs/QueriesApi.md#view_default_query_for_project) | **GET** /api/v3/projects/{id}/queries/default | View default query for project
*QueriesApi* | [**view_default_query_for_workspace**](docs/QueriesApi.md#view_default_query_for_workspace) | **GET** /api/v3/workspaces/{id}/queries/default | View default query for workspace
*QueriesApi* | [**view_query**](docs/QueriesApi.md#view_query) | **GET** /api/v3/queries/{id} | View query
*QueriesApi* | [**view_schema_for_global_queries**](docs/QueriesApi.md#view_schema_for_global_queries) | **GET** /api/v3/queries/schema | View schema for global queries
*QueriesApi* | [**view_schema_for_project_queries**](docs/QueriesApi.md#view_schema_for_project_queries) | **GET** /api/v3/projects/{id}/queries/schema | View schema for project queries
*QueriesApi* | [**view_schema_for_workspace_queries**](docs/QueriesApi.md#view_schema_for_workspace_queries) | **GET** /api/v3/workspace/{id}/queries/schema | View schema for workspace queries
*QueryColumnsApi* | [**view_query_column**](docs/QueryColumnsApi.md#view_query_column) | **GET** /api/v3/queries/columns/{id} | View Query Column
*QueryFilterInstanceSchemaApi* | [**list_query_filter_instance_schemas**](docs/QueryFilterInstanceSchemaApi.md#list_query_filter_instance_schemas) | **GET** /api/v3/queries/filter_instance_schemas | List Query Filter Instance Schemas
*QueryFilterInstanceSchemaApi* | [**list_query_filter_instance_schemas_for_project**](docs/QueryFilterInstanceSchemaApi.md#list_query_filter_instance_schemas_for_project) | **GET** /api/v3/projects/{id}/queries/filter_instance_schemas | List Query Filter Instance Schemas for Project
*QueryFilterInstanceSchemaApi* | [**list_query_filter_instance_schemas_for_workspace**](docs/QueryFilterInstanceSchemaApi.md#list_query_filter_instance_schemas_for_workspace) | **GET** /api/v3/workspace/{id}/queries/filter_instance_schemas | List Query Filter Instance Schemas for Workspace
*QueryFilterInstanceSchemaApi* | [**view_query_filter_instance_schema**](docs/QueryFilterInstanceSchemaApi.md#view_query_filter_instance_schema) | **GET** /api/v3/queries/filter_instance_schemas/{id} | View Query Filter Instance Schema
*QueryFiltersApi* | [**view_query_filter**](docs/QueryFiltersApi.md#view_query_filter) | **GET** /api/v3/queries/filters/{id} | View Query Filter
*QueryOperatorsApi* | [**view_query_operator**](docs/QueryOperatorsApi.md#view_query_operator) | **GET** /api/v3/queries/operators/{id} | View Query Operator
*QuerySortBysApi* | [**view_query_sort_by**](docs/QuerySortBysApi.md#view_query_sort_by) | **GET** /api/v3/queries/sort_bys/{id} | View Query Sort By
*RelationsApi* | [**create_relation**](docs/RelationsApi.md#create_relation) | **POST** /api/v3/work_packages/{id}/relations | Create relation
*RelationsApi* | [**delete_relation**](docs/RelationsApi.md#delete_relation) | **DELETE** /api/v3/relations/{id} | Delete Relation
*RelationsApi* | [**get_relation**](docs/RelationsApi.md#get_relation) | **GET** /api/v3/relations/{id} | Get Relation
*RelationsApi* | [**list_relations**](docs/RelationsApi.md#list_relations) | **GET** /api/v3/relations | List Relations
*RelationsApi* | [**update_relation**](docs/RelationsApi.md#update_relation) | **PATCH** /api/v3/relations/{id} | Update Relation
*RemindersApi* | [**create_work_package_reminder**](docs/RemindersApi.md#create_work_package_reminder) | **POST** /api/v3/work_packages/{work_package_id}/reminders | Create a work package reminder
*RemindersApi* | [**delete_reminder**](docs/RemindersApi.md#delete_reminder) | **DELETE** /api/v3/reminders/{id} | Delete a reminder
*RemindersApi* | [**list_reminders**](docs/RemindersApi.md#list_reminders) | **GET** /api/v3/reminders | List all active reminders
*RemindersApi* | [**list_work_package_reminders**](docs/RemindersApi.md#list_work_package_reminders) | **GET** /api/v3/work_packages/{work_package_id}/reminders | List work package reminders
*RemindersApi* | [**update_reminder**](docs/RemindersApi.md#update_reminder) | **PATCH** /api/v3/reminders/{id} | Update a reminder
*RevisionsApi* | [**view_revision**](docs/RevisionsApi.md#view_revision) | **GET** /api/v3/revisions/{id} | View revision
*RolesApi* | [**list_roles**](docs/RolesApi.md#list_roles) | **GET** /api/v3/roles | List roles
*RolesApi* | [**view_role**](docs/RolesApi.md#view_role) | **GET** /api/v3/roles/{id} | View role
*RootApi* | [**view_root**](docs/RootApi.md#view_root) | **GET** /api/v3 | View root
*SchemasApi* | [**view_the_schema**](docs/SchemasApi.md#view_the_schema) | **GET** /api/v3/example/schema | view the schema
*StatusesApi* | [**get_status**](docs/StatusesApi.md#get_status) | **GET** /api/v3/statuses/{id} | Get a work package status
*StatusesApi* | [**list_statuses**](docs/StatusesApi.md#list_statuses) | **GET** /api/v3/statuses | List the collection of all statuses
*TimeEntriesApi* | [**available_projects_for_time_entries**](docs/TimeEntriesApi.md#available_projects_for_time_entries) | **GET** /api/v3/time_entries/available_projects | Available projects for time entries
*TimeEntriesApi* | [**time_entry_create_form**](docs/TimeEntriesApi.md#time_entry_create_form) | **POST** /api/v3/time_entries/form | Time entry create form
*TimeEntriesApi* | [**time_entry_update_form**](docs/TimeEntriesApi.md#time_entry_update_form) | **POST** /api/v3/time_entries/{id}/form | Time entry update form
*TimeEntriesApi* | [**update_time_entry**](docs/TimeEntriesApi.md#update_time_entry) | **PATCH** /api/v3/time_entries/{id} | update time entry
*TimeEntriesApi* | [**view_time_entry_schema**](docs/TimeEntriesApi.md#view_time_entry_schema) | **GET** /api/v3/time_entries/schema | View time entry schema
*TimeEntriesApi* | [**create_time_entry**](docs/TimeEntriesApi.md#create_time_entry) | **POST** /api/v3/time_entries | Create time entry
*TimeEntriesApi* | [**delete_time_entry**](docs/TimeEntriesApi.md#delete_time_entry) | **DELETE** /api/v3/time_entries/{id} | Delete time entry
*TimeEntriesApi* | [**get_time_entry**](docs/TimeEntriesApi.md#get_time_entry) | **GET** /api/v3/time_entries/{id} | Get time entry
*TimeEntriesApi* | [**list_time_entries**](docs/TimeEntriesApi.md#list_time_entries) | **GET** /api/v3/time_entries | List time entries
*TimeEntryActivitiesApi* | [**get_time_entries_activity**](docs/TimeEntryActivitiesApi.md#get_time_entries_activity) | **GET** /api/v3/time_entries/activity/{id} | View time entries activity
*TypesApi* | [**list_all_types**](docs/TypesApi.md#list_all_types) | **GET** /api/v3/types | List all Types
*TypesApi* | [**list_types_available_in_a_project**](docs/TypesApi.md#list_types_available_in_a_project) | **GET** /api/v3/projects/{id}/types | List types available in a project
*TypesApi* | [**list_types_available_in_a_workspace**](docs/TypesApi.md#list_types_available_in_a_workspace) | **GET** /api/v3/workspaces/{id}/types | List types available in a workspace
*TypesApi* | [**view_type**](docs/TypesApi.md#view_type) | **GET** /api/v3/types/{id} | View Type
*UserPreferencesApi* | [**show_my_preferences**](docs/UserPreferencesApi.md#show_my_preferences) | **GET** /api/v3/my_preferences | Show my preferences
*UserPreferencesApi* | [**update_user_preferences**](docs/UserPreferencesApi.md#update_user_preferences) | **PATCH** /api/v3/my_preferences | Update my preferences
*UsersApi* | [**create_user**](docs/UsersApi.md#create_user) | **POST** /api/v3/users | Create User
*UsersApi* | [**delete_user**](docs/UsersApi.md#delete_user) | **DELETE** /api/v3/users/{id} | Delete user
*UsersApi* | [**list_users**](docs/UsersApi.md#list_users) | **GET** /api/v3/users | List Users
*UsersApi* | [**lock_user**](docs/UsersApi.md#lock_user) | **POST** /api/v3/users/{id}/lock | Lock user
*UsersApi* | [**unlock_user**](docs/UsersApi.md#unlock_user) | **DELETE** /api/v3/users/{id}/lock | Unlock user
*UsersApi* | [**update_user**](docs/UsersApi.md#update_user) | **PATCH** /api/v3/users/{id} | Update user
*UsersApi* | [**user_update_form**](docs/UsersApi.md#user_update_form) | **POST** /api/v3/users/{id}/form | User update form
*UsersApi* | [**view_user**](docs/UsersApi.md#view_user) | **GET** /api/v3/users/{id} | View user
*UsersApi* | [**view_user_schema**](docs/UsersApi.md#view_user_schema) | **GET** /api/v3/users/schema | View user schema
*ValuesPropertyApi* | [**view_notification_detail**](docs/ValuesPropertyApi.md#view_notification_detail) | **GET** /api/v3/notifications/{notification_id}/details/{id} | Get a notification detail
*ValuesPropertyApi* | [**view_values_schema**](docs/ValuesPropertyApi.md#view_values_schema) | **GET** /api/v3/values/schema/{id} | View Values schema
*VersionsApi* | [**available_projects_for_versions**](docs/VersionsApi.md#available_projects_for_versions) | **GET** /api/v3/versions/available_projects | Available projects for versions
*VersionsApi* | [**create_version**](docs/VersionsApi.md#create_version) | **POST** /api/v3/versions | Create version
*VersionsApi* | [**delete_version**](docs/VersionsApi.md#delete_version) | **DELETE** /api/v3/versions/{id} | Delete version
*VersionsApi* | [**get_version**](docs/VersionsApi.md#get_version) | **GET** /api/v3/versions/{id} | Get version
*VersionsApi* | [**list_versions**](docs/VersionsApi.md#list_versions) | **GET** /api/v3/versions | List versions
*VersionsApi* | [**list_versions_available_in_a_project**](docs/VersionsApi.md#list_versions_available_in_a_project) | **GET** /api/v3/projects/{id}/versions | List versions available in a project
*VersionsApi* | [**list_versions_available_in_a_workspace**](docs/VersionsApi.md#list_versions_available_in_a_workspace) | **GET** /api/v3/workspaces/{id}/versions | List versions available in a workspace
*VersionsApi* | [**update_version**](docs/VersionsApi.md#update_version) | **PATCH** /api/v3/versions/{id} | Update Version
*VersionsApi* | [**version_create_form**](docs/VersionsApi.md#version_create_form) | **POST** /api/v3/versions/form | Version create form
*VersionsApi* | [**version_update_form**](docs/VersionsApi.md#version_update_form) | **POST** /api/v3/versions/{id}/form | Version update form
*VersionsApi* | [**view_version_schema**](docs/VersionsApi.md#view_version_schema) | **GET** /api/v3/versions/schema | View version schema
*ViewsApi* | [**create_views**](docs/ViewsApi.md#create_views) | **POST** /api/v3/views/{id} | Create view
*ViewsApi* | [**list_views**](docs/ViewsApi.md#list_views) | **GET** /api/v3/views | List views
*ViewsApi* | [**view_view**](docs/ViewsApi.md#view_view) | **GET** /api/v3/views/{id} | View view
*WikiPagesApi* | [**view_wiki_page**](docs/WikiPagesApi.md#view_wiki_page) | **GET** /api/v3/wiki_pages/{id} | View Wiki Page
*WorkPackagesApi* | [**list_work_package_activities_emoji_reactions**](docs/WorkPackagesApi.md#list_work_package_activities_emoji_reactions) | **GET** /api/v3/work_packages/{id}/activities_emoji_reactions | List emoji reactions by work package activities
*WorkPackagesApi* | [**add_watcher**](docs/WorkPackagesApi.md#add_watcher) | **POST** /api/v3/work_packages/{id}/watchers | Add watcher
*WorkPackagesApi* | [**available_projects_for_work_package**](docs/WorkPackagesApi.md#available_projects_for_work_package) | **GET** /api/v3/work_packages/{id}/available_projects | Available projects for work package
*WorkPackagesApi* | [**available_watchers**](docs/WorkPackagesApi.md#available_watchers) | **GET** /api/v3/work_packages/{id}/available_watchers | Available watchers
*WorkPackagesApi* | [**comment_work_package**](docs/WorkPackagesApi.md#comment_work_package) | **POST** /api/v3/work_packages/{id}/activities | Comment work package
*WorkPackagesApi* | [**create_project_work_package**](docs/WorkPackagesApi.md#create_project_work_package) | **POST** /api/v3/projects/{id}/work_packages | Create work package in project
*WorkPackagesApi* | [**create_work_package**](docs/WorkPackagesApi.md#create_work_package) | **POST** /api/v3/work_packages | Create Work Package
*WorkPackagesApi* | [**create_work_package_file_link**](docs/WorkPackagesApi.md#create_work_package_file_link) | **POST** /api/v3/work_packages/{id}/file_links | Creates file links.
*WorkPackagesApi* | [**create_work_package_reminder**](docs/WorkPackagesApi.md#create_work_package_reminder) | **POST** /api/v3/work_packages/{work_package_id}/reminders | Create a work package reminder
*WorkPackagesApi* | [**create_workspace_work_package**](docs/WorkPackagesApi.md#create_workspace_work_package) | **POST** /api/v3/workspaces/{id}/work_packages | Create work package in workspace
*WorkPackagesApi* | [**delete_work_package**](docs/WorkPackagesApi.md#delete_work_package) | **DELETE** /api/v3/work_packages/{id} | Delete Work Package
*WorkPackagesApi* | [**form_create_work_package**](docs/WorkPackagesApi.md#form_create_work_package) | **POST** /api/v3/work_packages/form | Form for creating a Work Package
*WorkPackagesApi* | [**form_create_work_package_in_project**](docs/WorkPackagesApi.md#form_create_work_package_in_project) | **POST** /api/v3/projects/{id}/work_packages/form | Form for creating Work Packages in a Project
*WorkPackagesApi* | [**form_create_work_package_in_workspace**](docs/WorkPackagesApi.md#form_create_work_package_in_workspace) | **POST** /api/v3/workspaces/{id}/work_packages/form | Form for creating Work Packages in a Workspace
*WorkPackagesApi* | [**form_edit_work_package**](docs/WorkPackagesApi.md#form_edit_work_package) | **POST** /api/v3/work_packages/{id}/form | Form for editing a Work Package
*WorkPackagesApi* | [**get_project_work_package_collection**](docs/WorkPackagesApi.md#get_project_work_package_collection) | **GET** /api/v3/projects/{id}/work_packages | Get work packages of project
*WorkPackagesApi* | [**get_workspace_work_package_collection**](docs/WorkPackagesApi.md#get_workspace_work_package_collection) | **GET** /api/v3/workspaces/{id}/work_packages | Get work packages of workspace
*WorkPackagesApi* | [**list_available_relation_candidates**](docs/WorkPackagesApi.md#list_available_relation_candidates) | **GET** /api/v3/work_packages/{id}/available_relation_candidates | Available relation candidates
*WorkPackagesApi* | [**list_watchers**](docs/WorkPackagesApi.md#list_watchers) | **GET** /api/v3/work_packages/{id}/watchers | List watchers
*WorkPackagesApi* | [**list_work_package_activities**](docs/WorkPackagesApi.md#list_work_package_activities) | **GET** /api/v3/work_packages/{id}/activities | List work package activities
*WorkPackagesApi* | [**list_work_package_file_links**](docs/WorkPackagesApi.md#list_work_package_file_links) | **GET** /api/v3/work_packages/{id}/file_links | Gets all file links of a work package
*WorkPackagesApi* | [**list_work_package_reminders**](docs/WorkPackagesApi.md#list_work_package_reminders) | **GET** /api/v3/work_packages/{work_package_id}/reminders | List work package reminders
*WorkPackagesApi* | [**list_work_package_schemas**](docs/WorkPackagesApi.md#list_work_package_schemas) | **GET** /api/v3/work_packages/schemas | List Work Package Schemas
*WorkPackagesApi* | [**list_work_packages**](docs/WorkPackagesApi.md#list_work_packages) | **GET** /api/v3/work_packages | List work packages
*WorkPackagesApi* | [**project_available_assignees**](docs/WorkPackagesApi.md#project_available_assignees) | **GET** /api/v3/projects/{id}/available_assignees | Project Available assignees
*WorkPackagesApi* | [**remove_watcher**](docs/WorkPackagesApi.md#remove_watcher) | **DELETE** /api/v3/work_packages/{id}/watchers/{user_id} | Remove watcher
*WorkPackagesApi* | [**revisions**](docs/WorkPackagesApi.md#revisions) | **GET** /api/v3/work_packages/{id}/revisions | Revisions
*WorkPackagesApi* | [**update_work_package**](docs/WorkPackagesApi.md#update_work_package) | **PATCH** /api/v3/work_packages/{id} | Update a Work Package
*WorkPackagesApi* | [**view_work_package**](docs/WorkPackagesApi.md#view_work_package) | **GET** /api/v3/work_packages/{id} | View Work Package
*WorkPackagesApi* | [**view_work_package_schema**](docs/WorkPackagesApi.md#view_work_package_schema) | **GET** /api/v3/work_packages/schemas/{identifier} | View Work Package Schema
*WorkPackagesApi* | [**work_package_available_assignees**](docs/WorkPackagesApi.md#work_package_available_assignees) | **GET** /api/v3/work_packages/{id}/available_assignees | Work Package Available assignees
*WorkPackagesApi* | [**workspace_available_assignees**](docs/WorkPackagesApi.md#workspace_available_assignees) | **GET** /api/v3/workspaces/{id}/available_assignees | Workspace Available assignees
*WorkScheduleApi* | [**create_non_working_day**](docs/WorkScheduleApi.md#create_non_working_day) | **POST** /api/v3/days/non_working | Creates a non-working day (NOT IMPLEMENTED)
*WorkScheduleApi* | [**delete_non_working_day**](docs/WorkScheduleApi.md#delete_non_working_day) | **DELETE** /api/v3/days/non_working/{date} | Removes a non-working day (NOT IMPLEMENTED)
*WorkScheduleApi* | [**list_days**](docs/WorkScheduleApi.md#list_days) | **GET** /api/v3/days | Lists days
*WorkScheduleApi* | [**list_non_working_days**](docs/WorkScheduleApi.md#list_non_working_days) | **GET** /api/v3/days/non_working | Lists all non working days
*WorkScheduleApi* | [**list_week_days**](docs/WorkScheduleApi.md#list_week_days) | **GET** /api/v3/days/week | Lists week days
*WorkScheduleApi* | [**update_non_working_day**](docs/WorkScheduleApi.md#update_non_working_day) | **PATCH** /api/v3/days/non_working/{date} | Update a non-working day attributes (NOT IMPLEMENTED)
*WorkScheduleApi* | [**update_week_day**](docs/WorkScheduleApi.md#update_week_day) | **PATCH** /api/v3/days/week/{day} | Update a week day attributes (NOT IMPLEMENTED)
*WorkScheduleApi* | [**update_week_days**](docs/WorkScheduleApi.md#update_week_days) | **PATCH** /api/v3/days/week | Update week days (NOT IMPLEMENTED)
*WorkScheduleApi* | [**view_day**](docs/WorkScheduleApi.md#view_day) | **GET** /api/v3/days/{date} | View day
*WorkScheduleApi* | [**view_non_working_day**](docs/WorkScheduleApi.md#view_non_working_day) | **GET** /api/v3/days/non_working/{date} | View a non-working day
*WorkScheduleApi* | [**view_week_day**](docs/WorkScheduleApi.md#view_week_day) | **GET** /api/v3/days/week/{day} | View a week day
*WorkspaceApi* | [**list_workspace**](docs/WorkspaceApi.md#list_workspace) | **GET** /api/v3/workspaces | List workspace
*WorkspacesApi* | [**favorite_workspace**](docs/WorkspacesApi.md#favorite_workspace) | **POST** /api/v3/workspaces/{id}/favorite | Favorite Workspace
*WorkspacesApi* | [**list_types_available_in_a_workspace**](docs/WorkspacesApi.md#list_types_available_in_a_workspace) | **GET** /api/v3/workspaces/{id}/types | List types available in a workspace
*WorkspacesApi* | [**unfavorite_workspace**](docs/WorkspacesApi.md#unfavorite_workspace) | **DELETE** /api/v3/workspaces/{id}/favorite | Unfavorite Workspace
*WorkspacesApi* | [**view_workspace_schema**](docs/WorkspacesApi.md#view_workspace_schema) | **GET** /api/v3/workspaces/schema | View workspace schema
*DefaultApi* | [**get_custom_field_item**](docs/DefaultApi.md#get_custom_field_item) | **GET** /api/v3/custom_field_items/{id} | Get a custom field hierarchy item
*DefaultApi* | [**get_custom_field_item_branch**](docs/DefaultApi.md#get_custom_field_item_branch) | **GET** /api/v3/custom_field_items/{id}/branch | Get a custom field hierarchy item&#39;s branch
*DefaultApi* | [**get_custom_field_items**](docs/DefaultApi.md#get_custom_field_items) | **GET** /api/v3/custom_fields/{id}/items | Get the custom field hierarchy items


## Documentation For Models

 - [ActivityCommentWriteModel](docs/ActivityCommentWriteModel.md)
 - [ActivityCommentWriteModelComment](docs/ActivityCommentWriteModelComment.md)
 - [ActivityModel](docs/ActivityModel.md)
 - [ActivityModelEmbedded](docs/ActivityModelEmbedded.md)
 - [ActivityModelLinks](docs/ActivityModelLinks.md)
 - [AddWatcherRequest](docs/AddWatcherRequest.md)
 - [AttachmentModel](docs/AttachmentModel.md)
 - [AttachmentModelDigest](docs/AttachmentModelDigest.md)
 - [AttachmentModelLinks](docs/AttachmentModelLinks.md)
 - [AttachmentsModel](docs/AttachmentsModel.md)
 - [AttachmentsModelAllOfEmbedded](docs/AttachmentsModelAllOfEmbedded.md)
 - [AttachmentsModelAllOfEmbeddedElements](docs/AttachmentsModelAllOfEmbeddedElements.md)
 - [AttachmentsModelAllOfLinks](docs/AttachmentsModelAllOfLinks.md)
 - [AvailableAssigneesModel](docs/AvailableAssigneesModel.md)
 - [AvailableAssigneesModelAllOfEmbedded](docs/AvailableAssigneesModelAllOfEmbedded.md)
 - [AvailableAssigneesModelAllOfEmbeddedElements](docs/AvailableAssigneesModelAllOfEmbeddedElements.md)
 - [AvailableAssigneesModelAllOfLinks](docs/AvailableAssigneesModelAllOfLinks.md)
 - [BudgetModel](docs/BudgetModel.md)
 - [BudgetModelLinks](docs/BudgetModelLinks.md)
 - [CategoriesByWorkspaceModel](docs/CategoriesByWorkspaceModel.md)
 - [CategoriesByWorkspaceModelAllOfEmbedded](docs/CategoriesByWorkspaceModelAllOfEmbedded.md)
 - [CategoriesByWorkspaceModelAllOfEmbeddedElements](docs/CategoriesByWorkspaceModelAllOfEmbeddedElements.md)
 - [CategoriesByWorkspaceModelAllOfLinks](docs/CategoriesByWorkspaceModelAllOfLinks.md)
 - [CategoryModel](docs/CategoryModel.md)
 - [CategoryModelLinks](docs/CategoryModelLinks.md)
 - [CollectionLinks](docs/CollectionLinks.md)
 - [CollectionModel](docs/CollectionModel.md)
 - [ConfigurationModel](docs/ConfigurationModel.md)
 - [CreateViewsRequest](docs/CreateViewsRequest.md)
 - [CreateViewsRequestLinks](docs/CreateViewsRequestLinks.md)
 - [CreateViewsRequestLinksQuery](docs/CreateViewsRequestLinksQuery.md)
 - [CreateWorkPackageReminderRequest](docs/CreateWorkPackageReminderRequest.md)
 - [CustomActionModel](docs/CustomActionModel.md)
 - [CustomActionModelLinks](docs/CustomActionModelLinks.md)
 - [CustomOptionModel](docs/CustomOptionModel.md)
 - [CustomOptionModelLinks](docs/CustomOptionModelLinks.md)
 - [DayCollectionModel](docs/DayCollectionModel.md)
 - [DayCollectionModelAllOfEmbedded](docs/DayCollectionModelAllOfEmbedded.md)
 - [DayCollectionModelAllOfLinks](docs/DayCollectionModelAllOfLinks.md)
 - [DayModel](docs/DayModel.md)
 - [DayModelLinks](docs/DayModelLinks.md)
 - [DocumentModel](docs/DocumentModel.md)
 - [DocumentModelLinks](docs/DocumentModelLinks.md)
 - [EmojiReactionModel](docs/EmojiReactionModel.md)
 - [EmojiReactionModelLinks](docs/EmojiReactionModelLinks.md)
 - [EmojiReactionsModel](docs/EmojiReactionsModel.md)
 - [EmojiReactionsModelEmbedded](docs/EmojiReactionsModelEmbedded.md)
 - [EmojiReactionsModelLinks](docs/EmojiReactionsModelLinks.md)
 - [ErrorResponse](docs/ErrorResponse.md)
 - [ErrorResponseEmbedded](docs/ErrorResponseEmbedded.md)
 - [ErrorResponseEmbeddedDetails](docs/ErrorResponseEmbeddedDetails.md)
 - [ExecuteCustomActionRequest](docs/ExecuteCustomActionRequest.md)
 - [ExecuteCustomActionRequestLinks](docs/ExecuteCustomActionRequestLinks.md)
 - [ExecuteCustomActionRequestLinksWorkPackage](docs/ExecuteCustomActionRequestLinksWorkPackage.md)
 - [FileLinkCollectionReadModel](docs/FileLinkCollectionReadModel.md)
 - [FileLinkCollectionReadModelAllOfEmbedded](docs/FileLinkCollectionReadModelAllOfEmbedded.md)
 - [FileLinkCollectionReadModelAllOfLinks](docs/FileLinkCollectionReadModelAllOfLinks.md)
 - [FileLinkCollectionWriteModel](docs/FileLinkCollectionWriteModel.md)
 - [FileLinkCollectionWriteModelEmbedded](docs/FileLinkCollectionWriteModelEmbedded.md)
 - [FileLinkOriginDataModel](docs/FileLinkOriginDataModel.md)
 - [FileLinkReadModel](docs/FileLinkReadModel.md)
 - [FileLinkReadModelEmbedded](docs/FileLinkReadModelEmbedded.md)
 - [FileLinkReadModelLinks](docs/FileLinkReadModelLinks.md)
 - [FileLinkWriteModel](docs/FileLinkWriteModel.md)
 - [FileLinkWriteModelLinks](docs/FileLinkWriteModelLinks.md)
 - [FileLinkWriteModelLinksOneOf](docs/FileLinkWriteModelLinksOneOf.md)
 - [FileLinkWriteModelLinksOneOf1](docs/FileLinkWriteModelLinksOneOf1.md)
 - [FileUploadFormMetadata](docs/FileUploadFormMetadata.md)
 - [Formattable](docs/Formattable.md)
 - [GridCollectionModel](docs/GridCollectionModel.md)
 - [GridCollectionModelAllOfEmbedded](docs/GridCollectionModelAllOfEmbedded.md)
 - [GridReadModel](docs/GridReadModel.md)
 - [GridReadModelLinks](docs/GridReadModelLinks.md)
 - [GridWidgetModel](docs/GridWidgetModel.md)
 - [GridWriteModel](docs/GridWriteModel.md)
 - [GridWriteModelLinks](docs/GridWriteModelLinks.md)
 - [GroupCollectionModel](docs/GroupCollectionModel.md)
 - [GroupCollectionModelAllOfEmbedded](docs/GroupCollectionModelAllOfEmbedded.md)
 - [GroupCollectionModelAllOfLinks](docs/GroupCollectionModelAllOfLinks.md)
 - [GroupModel](docs/GroupModel.md)
 - [GroupModelAllOfEmbedded](docs/GroupModelAllOfEmbedded.md)
 - [GroupModelAllOfLinks](docs/GroupModelAllOfLinks.md)
 - [GroupModelAllOfLinksMembers](docs/GroupModelAllOfLinksMembers.md)
 - [GroupWriteModel](docs/GroupWriteModel.md)
 - [GroupWriteModelLinks](docs/GroupWriteModelLinks.md)
 - [HelpTextCollectionModel](docs/HelpTextCollectionModel.md)
 - [HelpTextCollectionModelAllOfEmbedded](docs/HelpTextCollectionModelAllOfEmbedded.md)
 - [HelpTextCollectionModelAllOfLinks](docs/HelpTextCollectionModelAllOfLinks.md)
 - [HelpTextModel](docs/HelpTextModel.md)
 - [HelpTextModelLinks](docs/HelpTextModelLinks.md)
 - [HierarchyItemCollectionModel](docs/HierarchyItemCollectionModel.md)
 - [HierarchyItemCollectionModelAllOfEmbedded](docs/HierarchyItemCollectionModelAllOfEmbedded.md)
 - [HierarchyItemCollectionModelAllOfLinks](docs/HierarchyItemCollectionModelAllOfLinks.md)
 - [HierarchyItemReadModel](docs/HierarchyItemReadModel.md)
 - [HierarchyItemReadModelLinks](docs/HierarchyItemReadModelLinks.md)
 - [Link](docs/Link.md)
 - [ListAvailableParentProjectCandidatesModel](docs/ListAvailableParentProjectCandidatesModel.md)
 - [ListAvailableParentProjectCandidatesModelAllOfEmbedded](docs/ListAvailableParentProjectCandidatesModelAllOfEmbedded.md)
 - [ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements](docs/ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements.md)
 - [ListAvailableParentProjectCandidatesModelAllOfLinks](docs/ListAvailableParentProjectCandidatesModelAllOfLinks.md)
 - [ListReminders200Response](docs/ListReminders200Response.md)
 - [ListReminders200ResponseEmbedded](docs/ListReminders200ResponseEmbedded.md)
 - [MeetingModel](docs/MeetingModel.md)
 - [MeetingModelLinks](docs/MeetingModelLinks.md)
 - [MembershipCollectionModel](docs/MembershipCollectionModel.md)
 - [MembershipCollectionModelAllOfEmbedded](docs/MembershipCollectionModelAllOfEmbedded.md)
 - [MembershipFormModel](docs/MembershipFormModel.md)
 - [MembershipFormModelEmbedded](docs/MembershipFormModelEmbedded.md)
 - [MembershipFormModelEmbeddedValidationError](docs/MembershipFormModelEmbeddedValidationError.md)
 - [MembershipFormModelLinks](docs/MembershipFormModelLinks.md)
 - [MembershipReadModel](docs/MembershipReadModel.md)
 - [MembershipReadModelEmbedded](docs/MembershipReadModelEmbedded.md)
 - [MembershipReadModelEmbeddedPrincipal](docs/MembershipReadModelEmbeddedPrincipal.md)
 - [MembershipReadModelEmbeddedProject](docs/MembershipReadModelEmbeddedProject.md)
 - [MembershipReadModelLinks](docs/MembershipReadModelLinks.md)
 - [MembershipSchemaModel](docs/MembershipSchemaModel.md)
 - [MembershipWriteModel](docs/MembershipWriteModel.md)
 - [MembershipWriteModelLinks](docs/MembershipWriteModelLinks.md)
 - [MembershipWriteModelMeta](docs/MembershipWriteModelMeta.md)
 - [NewsCreateModel](docs/NewsCreateModel.md)
 - [NewsCreateModelLinks](docs/NewsCreateModelLinks.md)
 - [NewsModel](docs/NewsModel.md)
 - [NewsModelLinks](docs/NewsModelLinks.md)
 - [NonWorkingDayCollectionModel](docs/NonWorkingDayCollectionModel.md)
 - [NonWorkingDayCollectionModelAllOfEmbedded](docs/NonWorkingDayCollectionModelAllOfEmbedded.md)
 - [NonWorkingDayCollectionModelAllOfLinks](docs/NonWorkingDayCollectionModelAllOfLinks.md)
 - [NonWorkingDayModel](docs/NonWorkingDayModel.md)
 - [NonWorkingDayModelLinks](docs/NonWorkingDayModelLinks.md)
 - [NotificationCollectionModel](docs/NotificationCollectionModel.md)
 - [NotificationCollectionModelAllOfEmbedded](docs/NotificationCollectionModelAllOfEmbedded.md)
 - [NotificationCollectionModelAllOfLinks](docs/NotificationCollectionModelAllOfLinks.md)
 - [NotificationModel](docs/NotificationModel.md)
 - [NotificationModelEmbedded](docs/NotificationModelEmbedded.md)
 - [NotificationModelLinks](docs/NotificationModelLinks.md)
 - [OAuthApplicationReadModel](docs/OAuthApplicationReadModel.md)
 - [OAuthApplicationReadModelLinks](docs/OAuthApplicationReadModelLinks.md)
 - [OAuthClientCredentialsReadModel](docs/OAuthClientCredentialsReadModel.md)
 - [OAuthClientCredentialsReadModelLinks](docs/OAuthClientCredentialsReadModelLinks.md)
 - [OAuthClientCredentialsWriteModel](docs/OAuthClientCredentialsWriteModel.md)
 - [OffsetPaginatedCollectionLinks](docs/OffsetPaginatedCollectionLinks.md)
 - [OffsetPaginatedCollectionModel](docs/OffsetPaginatedCollectionModel.md)
 - [PaginatedCollectionModel](docs/PaginatedCollectionModel.md)
 - [PaginatedCollectionModelAllOfLinks](docs/PaginatedCollectionModelAllOfLinks.md)
 - [PlaceholderUserCollectionModel](docs/PlaceholderUserCollectionModel.md)
 - [PlaceholderUserCollectionModelAllOfEmbedded](docs/PlaceholderUserCollectionModelAllOfEmbedded.md)
 - [PlaceholderUserCollectionModelAllOfLinks](docs/PlaceholderUserCollectionModelAllOfLinks.md)
 - [PlaceholderUserCreateModel](docs/PlaceholderUserCreateModel.md)
 - [PlaceholderUserModel](docs/PlaceholderUserModel.md)
 - [PlaceholderUserModelAllOfLinks](docs/PlaceholderUserModelAllOfLinks.md)
 - [PortfolioCollectionModel](docs/PortfolioCollectionModel.md)
 - [PortfolioCollectionModelAllOfEmbedded](docs/PortfolioCollectionModelAllOfEmbedded.md)
 - [PortfolioCollectionModelAllOfLinks](docs/PortfolioCollectionModelAllOfLinks.md)
 - [PortfolioModel](docs/PortfolioModel.md)
 - [PortfolioModelAllOfLinks](docs/PortfolioModelAllOfLinks.md)
 - [PortfolioModelAllOfLinksAncestors](docs/PortfolioModelAllOfLinksAncestors.md)
 - [PortfolioModelAllOfLinksStorages](docs/PortfolioModelAllOfLinksStorages.md)
 - [PostModel](docs/PostModel.md)
 - [PostModelLinks](docs/PostModelLinks.md)
 - [PrincipalCollectionModel](docs/PrincipalCollectionModel.md)
 - [PrincipalCollectionModelAllOfEmbedded](docs/PrincipalCollectionModelAllOfEmbedded.md)
 - [PrincipalCollectionModelAllOfEmbeddedElements](docs/PrincipalCollectionModelAllOfEmbeddedElements.md)
 - [PrincipalModel](docs/PrincipalModel.md)
 - [PrincipalModelLinks](docs/PrincipalModelLinks.md)
 - [PriorityCollectionModel](docs/PriorityCollectionModel.md)
 - [PriorityCollectionModelAllOfEmbedded](docs/PriorityCollectionModelAllOfEmbedded.md)
 - [PriorityCollectionModelAllOfLinks](docs/PriorityCollectionModelAllOfLinks.md)
 - [PriorityCollectionModelAllOfLinksSelf](docs/PriorityCollectionModelAllOfLinksSelf.md)
 - [PriorityModel](docs/PriorityModel.md)
 - [PriorityModelLinks](docs/PriorityModelLinks.md)
 - [ProgramCollectionModel](docs/ProgramCollectionModel.md)
 - [ProgramCollectionModelAllOfEmbedded](docs/ProgramCollectionModelAllOfEmbedded.md)
 - [ProgramCollectionModelAllOfLinks](docs/ProgramCollectionModelAllOfLinks.md)
 - [ProgramModel](docs/ProgramModel.md)
 - [ProgramModelAllOfLinks](docs/ProgramModelAllOfLinks.md)
 - [ProgramModelAllOfLinksAncestors](docs/ProgramModelAllOfLinksAncestors.md)
 - [ProgramModelAllOfLinksStorages](docs/ProgramModelAllOfLinksStorages.md)
 - [ProjectCollectionModel](docs/ProjectCollectionModel.md)
 - [ProjectCollectionModelAllOfEmbedded](docs/ProjectCollectionModelAllOfEmbedded.md)
 - [ProjectCollectionModelAllOfLinks](docs/ProjectCollectionModelAllOfLinks.md)
 - [ProjectConfigurationModel](docs/ProjectConfigurationModel.md)
 - [ProjectModel](docs/ProjectModel.md)
 - [ProjectModelAllOfLinks](docs/ProjectModelAllOfLinks.md)
 - [ProjectModelAllOfLinksAncestors](docs/ProjectModelAllOfLinksAncestors.md)
 - [ProjectModelAllOfLinksStorages](docs/ProjectModelAllOfLinksStorages.md)
 - [ProjectPhaseDefinitionCollectionModel](docs/ProjectPhaseDefinitionCollectionModel.md)
 - [ProjectPhaseDefinitionCollectionModelAllOfEmbedded](docs/ProjectPhaseDefinitionCollectionModelAllOfEmbedded.md)
 - [ProjectPhaseDefinitionCollectionModelAllOfLinks](docs/ProjectPhaseDefinitionCollectionModelAllOfLinks.md)
 - [ProjectPhaseDefinitionModel](docs/ProjectPhaseDefinitionModel.md)
 - [ProjectPhaseDefinitionModelLinks](docs/ProjectPhaseDefinitionModelLinks.md)
 - [ProjectPhaseModel](docs/ProjectPhaseModel.md)
 - [ProjectPhaseModelLinks](docs/ProjectPhaseModelLinks.md)
 - [ProjectStorageCollectionModel](docs/ProjectStorageCollectionModel.md)
 - [ProjectStorageCollectionModelAllOfEmbedded](docs/ProjectStorageCollectionModelAllOfEmbedded.md)
 - [ProjectStorageCollectionModelAllOfLinks](docs/ProjectStorageCollectionModelAllOfLinks.md)
 - [ProjectStorageModel](docs/ProjectStorageModel.md)
 - [ProjectStorageModelLinks](docs/ProjectStorageModelLinks.md)
 - [QueryColumnModel](docs/QueryColumnModel.md)
 - [QueryCreateForm](docs/QueryCreateForm.md)
 - [QueryFilterInstanceModel](docs/QueryFilterInstanceModel.md)
 - [QueryFilterInstanceModelLinks](docs/QueryFilterInstanceModelLinks.md)
 - [QueryFilterInstanceSchemaModel](docs/QueryFilterInstanceSchemaModel.md)
 - [QueryFilterInstanceSchemaModelLinks](docs/QueryFilterInstanceSchemaModelLinks.md)
 - [QueryFilterModel](docs/QueryFilterModel.md)
 - [QueryModel](docs/QueryModel.md)
 - [QueryModelLinks](docs/QueryModelLinks.md)
 - [QueryOperatorModel](docs/QueryOperatorModel.md)
 - [QuerySortByModel](docs/QuerySortByModel.md)
 - [QueryUpdateForm](docs/QueryUpdateForm.md)
 - [RelationCollectionModel](docs/RelationCollectionModel.md)
 - [RelationCollectionModelAllOfEmbedded](docs/RelationCollectionModelAllOfEmbedded.md)
 - [RelationCollectionModelAllOfLinks](docs/RelationCollectionModelAllOfLinks.md)
 - [RelationReadModel](docs/RelationReadModel.md)
 - [RelationReadModelEmbedded](docs/RelationReadModelEmbedded.md)
 - [RelationReadModelLinks](docs/RelationReadModelLinks.md)
 - [RelationWriteModel](docs/RelationWriteModel.md)
 - [RelationWriteModelLinks](docs/RelationWriteModelLinks.md)
 - [ReminderModel](docs/ReminderModel.md)
 - [ReminderModelLinks](docs/ReminderModelLinks.md)
 - [RevisionModel](docs/RevisionModel.md)
 - [RevisionModelLinks](docs/RevisionModelLinks.md)
 - [RoleModel](docs/RoleModel.md)
 - [RoleModelLinks](docs/RoleModelLinks.md)
 - [RootModel](docs/RootModel.md)
 - [RootModelLinks](docs/RootModelLinks.md)
 - [SchemaModel](docs/SchemaModel.md)
 - [SchemaModelLinks](docs/SchemaModelLinks.md)
 - [SchemaPropertyModel](docs/SchemaPropertyModel.md)
 - [ShowOrValidateFormRequest](docs/ShowOrValidateFormRequest.md)
 - [StatusCollectionModel](docs/StatusCollectionModel.md)
 - [StatusCollectionModelAllOfEmbedded](docs/StatusCollectionModelAllOfEmbedded.md)
 - [StatusModel](docs/StatusModel.md)
 - [StatusModelLinks](docs/StatusModelLinks.md)
 - [StorageCollectionModel](docs/StorageCollectionModel.md)
 - [StorageCollectionModelAllOfEmbedded](docs/StorageCollectionModelAllOfEmbedded.md)
 - [StorageCollectionModelAllOfLinks](docs/StorageCollectionModelAllOfLinks.md)
 - [StorageFileModel](docs/StorageFileModel.md)
 - [StorageFileModelAllOfLinks](docs/StorageFileModelAllOfLinks.md)
 - [StorageFileUploadLinkModel](docs/StorageFileUploadLinkModel.md)
 - [StorageFileUploadLinkModelLinks](docs/StorageFileUploadLinkModelLinks.md)
 - [StorageFileUploadPreparationModel](docs/StorageFileUploadPreparationModel.md)
 - [StorageFilesModel](docs/StorageFilesModel.md)
 - [StorageFolderWriteModel](docs/StorageFolderWriteModel.md)
 - [StorageReadModel](docs/StorageReadModel.md)
 - [StorageReadModelEmbedded](docs/StorageReadModelEmbedded.md)
 - [StorageReadModelLinks](docs/StorageReadModelLinks.md)
 - [StorageWriteModel](docs/StorageWriteModel.md)
 - [StorageWriteModelLinks](docs/StorageWriteModelLinks.md)
 - [TimeEntryActivityModel](docs/TimeEntryActivityModel.md)
 - [TimeEntryActivityModelEmbedded](docs/TimeEntryActivityModelEmbedded.md)
 - [TimeEntryActivityModelLinks](docs/TimeEntryActivityModelLinks.md)
 - [TimeEntryCollectionModel](docs/TimeEntryCollectionModel.md)
 - [TimeEntryCollectionModelAllOfEmbedded](docs/TimeEntryCollectionModelAllOfEmbedded.md)
 - [TimeEntryCollectionModelAllOfLinks](docs/TimeEntryCollectionModelAllOfLinks.md)
 - [TimeEntryModel](docs/TimeEntryModel.md)
 - [TimeEntryModelAllOfLinks](docs/TimeEntryModelAllOfLinks.md)
 - [ToggleActivityEmojiReactionRequest](docs/ToggleActivityEmojiReactionRequest.md)
 - [TypeModel](docs/TypeModel.md)
 - [TypeModelLinks](docs/TypeModelLinks.md)
 - [TypesByWorkspaceModel](docs/TypesByWorkspaceModel.md)
 - [TypesByWorkspaceModelAllOfEmbedded](docs/TypesByWorkspaceModelAllOfEmbedded.md)
 - [TypesByWorkspaceModelAllOfEmbeddedElements](docs/TypesByWorkspaceModelAllOfEmbeddedElements.md)
 - [TypesByWorkspaceModelAllOfLinks](docs/TypesByWorkspaceModelAllOfLinks.md)
 - [UpdateDocumentRequest](docs/UpdateDocumentRequest.md)
 - [UpdateDocumentRequestDescription](docs/UpdateDocumentRequestDescription.md)
 - [UpdateReminderRequest](docs/UpdateReminderRequest.md)
 - [UpdateUserPreferencesRequest](docs/UpdateUserPreferencesRequest.md)
 - [UserCollectionModel](docs/UserCollectionModel.md)
 - [UserCollectionModelAllOfEmbedded](docs/UserCollectionModelAllOfEmbedded.md)
 - [UserCollectionModelAllOfLinks](docs/UserCollectionModelAllOfLinks.md)
 - [UserCreateModel](docs/UserCreateModel.md)
 - [UserModel](docs/UserModel.md)
 - [UserModelAllOfLinks](docs/UserModelAllOfLinks.md)
 - [ValuesPropertyModel](docs/ValuesPropertyModel.md)
 - [ValuesPropertyModelLinks](docs/ValuesPropertyModelLinks.md)
 - [VersionCollectionModel](docs/VersionCollectionModel.md)
 - [VersionCollectionModelAllOfEmbedded](docs/VersionCollectionModelAllOfEmbedded.md)
 - [VersionCollectionModelAllOfLinks](docs/VersionCollectionModelAllOfLinks.md)
 - [VersionReadModel](docs/VersionReadModel.md)
 - [VersionReadModelAllOfLinks](docs/VersionReadModelAllOfLinks.md)
 - [VersionWriteModel](docs/VersionWriteModel.md)
 - [VersionWriteModelAllOfLinks](docs/VersionWriteModelAllOfLinks.md)
 - [VersionsByWorkspaceModel](docs/VersionsByWorkspaceModel.md)
 - [VersionsByWorkspaceModelAllOfEmbedded](docs/VersionsByWorkspaceModelAllOfEmbedded.md)
 - [VersionsByWorkspaceModelAllOfEmbeddedElements](docs/VersionsByWorkspaceModelAllOfEmbeddedElements.md)
 - [VersionsByWorkspaceModelAllOfLinks](docs/VersionsByWorkspaceModelAllOfLinks.md)
 - [WatchersModel](docs/WatchersModel.md)
 - [WatchersModelAllOfEmbedded](docs/WatchersModelAllOfEmbedded.md)
 - [WatchersModelAllOfEmbeddedElements](docs/WatchersModelAllOfEmbeddedElements.md)
 - [WatchersModelAllOfLinks](docs/WatchersModelAllOfLinks.md)
 - [WeekDayCollectionModel](docs/WeekDayCollectionModel.md)
 - [WeekDayCollectionModelAllOfEmbedded](docs/WeekDayCollectionModelAllOfEmbedded.md)
 - [WeekDayCollectionModelAllOfLinks](docs/WeekDayCollectionModelAllOfLinks.md)
 - [WeekDayCollectionWriteModel](docs/WeekDayCollectionWriteModel.md)
 - [WeekDayCollectionWriteModelEmbedded](docs/WeekDayCollectionWriteModelEmbedded.md)
 - [WeekDayCollectionWriteModelEmbeddedElementsInner](docs/WeekDayCollectionWriteModelEmbeddedElementsInner.md)
 - [WeekDayModel](docs/WeekDayModel.md)
 - [WeekDaySelfLinkModel](docs/WeekDaySelfLinkModel.md)
 - [WeekDayWriteModel](docs/WeekDayWriteModel.md)
 - [WikiPageModel](docs/WikiPageModel.md)
 - [WikiPageModelLinks](docs/WikiPageModelLinks.md)
 - [WorkPackageFormModel](docs/WorkPackageFormModel.md)
 - [WorkPackageFormModelEmbedded](docs/WorkPackageFormModelEmbedded.md)
 - [WorkPackageFormModelLinks](docs/WorkPackageFormModelLinks.md)
 - [WorkPackageModel](docs/WorkPackageModel.md)
 - [WorkPackageModelAllOfLinks](docs/WorkPackageModelAllOfLinks.md)
 - [WorkPackageModelAllOfLinksAncestors](docs/WorkPackageModelAllOfLinksAncestors.md)
 - [WorkPackageModelAllOfLinksChildren](docs/WorkPackageModelAllOfLinksChildren.md)
 - [WorkPackageModelAllOfLinksCustomActions](docs/WorkPackageModelAllOfLinksCustomActions.md)
 - [WorkPackagePatchModel](docs/WorkPackagePatchModel.md)
 - [WorkPackageSchemaModel](docs/WorkPackageSchemaModel.md)
 - [WorkPackageSchemaModelLinks](docs/WorkPackageSchemaModelLinks.md)
 - [WorkPackageWriteModel](docs/WorkPackageWriteModel.md)
 - [WorkPackageWriteModelLinks](docs/WorkPackageWriteModelLinks.md)
 - [WorkPackageWriteModelMeta](docs/WorkPackageWriteModelMeta.md)
 - [WorkPackagesModel](docs/WorkPackagesModel.md)
 - [WorkPackagesModelAllOfEmbedded](docs/WorkPackagesModelAllOfEmbedded.md)
 - [WorkPackagesModelAllOfLinks](docs/WorkPackagesModelAllOfLinks.md)
 - [WorkspaceCollectionModel](docs/WorkspaceCollectionModel.md)
 - [WorkspaceCollectionModelAllOfEmbedded](docs/WorkspaceCollectionModelAllOfEmbedded.md)
 - [WorkspaceCollectionModelAllOfEmbeddedElements](docs/WorkspaceCollectionModelAllOfEmbeddedElements.md)
 - [WorkspaceCollectionModelAllOfLinks](docs/WorkspaceCollectionModelAllOfLinks.md)
 - [WorkspacesSchemaModel](docs/WorkspacesSchemaModel.md)
 - [WorkspacesSchemaModelAttributeGroupsInner](docs/WorkspacesSchemaModelAttributeGroupsInner.md)
 - [WorkspacesSchemaModelLinks](docs/WorkspacesSchemaModelLinks.md)
 - [WorkspacesSchemaModelLinksSelf](docs/WorkspacesSchemaModelLinksSelf.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="BasicAuth"></a>
### BasicAuth

- **Type**: HTTP basic authentication


## Author




