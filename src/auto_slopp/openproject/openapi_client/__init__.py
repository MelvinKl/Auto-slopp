# coding: utf-8

# flake8: noqa

"""
    OpenProject API V3 (Stable)

    You're looking at the current **stable** documentation of the OpenProject APIv3. If you're interested in the current development version, please go to [github.com/opf](https://github.com/opf/openproject/tree/dev/docs/api/apiv3).  ## Introduction  The documentation for the APIv3 is written according to the [OpenAPI 3.1 Specification](https://swagger.io/specification/). You can either view the static version of this documentation on the [website](https://www.openproject.org/docs/api/introduction/) or the interactive version, rendered with [OpenAPI Explorer](https://github.com/Rhosys/openapi-explorer/blob/main/README.md), in your OpenProject installation under `/api/docs`. In the latter you can try out the various API endpoints directly interacting with our OpenProject data. Moreover you can access the specification source itself under `/api/v3/spec.json` and `/api/v3/spec.yml` (e.g. [here](https://community.openproject.org/api/v3/spec.yml)).  The APIv3 is a hypermedia REST API, a shorthand for \"Hypermedia As The Engine Of Application State\" (HATEOAS). This means that each endpoint of this API will have links to other resources or actions defined in the resulting body.  These related resources and actions for any given resource will be context sensitive. For example, only actions that the authenticated user can take are being rendered. This can be used to dynamically identify actions that the user might take for any given response.  As an example, if you fetch a work package through the [Work Package endpoint](https://www.openproject.org/docs/api/endpoints/work-packages/), the `update` link will only be present when the user you authenticated has been granted a permission to update the work package in the assigned project.  ## HAL+JSON  HAL is a simple format that gives a consistent and easy way to hyperlink between resources in your API. Read more in the following specification: [https://tools.ietf.org/html/draft-kelly-json-hal-08](https://tools.ietf.org/html/draft-kelly-json-hal-08)  **OpenProject API implementation of HAL+JSON format** enriches JSON and introduces a few meta properties:  - `_type` - specifies the type of the resource (e.g.: WorkPackage, Project) - `_links` - contains all related resource and action links available for the resource - `_embedded` - contains all embedded objects  HAL does not guarantee that embedded resources are embedded in their full representation, they might as well be partially represented (e.g. some properties can be left out). However in this API you have the guarantee that whenever a resource is **embedded**, it is embedded in its **full representation**.  ## API response structure  All API responses contain a single HAL+JSON object, even collections of objects are technically represented by a single HAL+JSON object that itself contains its members. More details on collections can be found in the [Collections Section](https://www.openproject.org/docs/api/collections/).  ## Authentication  The API supports the following authentication schemes:  * Session-based authentication * API tokens     * passed as Bearer token     * passed via Basic auth * OAuth 2.0     * using built-in authorization server     * using an external authorization server (RFC 9068)  Depending on the settings of the OpenProject instance many resources can be accessed without being authenticated. In case the instance requires authentication on all requests the client will receive an **HTTP 401** status code in response to any request.  Otherwise unauthenticated clients have all the permissions of the anonymous user.  ### Session-based authentication  This means you have to login to OpenProject via the Web-Interface to be authenticated in the API. This method is well-suited for clients acting within the browser, like the Angular-Client built into OpenProject.  In this case, you always need to pass the HTTP header `X-Requested-With \"XMLHttpRequest\"` for authentication.  ### API token as bearer token  Users can authenticate towards the API v3 using an API token as a bearer token.  For example:  ```shell API_KEY=opapi-2519132cdf62dcf5a66fd96394672079f9e9cad1 curl -H \"Authorization: Bearer $API_KEY\" https://community.openproject.org/api/v3/users/42 ```  Users can generate API tokens on their account page.  ### API token through Basic Auth  API tokens can also be used with basic auth, using the user name `apikey` (NOT your login) and the API token as the password.  For example:  ```shell API_KEY=opapi-2519132cdf62dcf5a66fd96394672079f9e9cad1 curl -u apikey:$API_KEY https://community.openproject.org/api/v3/users/42 ```  ### OAuth 2.0 authentication  OpenProject allows authentication and authorization with OAuth2 with *Authorization code flow*, as well as *Client credentials* operation modes.  To get started, you first need to register an application in the OpenProject OAuth administration section of your installation. This will save an entry for your application with a client unique identifier (`client_id`) and an accompanying secret key (`client_secret`).  You can then use one the following guides to perform the supported OAuth 2.0 flows:  - [Authorization code flow](https://oauth.net/2/grant-types/authorization-code)  - [Authorization code flow with PKCE](https://doorkeeper.gitbook.io/guides/ruby-on-rails/pkce-flow), recommended for clients unable to keep the client_secret confidential  - [Client credentials](https://oauth.net/2/grant-types/client-credentials/) - Requires an application to be bound to an impersonating user for non-public access  ### OAuth 2.0 using an external authorization server  There is a possibility to use JSON Web Tokens (JWT) generated by an OIDC provider configured in OpenProject as a bearer token to do authenticated requests against the API. The following requirements must be met:  - OIDC provider must be configured in OpenProject with **jwks_uri** - JWT must be signed using RSA algorithm - JWT **iss** claim must be equal to OIDC provider **issuer** - JWT **aud** claim must contain the OpenProject **client ID** used at the OIDC provider - JWT **scope** claim must include a valid scope to access the desired API (e.g. `api_v3` for APIv3) - JWT must be actual (neither expired or too early to be used) - JWT must be passed in Authorization header like: `Authorization: Bearer {jwt}` - User from **sub** claim must be linked to OpenProject before (e.g. by logging in), otherwise it will be not authenticated  In more general terms, OpenProject should be compliant to [RFC 9068](https://www.rfc-editor.org/rfc/rfc9068) when validating access tokens.  ### Why not username and password?  The simplest way to do basic auth would be to use a user's username and password naturally. However, OpenProject already has supported API keys in the past for the API v2, though not through basic auth.  Using **username and password** directly would have some advantages:  * It is intuitive for the user who then just has to provide those just as they would when logging into OpenProject.  * No extra logic for token management necessary.  On the other hand using **API keys** has some advantages too, which is why we went for that:  * If compromised while saved on an insecure client the user only has to regenerate the API key instead of changing their password, too.  * They are naturally long and random which makes them invulnerable to dictionary attacks and harder to crack in general.  Most importantly users may not actually have a password to begin with. Specifically when they have registered through an OpenID Connect provider.  ## Cross-Origin Resource Sharing (CORS)  By default, the OpenProject API is _not_ responding with any CORS headers. If you want to allow cross-domain AJAX calls against your OpenProject instance, you need to enable CORS headers being returned.  Please see [our API settings documentation](https://www.openproject.org/docs/system-admin-guide/api-and-webhooks/) on how to selectively enable CORS.  ## Allowed HTTP methods  - `GET` - Get a single resource or collection of resources  - `POST` - Create a new resource or perform  - `PATCH` - Update a resource  - `DELETE` - Delete a resource  ## Compression  Responses are compressed if requested by the client. Currently [gzip](https://www.gzip.org/) and [deflate](https://tools.ietf.org/html/rfc1951) are supported. The client signals the desired compression by setting the [`Accept-Encoding` header](https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.3). If no `Accept-Encoding` header is send, `Accept-Encoding: identity` is assumed which will result in the API responding uncompressed.

    The version of the OpenAPI document: 3
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "1.0.0"

# Define package exports
__all__ = [
    "ActionsCapabilitiesApi",
    "ActivitiesApi",
    "AttachmentsApi",
    "BudgetsApi",
    "CategoriesApi",
    "CollectionsApi",
    "ConfigurationApi",
    "CustomOptionsApi",
    "CustomActionsApi",
    "DocumentsApi",
    "EmojiReactionsApi",
    "FavoritesApi",
    "FileLinksApi",
    "FileLinksApi",
    "FormsApi",
    "GridsApi",
    "GroupsApi",
    "HelpTextsApi",
    "MeetingsApi",
    "MembershipsApi",
    "NewsApi",
    "NotificationsApi",
    "OAuth2Api",
    "PortfoliosApi",
    "PostsApi",
    "PreviewingApi",
    "PrincipalsApi",
    "PrioritiesApi",
    "ProgramsApi",
    "ProjectPhaseDefinitionsApi",
    "ProjectPhasesApi",
    "ProjectsApi",
    "QueriesApi",
    "QueryColumnsApi",
    "QueryFilterInstanceSchemaApi",
    "QueryFiltersApi",
    "QueryOperatorsApi",
    "QuerySortBysApi",
    "RelationsApi",
    "RemindersApi",
    "RevisionsApi",
    "RolesApi",
    "RootApi",
    "SchemasApi",
    "StatusesApi",
    "TimeEntriesApi",
    "TimeEntriesApi",
    "TimeEntryActivitiesApi",
    "TypesApi",
    "UserPreferencesApi",
    "UsersApi",
    "ValuesPropertyApi",
    "VersionsApi",
    "ViewsApi",
    "WikiPagesApi",
    "WorkPackagesApi",
    "WorkPackagesApi",
    "WorkScheduleApi",
    "WorkspaceApi",
    "WorkspacesApi",
    "DefaultApi",
    "ApiResponse",
    "ApiClient",
    "Configuration",
    "OpenApiException",
    "ApiTypeError",
    "ApiValueError",
    "ApiKeyError",
    "ApiAttributeError",
    "ApiException",
    "ActivityCommentWriteModel",
    "ActivityCommentWriteModelComment",
    "ActivityModel",
    "ActivityModelEmbedded",
    "ActivityModelLinks",
    "AddWatcherRequest",
    "AttachmentModel",
    "AttachmentModelDigest",
    "AttachmentModelLinks",
    "AttachmentsModel",
    "AttachmentsModelAllOfEmbedded",
    "AttachmentsModelAllOfEmbeddedElements",
    "AttachmentsModelAllOfLinks",
    "AvailableAssigneesModel",
    "AvailableAssigneesModelAllOfEmbedded",
    "AvailableAssigneesModelAllOfEmbeddedElements",
    "AvailableAssigneesModelAllOfLinks",
    "BudgetModel",
    "BudgetModelLinks",
    "CategoriesByWorkspaceModel",
    "CategoriesByWorkspaceModelAllOfEmbedded",
    "CategoriesByWorkspaceModelAllOfEmbeddedElements",
    "CategoriesByWorkspaceModelAllOfLinks",
    "CategoryModel",
    "CategoryModelLinks",
    "CollectionLinks",
    "CollectionModel",
    "ConfigurationModel",
    "CreateViewsRequest",
    "CreateViewsRequestLinks",
    "CreateViewsRequestLinksQuery",
    "CreateWorkPackageReminderRequest",
    "CustomActionModel",
    "CustomActionModelLinks",
    "CustomOptionModel",
    "CustomOptionModelLinks",
    "DayCollectionModel",
    "DayCollectionModelAllOfEmbedded",
    "DayCollectionModelAllOfLinks",
    "DayModel",
    "DayModelLinks",
    "DocumentModel",
    "DocumentModelLinks",
    "EmojiReactionModel",
    "EmojiReactionModelLinks",
    "EmojiReactionsModel",
    "EmojiReactionsModelEmbedded",
    "EmojiReactionsModelLinks",
    "ErrorResponse",
    "ErrorResponseEmbedded",
    "ErrorResponseEmbeddedDetails",
    "ExecuteCustomActionRequest",
    "ExecuteCustomActionRequestLinks",
    "ExecuteCustomActionRequestLinksWorkPackage",
    "FileLinkCollectionReadModel",
    "FileLinkCollectionReadModelAllOfEmbedded",
    "FileLinkCollectionReadModelAllOfLinks",
    "FileLinkCollectionWriteModel",
    "FileLinkCollectionWriteModelEmbedded",
    "FileLinkOriginDataModel",
    "FileLinkReadModel",
    "FileLinkReadModelEmbedded",
    "FileLinkReadModelLinks",
    "FileLinkWriteModel",
    "FileLinkWriteModelLinks",
    "FileLinkWriteModelLinksOneOf",
    "FileLinkWriteModelLinksOneOf1",
    "FileUploadFormMetadata",
    "Formattable",
    "GridCollectionModel",
    "GridCollectionModelAllOfEmbedded",
    "GridReadModel",
    "GridReadModelLinks",
    "GridWidgetModel",
    "GridWriteModel",
    "GridWriteModelLinks",
    "GroupCollectionModel",
    "GroupCollectionModelAllOfEmbedded",
    "GroupCollectionModelAllOfLinks",
    "GroupModel",
    "GroupModelAllOfEmbedded",
    "GroupModelAllOfLinks",
    "GroupModelAllOfLinksMembers",
    "GroupWriteModel",
    "GroupWriteModelLinks",
    "HelpTextCollectionModel",
    "HelpTextCollectionModelAllOfEmbedded",
    "HelpTextCollectionModelAllOfLinks",
    "HelpTextModel",
    "HelpTextModelLinks",
    "HierarchyItemCollectionModel",
    "HierarchyItemCollectionModelAllOfEmbedded",
    "HierarchyItemCollectionModelAllOfLinks",
    "HierarchyItemReadModel",
    "HierarchyItemReadModelLinks",
    "Link",
    "ListAvailableParentProjectCandidatesModel",
    "ListAvailableParentProjectCandidatesModelAllOfEmbedded",
    "ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements",
    "ListAvailableParentProjectCandidatesModelAllOfLinks",
    "ListReminders200Response",
    "ListReminders200ResponseEmbedded",
    "MeetingModel",
    "MeetingModelLinks",
    "MembershipCollectionModel",
    "MembershipCollectionModelAllOfEmbedded",
    "MembershipFormModel",
    "MembershipFormModelEmbedded",
    "MembershipFormModelEmbeddedValidationError",
    "MembershipFormModelLinks",
    "MembershipReadModel",
    "MembershipReadModelEmbedded",
    "MembershipReadModelEmbeddedPrincipal",
    "MembershipReadModelEmbeddedProject",
    "MembershipReadModelLinks",
    "MembershipSchemaModel",
    "MembershipWriteModel",
    "MembershipWriteModelLinks",
    "MembershipWriteModelMeta",
    "NewsCreateModel",
    "NewsCreateModelLinks",
    "NewsModel",
    "NewsModelLinks",
    "NonWorkingDayCollectionModel",
    "NonWorkingDayCollectionModelAllOfEmbedded",
    "NonWorkingDayCollectionModelAllOfLinks",
    "NonWorkingDayModel",
    "NonWorkingDayModelLinks",
    "NotificationCollectionModel",
    "NotificationCollectionModelAllOfEmbedded",
    "NotificationCollectionModelAllOfLinks",
    "NotificationModel",
    "NotificationModelEmbedded",
    "NotificationModelLinks",
    "OAuthApplicationReadModel",
    "OAuthApplicationReadModelLinks",
    "OAuthClientCredentialsReadModel",
    "OAuthClientCredentialsReadModelLinks",
    "OAuthClientCredentialsWriteModel",
    "OffsetPaginatedCollectionLinks",
    "OffsetPaginatedCollectionModel",
    "PaginatedCollectionModel",
    "PaginatedCollectionModelAllOfLinks",
    "PlaceholderUserCollectionModel",
    "PlaceholderUserCollectionModelAllOfEmbedded",
    "PlaceholderUserCollectionModelAllOfLinks",
    "PlaceholderUserCreateModel",
    "PlaceholderUserModel",
    "PlaceholderUserModelAllOfLinks",
    "PortfolioCollectionModel",
    "PortfolioCollectionModelAllOfEmbedded",
    "PortfolioCollectionModelAllOfLinks",
    "PortfolioModel",
    "PortfolioModelAllOfLinks",
    "PortfolioModelAllOfLinksAncestors",
    "PortfolioModelAllOfLinksStorages",
    "PostModel",
    "PostModelLinks",
    "PrincipalCollectionModel",
    "PrincipalCollectionModelAllOfEmbedded",
    "PrincipalCollectionModelAllOfEmbeddedElements",
    "PrincipalModel",
    "PrincipalModelLinks",
    "PriorityCollectionModel",
    "PriorityCollectionModelAllOfEmbedded",
    "PriorityCollectionModelAllOfLinks",
    "PriorityCollectionModelAllOfLinksSelf",
    "PriorityModel",
    "PriorityModelLinks",
    "ProgramCollectionModel",
    "ProgramCollectionModelAllOfEmbedded",
    "ProgramCollectionModelAllOfLinks",
    "ProgramModel",
    "ProgramModelAllOfLinks",
    "ProgramModelAllOfLinksAncestors",
    "ProgramModelAllOfLinksStorages",
    "ProjectCollectionModel",
    "ProjectCollectionModelAllOfEmbedded",
    "ProjectCollectionModelAllOfLinks",
    "ProjectConfigurationModel",
    "ProjectModel",
    "ProjectModelAllOfLinks",
    "ProjectModelAllOfLinksAncestors",
    "ProjectModelAllOfLinksStorages",
    "ProjectPhaseDefinitionCollectionModel",
    "ProjectPhaseDefinitionCollectionModelAllOfEmbedded",
    "ProjectPhaseDefinitionCollectionModelAllOfLinks",
    "ProjectPhaseDefinitionModel",
    "ProjectPhaseDefinitionModelLinks",
    "ProjectPhaseModel",
    "ProjectPhaseModelLinks",
    "ProjectStorageCollectionModel",
    "ProjectStorageCollectionModelAllOfEmbedded",
    "ProjectStorageCollectionModelAllOfLinks",
    "ProjectStorageModel",
    "ProjectStorageModelLinks",
    "QueryColumnModel",
    "QueryCreateForm",
    "QueryFilterInstanceModel",
    "QueryFilterInstanceModelLinks",
    "QueryFilterInstanceSchemaModel",
    "QueryFilterInstanceSchemaModelLinks",
    "QueryFilterModel",
    "QueryModel",
    "QueryModelLinks",
    "QueryOperatorModel",
    "QuerySortByModel",
    "QueryUpdateForm",
    "RelationCollectionModel",
    "RelationCollectionModelAllOfEmbedded",
    "RelationCollectionModelAllOfLinks",
    "RelationReadModel",
    "RelationReadModelEmbedded",
    "RelationReadModelLinks",
    "RelationWriteModel",
    "RelationWriteModelLinks",
    "ReminderModel",
    "ReminderModelLinks",
    "RevisionModel",
    "RevisionModelLinks",
    "RoleModel",
    "RoleModelLinks",
    "RootModel",
    "RootModelLinks",
    "SchemaModel",
    "SchemaModelLinks",
    "SchemaPropertyModel",
    "ShowOrValidateFormRequest",
    "StatusCollectionModel",
    "StatusCollectionModelAllOfEmbedded",
    "StatusModel",
    "StatusModelLinks",
    "StorageCollectionModel",
    "StorageCollectionModelAllOfEmbedded",
    "StorageCollectionModelAllOfLinks",
    "StorageFileModel",
    "StorageFileModelAllOfLinks",
    "StorageFileUploadLinkModel",
    "StorageFileUploadLinkModelLinks",
    "StorageFileUploadPreparationModel",
    "StorageFilesModel",
    "StorageFolderWriteModel",
    "StorageReadModel",
    "StorageReadModelEmbedded",
    "StorageReadModelLinks",
    "StorageWriteModel",
    "StorageWriteModelLinks",
    "TimeEntryActivityModel",
    "TimeEntryActivityModelEmbedded",
    "TimeEntryActivityModelLinks",
    "TimeEntryCollectionModel",
    "TimeEntryCollectionModelAllOfEmbedded",
    "TimeEntryCollectionModelAllOfLinks",
    "TimeEntryModel",
    "TimeEntryModelAllOfLinks",
    "ToggleActivityEmojiReactionRequest",
    "TypeModel",
    "TypeModelLinks",
    "TypesByWorkspaceModel",
    "TypesByWorkspaceModelAllOfEmbedded",
    "TypesByWorkspaceModelAllOfEmbeddedElements",
    "TypesByWorkspaceModelAllOfLinks",
    "UpdateDocumentRequest",
    "UpdateDocumentRequestDescription",
    "UpdateReminderRequest",
    "UpdateUserPreferencesRequest",
    "UserCollectionModel",
    "UserCollectionModelAllOfEmbedded",
    "UserCollectionModelAllOfLinks",
    "UserCreateModel",
    "UserModel",
    "UserModelAllOfLinks",
    "ValuesPropertyModel",
    "ValuesPropertyModelLinks",
    "VersionCollectionModel",
    "VersionCollectionModelAllOfEmbedded",
    "VersionCollectionModelAllOfLinks",
    "VersionReadModel",
    "VersionReadModelAllOfLinks",
    "VersionWriteModel",
    "VersionWriteModelAllOfLinks",
    "VersionsByWorkspaceModel",
    "VersionsByWorkspaceModelAllOfEmbedded",
    "VersionsByWorkspaceModelAllOfEmbeddedElements",
    "VersionsByWorkspaceModelAllOfLinks",
    "WatchersModel",
    "WatchersModelAllOfEmbedded",
    "WatchersModelAllOfEmbeddedElements",
    "WatchersModelAllOfLinks",
    "WeekDayCollectionModel",
    "WeekDayCollectionModelAllOfEmbedded",
    "WeekDayCollectionModelAllOfLinks",
    "WeekDayCollectionWriteModel",
    "WeekDayCollectionWriteModelEmbedded",
    "WeekDayCollectionWriteModelEmbeddedElementsInner",
    "WeekDayModel",
    "WeekDaySelfLinkModel",
    "WeekDayWriteModel",
    "WikiPageModel",
    "WikiPageModelLinks",
    "WorkPackageFormModel",
    "WorkPackageFormModelEmbedded",
    "WorkPackageFormModelLinks",
    "WorkPackageModel",
    "WorkPackageModelAllOfLinks",
    "WorkPackageModelAllOfLinksAncestors",
    "WorkPackageModelAllOfLinksChildren",
    "WorkPackageModelAllOfLinksCustomActions",
    "WorkPackagePatchModel",
    "WorkPackageSchemaModel",
    "WorkPackageSchemaModelLinks",
    "WorkPackageWriteModel",
    "WorkPackageWriteModelLinks",
    "WorkPackageWriteModelMeta",
    "WorkPackagesModel",
    "WorkPackagesModelAllOfEmbedded",
    "WorkPackagesModelAllOfLinks",
    "WorkspaceCollectionModel",
    "WorkspaceCollectionModelAllOfEmbedded",
    "WorkspaceCollectionModelAllOfEmbeddedElements",
    "WorkspaceCollectionModelAllOfLinks",
    "WorkspacesSchemaModel",
    "WorkspacesSchemaModelAttributeGroupsInner",
    "WorkspacesSchemaModelLinks",
    "WorkspacesSchemaModelLinksSelf",
]

# import apis into sdk package
from auto_slopp.openproject.openapi_client.api.actions_capabilities_api import ActionsCapabilitiesApi as ActionsCapabilitiesApi
from auto_slopp.openproject.openapi_client.api.activities_api import ActivitiesApi as ActivitiesApi
from auto_slopp.openproject.openapi_client.api.attachments_api import AttachmentsApi as AttachmentsApi
from auto_slopp.openproject.openapi_client.api.budgets_api import BudgetsApi as BudgetsApi
from auto_slopp.openproject.openapi_client.api.categories_api import CategoriesApi as CategoriesApi
from auto_slopp.openproject.openapi_client.api.collections_api import CollectionsApi as CollectionsApi
from auto_slopp.openproject.openapi_client.api.configuration_api import ConfigurationApi as ConfigurationApi
from auto_slopp.openproject.openapi_client.api.custom_options_api import CustomOptionsApi as CustomOptionsApi
from auto_slopp.openproject.openapi_client.api.custom_actions_api import CustomActionsApi as CustomActionsApi
from auto_slopp.openproject.openapi_client.api.documents_api import DocumentsApi as DocumentsApi
from auto_slopp.openproject.openapi_client.api.emoji_reactions_api import EmojiReactionsApi as EmojiReactionsApi
from auto_slopp.openproject.openapi_client.api.favorites_api import FavoritesApi as FavoritesApi
from auto_slopp.openproject.openapi_client.api.file_links_api import FileLinksApi as FileLinksApi
from auto_slopp.openproject.openapi_client.api.file_links_api import FileLinksApi as FileLinksApi
from auto_slopp.openproject.openapi_client.api.forms_api import FormsApi as FormsApi
from auto_slopp.openproject.openapi_client.api.grids_api import GridsApi as GridsApi
from auto_slopp.openproject.openapi_client.api.groups_api import GroupsApi as GroupsApi
from auto_slopp.openproject.openapi_client.api.help_texts_api import HelpTextsApi as HelpTextsApi
from auto_slopp.openproject.openapi_client.api.meetings_api import MeetingsApi as MeetingsApi
from auto_slopp.openproject.openapi_client.api.memberships_api import MembershipsApi as MembershipsApi
from auto_slopp.openproject.openapi_client.api.news_api import NewsApi as NewsApi
from auto_slopp.openproject.openapi_client.api.notifications_api import NotificationsApi as NotificationsApi
from auto_slopp.openproject.openapi_client.api.o_auth2_api import OAuth2Api as OAuth2Api
from auto_slopp.openproject.openapi_client.api.portfolios_api import PortfoliosApi as PortfoliosApi
from auto_slopp.openproject.openapi_client.api.posts_api import PostsApi as PostsApi
from auto_slopp.openproject.openapi_client.api.previewing_api import PreviewingApi as PreviewingApi
from auto_slopp.openproject.openapi_client.api.principals_api import PrincipalsApi as PrincipalsApi
from auto_slopp.openproject.openapi_client.api.priorities_api import PrioritiesApi as PrioritiesApi
from auto_slopp.openproject.openapi_client.api.programs_api import ProgramsApi as ProgramsApi
from auto_slopp.openproject.openapi_client.api.project_phase_definitions_api import ProjectPhaseDefinitionsApi as ProjectPhaseDefinitionsApi
from auto_slopp.openproject.openapi_client.api.project_phases_api import ProjectPhasesApi as ProjectPhasesApi
from auto_slopp.openproject.openapi_client.api.projects_api import ProjectsApi as ProjectsApi
from auto_slopp.openproject.openapi_client.api.queries_api import QueriesApi as QueriesApi
from auto_slopp.openproject.openapi_client.api.query_columns_api import QueryColumnsApi as QueryColumnsApi
from auto_slopp.openproject.openapi_client.api.query_filter_instance_schema_api import QueryFilterInstanceSchemaApi as QueryFilterInstanceSchemaApi
from auto_slopp.openproject.openapi_client.api.query_filters_api import QueryFiltersApi as QueryFiltersApi
from auto_slopp.openproject.openapi_client.api.query_operators_api import QueryOperatorsApi as QueryOperatorsApi
from auto_slopp.openproject.openapi_client.api.query_sort_bys_api import QuerySortBysApi as QuerySortBysApi
from auto_slopp.openproject.openapi_client.api.relations_api import RelationsApi as RelationsApi
from auto_slopp.openproject.openapi_client.api.reminders_api import RemindersApi as RemindersApi
from auto_slopp.openproject.openapi_client.api.revisions_api import RevisionsApi as RevisionsApi
from auto_slopp.openproject.openapi_client.api.roles_api import RolesApi as RolesApi
from auto_slopp.openproject.openapi_client.api.root_api import RootApi as RootApi
from auto_slopp.openproject.openapi_client.api.schemas_api import SchemasApi as SchemasApi
from auto_slopp.openproject.openapi_client.api.statuses_api import StatusesApi as StatusesApi
from auto_slopp.openproject.openapi_client.api.time_entries_api import TimeEntriesApi as TimeEntriesApi
from auto_slopp.openproject.openapi_client.api.time_entries_api import TimeEntriesApi as TimeEntriesApi
from auto_slopp.openproject.openapi_client.api.time_entry_activities_api import TimeEntryActivitiesApi as TimeEntryActivitiesApi
from auto_slopp.openproject.openapi_client.api.types_api import TypesApi as TypesApi
from auto_slopp.openproject.openapi_client.api.user_preferences_api import UserPreferencesApi as UserPreferencesApi
from auto_slopp.openproject.openapi_client.api.users_api import UsersApi as UsersApi
from auto_slopp.openproject.openapi_client.api.values_property_api import ValuesPropertyApi as ValuesPropertyApi
from auto_slopp.openproject.openapi_client.api.versions_api import VersionsApi as VersionsApi
from auto_slopp.openproject.openapi_client.api.views_api import ViewsApi as ViewsApi
from auto_slopp.openproject.openapi_client.api.wiki_pages_api import WikiPagesApi as WikiPagesApi
from auto_slopp.openproject.openapi_client.api.work_packages_api import WorkPackagesApi as WorkPackagesApi
from auto_slopp.openproject.openapi_client.api.work_packages_api import WorkPackagesApi as WorkPackagesApi
from auto_slopp.openproject.openapi_client.api.work_schedule_api import WorkScheduleApi as WorkScheduleApi
from auto_slopp.openproject.openapi_client.api.workspace_api import WorkspaceApi as WorkspaceApi
from auto_slopp.openproject.openapi_client.api.workspaces_api import WorkspacesApi as WorkspacesApi
from auto_slopp.openproject.openapi_client.api.default_api import DefaultApi as DefaultApi

# import ApiClient
from auto_slopp.openproject.openapi_client.api_response import ApiResponse as ApiResponse
from auto_slopp.openproject.openapi_client.api_client import ApiClient as ApiClient
from auto_slopp.openproject.openapi_client.configuration import Configuration as Configuration
from auto_slopp.openproject.openapi_client.exceptions import OpenApiException as OpenApiException
from auto_slopp.openproject.openapi_client.exceptions import ApiTypeError as ApiTypeError
from auto_slopp.openproject.openapi_client.exceptions import ApiValueError as ApiValueError
from auto_slopp.openproject.openapi_client.exceptions import ApiKeyError as ApiKeyError
from auto_slopp.openproject.openapi_client.exceptions import ApiAttributeError as ApiAttributeError
from auto_slopp.openproject.openapi_client.exceptions import ApiException as ApiException

# import models into sdk package
from auto_slopp.openproject.openapi_client.models.activity_comment_write_model import ActivityCommentWriteModel as ActivityCommentWriteModel
from auto_slopp.openproject.openapi_client.models.activity_comment_write_model_comment import ActivityCommentWriteModelComment as ActivityCommentWriteModelComment
from auto_slopp.openproject.openapi_client.models.activity_model import ActivityModel as ActivityModel
from auto_slopp.openproject.openapi_client.models.activity_model_embedded import ActivityModelEmbedded as ActivityModelEmbedded
from auto_slopp.openproject.openapi_client.models.activity_model_links import ActivityModelLinks as ActivityModelLinks
from auto_slopp.openproject.openapi_client.models.add_watcher_request import AddWatcherRequest as AddWatcherRequest
from auto_slopp.openproject.openapi_client.models.attachment_model import AttachmentModel as AttachmentModel
from auto_slopp.openproject.openapi_client.models.attachment_model_digest import AttachmentModelDigest as AttachmentModelDigest
from auto_slopp.openproject.openapi_client.models.attachment_model_links import AttachmentModelLinks as AttachmentModelLinks
from auto_slopp.openproject.openapi_client.models.attachments_model import AttachmentsModel as AttachmentsModel
from auto_slopp.openproject.openapi_client.models.attachments_model_all_of_embedded import AttachmentsModelAllOfEmbedded as AttachmentsModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.attachments_model_all_of_embedded_elements import AttachmentsModelAllOfEmbeddedElements as AttachmentsModelAllOfEmbeddedElements
from auto_slopp.openproject.openapi_client.models.attachments_model_all_of_links import AttachmentsModelAllOfLinks as AttachmentsModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.available_assignees_model import AvailableAssigneesModel as AvailableAssigneesModel
from auto_slopp.openproject.openapi_client.models.available_assignees_model_all_of_embedded import AvailableAssigneesModelAllOfEmbedded as AvailableAssigneesModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.available_assignees_model_all_of_embedded_elements import AvailableAssigneesModelAllOfEmbeddedElements as AvailableAssigneesModelAllOfEmbeddedElements
from auto_slopp.openproject.openapi_client.models.available_assignees_model_all_of_links import AvailableAssigneesModelAllOfLinks as AvailableAssigneesModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.budget_model import BudgetModel as BudgetModel
from auto_slopp.openproject.openapi_client.models.budget_model_links import BudgetModelLinks as BudgetModelLinks
from auto_slopp.openproject.openapi_client.models.categories_by_workspace_model import CategoriesByWorkspaceModel as CategoriesByWorkspaceModel
from auto_slopp.openproject.openapi_client.models.categories_by_workspace_model_all_of_embedded import CategoriesByWorkspaceModelAllOfEmbedded as CategoriesByWorkspaceModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.categories_by_workspace_model_all_of_embedded_elements import CategoriesByWorkspaceModelAllOfEmbeddedElements as CategoriesByWorkspaceModelAllOfEmbeddedElements
from auto_slopp.openproject.openapi_client.models.categories_by_workspace_model_all_of_links import CategoriesByWorkspaceModelAllOfLinks as CategoriesByWorkspaceModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.category_model import CategoryModel as CategoryModel
from auto_slopp.openproject.openapi_client.models.category_model_links import CategoryModelLinks as CategoryModelLinks
from auto_slopp.openproject.openapi_client.models.collection_links import CollectionLinks as CollectionLinks
from auto_slopp.openproject.openapi_client.models.collection_model import CollectionModel as CollectionModel
from auto_slopp.openproject.openapi_client.models.configuration_model import ConfigurationModel as ConfigurationModel
from auto_slopp.openproject.openapi_client.models.create_views_request import CreateViewsRequest as CreateViewsRequest
from auto_slopp.openproject.openapi_client.models.create_views_request_links import CreateViewsRequestLinks as CreateViewsRequestLinks
from auto_slopp.openproject.openapi_client.models.create_views_request_links_query import CreateViewsRequestLinksQuery as CreateViewsRequestLinksQuery
from auto_slopp.openproject.openapi_client.models.create_work_package_reminder_request import CreateWorkPackageReminderRequest as CreateWorkPackageReminderRequest
from auto_slopp.openproject.openapi_client.models.custom_action_model import CustomActionModel as CustomActionModel
from auto_slopp.openproject.openapi_client.models.custom_action_model_links import CustomActionModelLinks as CustomActionModelLinks
from auto_slopp.openproject.openapi_client.models.custom_option_model import CustomOptionModel as CustomOptionModel
from auto_slopp.openproject.openapi_client.models.custom_option_model_links import CustomOptionModelLinks as CustomOptionModelLinks
from auto_slopp.openproject.openapi_client.models.day_collection_model import DayCollectionModel as DayCollectionModel
from auto_slopp.openproject.openapi_client.models.day_collection_model_all_of_embedded import DayCollectionModelAllOfEmbedded as DayCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.day_collection_model_all_of_links import DayCollectionModelAllOfLinks as DayCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.day_model import DayModel as DayModel
from auto_slopp.openproject.openapi_client.models.day_model_links import DayModelLinks as DayModelLinks
from auto_slopp.openproject.openapi_client.models.document_model import DocumentModel as DocumentModel
from auto_slopp.openproject.openapi_client.models.document_model_links import DocumentModelLinks as DocumentModelLinks
from auto_slopp.openproject.openapi_client.models.emoji_reaction_model import EmojiReactionModel as EmojiReactionModel
from auto_slopp.openproject.openapi_client.models.emoji_reaction_model_links import EmojiReactionModelLinks as EmojiReactionModelLinks
from auto_slopp.openproject.openapi_client.models.emoji_reactions_model import EmojiReactionsModel as EmojiReactionsModel
from auto_slopp.openproject.openapi_client.models.emoji_reactions_model_embedded import EmojiReactionsModelEmbedded as EmojiReactionsModelEmbedded
from auto_slopp.openproject.openapi_client.models.emoji_reactions_model_links import EmojiReactionsModelLinks as EmojiReactionsModelLinks
from auto_slopp.openproject.openapi_client.models.error_response import ErrorResponse as ErrorResponse
from auto_slopp.openproject.openapi_client.models.error_response_embedded import ErrorResponseEmbedded as ErrorResponseEmbedded
from auto_slopp.openproject.openapi_client.models.error_response_embedded_details import ErrorResponseEmbeddedDetails as ErrorResponseEmbeddedDetails
from auto_slopp.openproject.openapi_client.models.execute_custom_action_request import ExecuteCustomActionRequest as ExecuteCustomActionRequest
from auto_slopp.openproject.openapi_client.models.execute_custom_action_request_links import ExecuteCustomActionRequestLinks as ExecuteCustomActionRequestLinks
from auto_slopp.openproject.openapi_client.models.execute_custom_action_request_links_work_package import ExecuteCustomActionRequestLinksWorkPackage as ExecuteCustomActionRequestLinksWorkPackage
from auto_slopp.openproject.openapi_client.models.file_link_collection_read_model import FileLinkCollectionReadModel as FileLinkCollectionReadModel
from auto_slopp.openproject.openapi_client.models.file_link_collection_read_model_all_of_embedded import FileLinkCollectionReadModelAllOfEmbedded as FileLinkCollectionReadModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.file_link_collection_read_model_all_of_links import FileLinkCollectionReadModelAllOfLinks as FileLinkCollectionReadModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.file_link_collection_write_model import FileLinkCollectionWriteModel as FileLinkCollectionWriteModel
from auto_slopp.openproject.openapi_client.models.file_link_collection_write_model_embedded import FileLinkCollectionWriteModelEmbedded as FileLinkCollectionWriteModelEmbedded
from auto_slopp.openproject.openapi_client.models.file_link_origin_data_model import FileLinkOriginDataModel as FileLinkOriginDataModel
from auto_slopp.openproject.openapi_client.models.file_link_read_model import FileLinkReadModel as FileLinkReadModel
from auto_slopp.openproject.openapi_client.models.file_link_read_model_embedded import FileLinkReadModelEmbedded as FileLinkReadModelEmbedded
from auto_slopp.openproject.openapi_client.models.file_link_read_model_links import FileLinkReadModelLinks as FileLinkReadModelLinks
from auto_slopp.openproject.openapi_client.models.file_link_write_model import FileLinkWriteModel as FileLinkWriteModel
from auto_slopp.openproject.openapi_client.models.file_link_write_model_links import FileLinkWriteModelLinks as FileLinkWriteModelLinks
from auto_slopp.openproject.openapi_client.models.file_link_write_model_links_one_of import FileLinkWriteModelLinksOneOf as FileLinkWriteModelLinksOneOf
from auto_slopp.openproject.openapi_client.models.file_link_write_model_links_one_of1 import FileLinkWriteModelLinksOneOf1 as FileLinkWriteModelLinksOneOf1
from auto_slopp.openproject.openapi_client.models.file_upload_form_metadata import FileUploadFormMetadata as FileUploadFormMetadata
from auto_slopp.openproject.openapi_client.models.formattable import Formattable as Formattable
from auto_slopp.openproject.openapi_client.models.grid_collection_model import GridCollectionModel as GridCollectionModel
from auto_slopp.openproject.openapi_client.models.grid_collection_model_all_of_embedded import GridCollectionModelAllOfEmbedded as GridCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.grid_read_model import GridReadModel as GridReadModel
from auto_slopp.openproject.openapi_client.models.grid_read_model_links import GridReadModelLinks as GridReadModelLinks
from auto_slopp.openproject.openapi_client.models.grid_widget_model import GridWidgetModel as GridWidgetModel
from auto_slopp.openproject.openapi_client.models.grid_write_model import GridWriteModel as GridWriteModel
from auto_slopp.openproject.openapi_client.models.grid_write_model_links import GridWriteModelLinks as GridWriteModelLinks
from auto_slopp.openproject.openapi_client.models.group_collection_model import GroupCollectionModel as GroupCollectionModel
from auto_slopp.openproject.openapi_client.models.group_collection_model_all_of_embedded import GroupCollectionModelAllOfEmbedded as GroupCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.group_collection_model_all_of_links import GroupCollectionModelAllOfLinks as GroupCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.group_model import GroupModel as GroupModel
from auto_slopp.openproject.openapi_client.models.group_model_all_of_embedded import GroupModelAllOfEmbedded as GroupModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.group_model_all_of_links import GroupModelAllOfLinks as GroupModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.group_model_all_of_links_members import GroupModelAllOfLinksMembers as GroupModelAllOfLinksMembers
from auto_slopp.openproject.openapi_client.models.group_write_model import GroupWriteModel as GroupWriteModel
from auto_slopp.openproject.openapi_client.models.group_write_model_links import GroupWriteModelLinks as GroupWriteModelLinks
from auto_slopp.openproject.openapi_client.models.help_text_collection_model import HelpTextCollectionModel as HelpTextCollectionModel
from auto_slopp.openproject.openapi_client.models.help_text_collection_model_all_of_embedded import HelpTextCollectionModelAllOfEmbedded as HelpTextCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.help_text_collection_model_all_of_links import HelpTextCollectionModelAllOfLinks as HelpTextCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.help_text_model import HelpTextModel as HelpTextModel
from auto_slopp.openproject.openapi_client.models.help_text_model_links import HelpTextModelLinks as HelpTextModelLinks
from auto_slopp.openproject.openapi_client.models.hierarchy_item_collection_model import HierarchyItemCollectionModel as HierarchyItemCollectionModel
from auto_slopp.openproject.openapi_client.models.hierarchy_item_collection_model_all_of_embedded import HierarchyItemCollectionModelAllOfEmbedded as HierarchyItemCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.hierarchy_item_collection_model_all_of_links import HierarchyItemCollectionModelAllOfLinks as HierarchyItemCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.hierarchy_item_read_model import HierarchyItemReadModel as HierarchyItemReadModel
from auto_slopp.openproject.openapi_client.models.hierarchy_item_read_model_links import HierarchyItemReadModelLinks as HierarchyItemReadModelLinks
from auto_slopp.openproject.openapi_client.models.link import Link as Link
from auto_slopp.openproject.openapi_client.models.list_available_parent_project_candidates_model import ListAvailableParentProjectCandidatesModel as ListAvailableParentProjectCandidatesModel
from auto_slopp.openproject.openapi_client.models.list_available_parent_project_candidates_model_all_of_embedded import ListAvailableParentProjectCandidatesModelAllOfEmbedded as ListAvailableParentProjectCandidatesModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.list_available_parent_project_candidates_model_all_of_embedded_elements import ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements as ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements
from auto_slopp.openproject.openapi_client.models.list_available_parent_project_candidates_model_all_of_links import ListAvailableParentProjectCandidatesModelAllOfLinks as ListAvailableParentProjectCandidatesModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.list_reminders200_response import ListReminders200Response as ListReminders200Response
from auto_slopp.openproject.openapi_client.models.list_reminders200_response_embedded import ListReminders200ResponseEmbedded as ListReminders200ResponseEmbedded
from auto_slopp.openproject.openapi_client.models.meeting_model import MeetingModel as MeetingModel
from auto_slopp.openproject.openapi_client.models.meeting_model_links import MeetingModelLinks as MeetingModelLinks
from auto_slopp.openproject.openapi_client.models.membership_collection_model import MembershipCollectionModel as MembershipCollectionModel
from auto_slopp.openproject.openapi_client.models.membership_collection_model_all_of_embedded import MembershipCollectionModelAllOfEmbedded as MembershipCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.membership_form_model import MembershipFormModel as MembershipFormModel
from auto_slopp.openproject.openapi_client.models.membership_form_model_embedded import MembershipFormModelEmbedded as MembershipFormModelEmbedded
from auto_slopp.openproject.openapi_client.models.membership_form_model_embedded_validation_error import MembershipFormModelEmbeddedValidationError as MembershipFormModelEmbeddedValidationError
from auto_slopp.openproject.openapi_client.models.membership_form_model_links import MembershipFormModelLinks as MembershipFormModelLinks
from auto_slopp.openproject.openapi_client.models.membership_read_model import MembershipReadModel as MembershipReadModel
from auto_slopp.openproject.openapi_client.models.membership_read_model_embedded import MembershipReadModelEmbedded as MembershipReadModelEmbedded
from auto_slopp.openproject.openapi_client.models.membership_read_model_embedded_principal import MembershipReadModelEmbeddedPrincipal as MembershipReadModelEmbeddedPrincipal
from auto_slopp.openproject.openapi_client.models.membership_read_model_embedded_project import MembershipReadModelEmbeddedProject as MembershipReadModelEmbeddedProject
from auto_slopp.openproject.openapi_client.models.membership_read_model_links import MembershipReadModelLinks as MembershipReadModelLinks
from auto_slopp.openproject.openapi_client.models.membership_schema_model import MembershipSchemaModel as MembershipSchemaModel
from auto_slopp.openproject.openapi_client.models.membership_write_model import MembershipWriteModel as MembershipWriteModel
from auto_slopp.openproject.openapi_client.models.membership_write_model_links import MembershipWriteModelLinks as MembershipWriteModelLinks
from auto_slopp.openproject.openapi_client.models.membership_write_model_meta import MembershipWriteModelMeta as MembershipWriteModelMeta
from auto_slopp.openproject.openapi_client.models.news_create_model import NewsCreateModel as NewsCreateModel
from auto_slopp.openproject.openapi_client.models.news_create_model_links import NewsCreateModelLinks as NewsCreateModelLinks
from auto_slopp.openproject.openapi_client.models.news_model import NewsModel as NewsModel
from auto_slopp.openproject.openapi_client.models.news_model_links import NewsModelLinks as NewsModelLinks
from auto_slopp.openproject.openapi_client.models.non_working_day_collection_model import NonWorkingDayCollectionModel as NonWorkingDayCollectionModel
from auto_slopp.openproject.openapi_client.models.non_working_day_collection_model_all_of_embedded import NonWorkingDayCollectionModelAllOfEmbedded as NonWorkingDayCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.non_working_day_collection_model_all_of_links import NonWorkingDayCollectionModelAllOfLinks as NonWorkingDayCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.non_working_day_model import NonWorkingDayModel as NonWorkingDayModel
from auto_slopp.openproject.openapi_client.models.non_working_day_model_links import NonWorkingDayModelLinks as NonWorkingDayModelLinks
from auto_slopp.openproject.openapi_client.models.notification_collection_model import NotificationCollectionModel as NotificationCollectionModel
from auto_slopp.openproject.openapi_client.models.notification_collection_model_all_of_embedded import NotificationCollectionModelAllOfEmbedded as NotificationCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.notification_collection_model_all_of_links import NotificationCollectionModelAllOfLinks as NotificationCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.notification_model import NotificationModel as NotificationModel
from auto_slopp.openproject.openapi_client.models.notification_model_embedded import NotificationModelEmbedded as NotificationModelEmbedded
from auto_slopp.openproject.openapi_client.models.notification_model_links import NotificationModelLinks as NotificationModelLinks
from auto_slopp.openproject.openapi_client.models.o_auth_application_read_model import OAuthApplicationReadModel as OAuthApplicationReadModel
from auto_slopp.openproject.openapi_client.models.o_auth_application_read_model_links import OAuthApplicationReadModelLinks as OAuthApplicationReadModelLinks
from auto_slopp.openproject.openapi_client.models.o_auth_client_credentials_read_model import OAuthClientCredentialsReadModel as OAuthClientCredentialsReadModel
from auto_slopp.openproject.openapi_client.models.o_auth_client_credentials_read_model_links import OAuthClientCredentialsReadModelLinks as OAuthClientCredentialsReadModelLinks
from auto_slopp.openproject.openapi_client.models.o_auth_client_credentials_write_model import OAuthClientCredentialsWriteModel as OAuthClientCredentialsWriteModel
from auto_slopp.openproject.openapi_client.models.offset_paginated_collection_links import OffsetPaginatedCollectionLinks as OffsetPaginatedCollectionLinks
from auto_slopp.openproject.openapi_client.models.offset_paginated_collection_model import OffsetPaginatedCollectionModel as OffsetPaginatedCollectionModel
from auto_slopp.openproject.openapi_client.models.paginated_collection_model import PaginatedCollectionModel as PaginatedCollectionModel
from auto_slopp.openproject.openapi_client.models.paginated_collection_model_all_of_links import PaginatedCollectionModelAllOfLinks as PaginatedCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.placeholder_user_collection_model import PlaceholderUserCollectionModel as PlaceholderUserCollectionModel
from auto_slopp.openproject.openapi_client.models.placeholder_user_collection_model_all_of_embedded import PlaceholderUserCollectionModelAllOfEmbedded as PlaceholderUserCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.placeholder_user_collection_model_all_of_links import PlaceholderUserCollectionModelAllOfLinks as PlaceholderUserCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.placeholder_user_create_model import PlaceholderUserCreateModel as PlaceholderUserCreateModel
from auto_slopp.openproject.openapi_client.models.placeholder_user_model import PlaceholderUserModel as PlaceholderUserModel
from auto_slopp.openproject.openapi_client.models.placeholder_user_model_all_of_links import PlaceholderUserModelAllOfLinks as PlaceholderUserModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.portfolio_collection_model import PortfolioCollectionModel as PortfolioCollectionModel
from auto_slopp.openproject.openapi_client.models.portfolio_collection_model_all_of_embedded import PortfolioCollectionModelAllOfEmbedded as PortfolioCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.portfolio_collection_model_all_of_links import PortfolioCollectionModelAllOfLinks as PortfolioCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.portfolio_model import PortfolioModel as PortfolioModel
from auto_slopp.openproject.openapi_client.models.portfolio_model_all_of_links import PortfolioModelAllOfLinks as PortfolioModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.portfolio_model_all_of_links_ancestors import PortfolioModelAllOfLinksAncestors as PortfolioModelAllOfLinksAncestors
from auto_slopp.openproject.openapi_client.models.portfolio_model_all_of_links_storages import PortfolioModelAllOfLinksStorages as PortfolioModelAllOfLinksStorages
from auto_slopp.openproject.openapi_client.models.post_model import PostModel as PostModel
from auto_slopp.openproject.openapi_client.models.post_model_links import PostModelLinks as PostModelLinks
from auto_slopp.openproject.openapi_client.models.principal_collection_model import PrincipalCollectionModel as PrincipalCollectionModel
from auto_slopp.openproject.openapi_client.models.principal_collection_model_all_of_embedded import PrincipalCollectionModelAllOfEmbedded as PrincipalCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.principal_collection_model_all_of_embedded_elements import PrincipalCollectionModelAllOfEmbeddedElements as PrincipalCollectionModelAllOfEmbeddedElements
from auto_slopp.openproject.openapi_client.models.principal_model import PrincipalModel as PrincipalModel
from auto_slopp.openproject.openapi_client.models.principal_model_links import PrincipalModelLinks as PrincipalModelLinks
from auto_slopp.openproject.openapi_client.models.priority_collection_model import PriorityCollectionModel as PriorityCollectionModel
from auto_slopp.openproject.openapi_client.models.priority_collection_model_all_of_embedded import PriorityCollectionModelAllOfEmbedded as PriorityCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.priority_collection_model_all_of_links import PriorityCollectionModelAllOfLinks as PriorityCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.priority_collection_model_all_of_links_self import PriorityCollectionModelAllOfLinksSelf as PriorityCollectionModelAllOfLinksSelf
from auto_slopp.openproject.openapi_client.models.priority_model import PriorityModel as PriorityModel
from auto_slopp.openproject.openapi_client.models.priority_model_links import PriorityModelLinks as PriorityModelLinks
from auto_slopp.openproject.openapi_client.models.program_collection_model import ProgramCollectionModel as ProgramCollectionModel
from auto_slopp.openproject.openapi_client.models.program_collection_model_all_of_embedded import ProgramCollectionModelAllOfEmbedded as ProgramCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.program_collection_model_all_of_links import ProgramCollectionModelAllOfLinks as ProgramCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.program_model import ProgramModel as ProgramModel
from auto_slopp.openproject.openapi_client.models.program_model_all_of_links import ProgramModelAllOfLinks as ProgramModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.program_model_all_of_links_ancestors import ProgramModelAllOfLinksAncestors as ProgramModelAllOfLinksAncestors
from auto_slopp.openproject.openapi_client.models.program_model_all_of_links_storages import ProgramModelAllOfLinksStorages as ProgramModelAllOfLinksStorages
from auto_slopp.openproject.openapi_client.models.project_collection_model import ProjectCollectionModel as ProjectCollectionModel
from auto_slopp.openproject.openapi_client.models.project_collection_model_all_of_embedded import ProjectCollectionModelAllOfEmbedded as ProjectCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.project_collection_model_all_of_links import ProjectCollectionModelAllOfLinks as ProjectCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.project_configuration_model import ProjectConfigurationModel as ProjectConfigurationModel
from auto_slopp.openproject.openapi_client.models.project_model import ProjectModel as ProjectModel
from auto_slopp.openproject.openapi_client.models.project_model_all_of_links import ProjectModelAllOfLinks as ProjectModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.project_model_all_of_links_ancestors import ProjectModelAllOfLinksAncestors as ProjectModelAllOfLinksAncestors
from auto_slopp.openproject.openapi_client.models.project_model_all_of_links_storages import ProjectModelAllOfLinksStorages as ProjectModelAllOfLinksStorages
from auto_slopp.openproject.openapi_client.models.project_phase_definition_collection_model import ProjectPhaseDefinitionCollectionModel as ProjectPhaseDefinitionCollectionModel
from auto_slopp.openproject.openapi_client.models.project_phase_definition_collection_model_all_of_embedded import ProjectPhaseDefinitionCollectionModelAllOfEmbedded as ProjectPhaseDefinitionCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.project_phase_definition_collection_model_all_of_links import ProjectPhaseDefinitionCollectionModelAllOfLinks as ProjectPhaseDefinitionCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.project_phase_definition_model import ProjectPhaseDefinitionModel as ProjectPhaseDefinitionModel
from auto_slopp.openproject.openapi_client.models.project_phase_definition_model_links import ProjectPhaseDefinitionModelLinks as ProjectPhaseDefinitionModelLinks
from auto_slopp.openproject.openapi_client.models.project_phase_model import ProjectPhaseModel as ProjectPhaseModel
from auto_slopp.openproject.openapi_client.models.project_phase_model_links import ProjectPhaseModelLinks as ProjectPhaseModelLinks
from auto_slopp.openproject.openapi_client.models.project_storage_collection_model import ProjectStorageCollectionModel as ProjectStorageCollectionModel
from auto_slopp.openproject.openapi_client.models.project_storage_collection_model_all_of_embedded import ProjectStorageCollectionModelAllOfEmbedded as ProjectStorageCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.project_storage_collection_model_all_of_links import ProjectStorageCollectionModelAllOfLinks as ProjectStorageCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.project_storage_model import ProjectStorageModel as ProjectStorageModel
from auto_slopp.openproject.openapi_client.models.project_storage_model_links import ProjectStorageModelLinks as ProjectStorageModelLinks
from auto_slopp.openproject.openapi_client.models.query_column_model import QueryColumnModel as QueryColumnModel
from auto_slopp.openproject.openapi_client.models.query_create_form import QueryCreateForm as QueryCreateForm
from auto_slopp.openproject.openapi_client.models.query_filter_instance_model import QueryFilterInstanceModel as QueryFilterInstanceModel
from auto_slopp.openproject.openapi_client.models.query_filter_instance_model_links import QueryFilterInstanceModelLinks as QueryFilterInstanceModelLinks
from auto_slopp.openproject.openapi_client.models.query_filter_instance_schema_model import QueryFilterInstanceSchemaModel as QueryFilterInstanceSchemaModel
from auto_slopp.openproject.openapi_client.models.query_filter_instance_schema_model_links import QueryFilterInstanceSchemaModelLinks as QueryFilterInstanceSchemaModelLinks
from auto_slopp.openproject.openapi_client.models.query_filter_model import QueryFilterModel as QueryFilterModel
from auto_slopp.openproject.openapi_client.models.query_model import QueryModel as QueryModel
from auto_slopp.openproject.openapi_client.models.query_model_links import QueryModelLinks as QueryModelLinks
from auto_slopp.openproject.openapi_client.models.query_operator_model import QueryOperatorModel as QueryOperatorModel
from auto_slopp.openproject.openapi_client.models.query_sort_by_model import QuerySortByModel as QuerySortByModel
from auto_slopp.openproject.openapi_client.models.query_update_form import QueryUpdateForm as QueryUpdateForm
from auto_slopp.openproject.openapi_client.models.relation_collection_model import RelationCollectionModel as RelationCollectionModel
from auto_slopp.openproject.openapi_client.models.relation_collection_model_all_of_embedded import RelationCollectionModelAllOfEmbedded as RelationCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.relation_collection_model_all_of_links import RelationCollectionModelAllOfLinks as RelationCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.relation_read_model import RelationReadModel as RelationReadModel
from auto_slopp.openproject.openapi_client.models.relation_read_model_embedded import RelationReadModelEmbedded as RelationReadModelEmbedded
from auto_slopp.openproject.openapi_client.models.relation_read_model_links import RelationReadModelLinks as RelationReadModelLinks
from auto_slopp.openproject.openapi_client.models.relation_write_model import RelationWriteModel as RelationWriteModel
from auto_slopp.openproject.openapi_client.models.relation_write_model_links import RelationWriteModelLinks as RelationWriteModelLinks
from auto_slopp.openproject.openapi_client.models.reminder_model import ReminderModel as ReminderModel
from auto_slopp.openproject.openapi_client.models.reminder_model_links import ReminderModelLinks as ReminderModelLinks
from auto_slopp.openproject.openapi_client.models.revision_model import RevisionModel as RevisionModel
from auto_slopp.openproject.openapi_client.models.revision_model_links import RevisionModelLinks as RevisionModelLinks
from auto_slopp.openproject.openapi_client.models.role_model import RoleModel as RoleModel
from auto_slopp.openproject.openapi_client.models.role_model_links import RoleModelLinks as RoleModelLinks
from auto_slopp.openproject.openapi_client.models.root_model import RootModel as RootModel
from auto_slopp.openproject.openapi_client.models.root_model_links import RootModelLinks as RootModelLinks
from auto_slopp.openproject.openapi_client.models.schema_model import SchemaModel as SchemaModel
from auto_slopp.openproject.openapi_client.models.schema_model_links import SchemaModelLinks as SchemaModelLinks
from auto_slopp.openproject.openapi_client.models.schema_property_model import SchemaPropertyModel as SchemaPropertyModel
from auto_slopp.openproject.openapi_client.models.show_or_validate_form_request import ShowOrValidateFormRequest as ShowOrValidateFormRequest
from auto_slopp.openproject.openapi_client.models.status_collection_model import StatusCollectionModel as StatusCollectionModel
from auto_slopp.openproject.openapi_client.models.status_collection_model_all_of_embedded import StatusCollectionModelAllOfEmbedded as StatusCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.status_model import StatusModel as StatusModel
from auto_slopp.openproject.openapi_client.models.status_model_links import StatusModelLinks as StatusModelLinks
from auto_slopp.openproject.openapi_client.models.storage_collection_model import StorageCollectionModel as StorageCollectionModel
from auto_slopp.openproject.openapi_client.models.storage_collection_model_all_of_embedded import StorageCollectionModelAllOfEmbedded as StorageCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.storage_collection_model_all_of_links import StorageCollectionModelAllOfLinks as StorageCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.storage_file_model import StorageFileModel as StorageFileModel
from auto_slopp.openproject.openapi_client.models.storage_file_model_all_of_links import StorageFileModelAllOfLinks as StorageFileModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.storage_file_upload_link_model import StorageFileUploadLinkModel as StorageFileUploadLinkModel
from auto_slopp.openproject.openapi_client.models.storage_file_upload_link_model_links import StorageFileUploadLinkModelLinks as StorageFileUploadLinkModelLinks
from auto_slopp.openproject.openapi_client.models.storage_file_upload_preparation_model import StorageFileUploadPreparationModel as StorageFileUploadPreparationModel
from auto_slopp.openproject.openapi_client.models.storage_files_model import StorageFilesModel as StorageFilesModel
from auto_slopp.openproject.openapi_client.models.storage_folder_write_model import StorageFolderWriteModel as StorageFolderWriteModel
from auto_slopp.openproject.openapi_client.models.storage_read_model import StorageReadModel as StorageReadModel
from auto_slopp.openproject.openapi_client.models.storage_read_model_embedded import StorageReadModelEmbedded as StorageReadModelEmbedded
from auto_slopp.openproject.openapi_client.models.storage_read_model_links import StorageReadModelLinks as StorageReadModelLinks
from auto_slopp.openproject.openapi_client.models.storage_write_model import StorageWriteModel as StorageWriteModel
from auto_slopp.openproject.openapi_client.models.storage_write_model_links import StorageWriteModelLinks as StorageWriteModelLinks
from auto_slopp.openproject.openapi_client.models.time_entry_activity_model import TimeEntryActivityModel as TimeEntryActivityModel
from auto_slopp.openproject.openapi_client.models.time_entry_activity_model_embedded import TimeEntryActivityModelEmbedded as TimeEntryActivityModelEmbedded
from auto_slopp.openproject.openapi_client.models.time_entry_activity_model_links import TimeEntryActivityModelLinks as TimeEntryActivityModelLinks
from auto_slopp.openproject.openapi_client.models.time_entry_collection_model import TimeEntryCollectionModel as TimeEntryCollectionModel
from auto_slopp.openproject.openapi_client.models.time_entry_collection_model_all_of_embedded import TimeEntryCollectionModelAllOfEmbedded as TimeEntryCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.time_entry_collection_model_all_of_links import TimeEntryCollectionModelAllOfLinks as TimeEntryCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.time_entry_model import TimeEntryModel as TimeEntryModel
from auto_slopp.openproject.openapi_client.models.time_entry_model_all_of_links import TimeEntryModelAllOfLinks as TimeEntryModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.toggle_activity_emoji_reaction_request import ToggleActivityEmojiReactionRequest as ToggleActivityEmojiReactionRequest
from auto_slopp.openproject.openapi_client.models.type_model import TypeModel as TypeModel
from auto_slopp.openproject.openapi_client.models.type_model_links import TypeModelLinks as TypeModelLinks
from auto_slopp.openproject.openapi_client.models.types_by_workspace_model import TypesByWorkspaceModel as TypesByWorkspaceModel
from auto_slopp.openproject.openapi_client.models.types_by_workspace_model_all_of_embedded import TypesByWorkspaceModelAllOfEmbedded as TypesByWorkspaceModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.types_by_workspace_model_all_of_embedded_elements import TypesByWorkspaceModelAllOfEmbeddedElements as TypesByWorkspaceModelAllOfEmbeddedElements
from auto_slopp.openproject.openapi_client.models.types_by_workspace_model_all_of_links import TypesByWorkspaceModelAllOfLinks as TypesByWorkspaceModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.update_document_request import UpdateDocumentRequest as UpdateDocumentRequest
from auto_slopp.openproject.openapi_client.models.update_document_request_description import UpdateDocumentRequestDescription as UpdateDocumentRequestDescription
from auto_slopp.openproject.openapi_client.models.update_reminder_request import UpdateReminderRequest as UpdateReminderRequest
from auto_slopp.openproject.openapi_client.models.update_user_preferences_request import UpdateUserPreferencesRequest as UpdateUserPreferencesRequest
from auto_slopp.openproject.openapi_client.models.user_collection_model import UserCollectionModel as UserCollectionModel
from auto_slopp.openproject.openapi_client.models.user_collection_model_all_of_embedded import UserCollectionModelAllOfEmbedded as UserCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.user_collection_model_all_of_links import UserCollectionModelAllOfLinks as UserCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.user_create_model import UserCreateModel as UserCreateModel
from auto_slopp.openproject.openapi_client.models.user_model import UserModel as UserModel
from auto_slopp.openproject.openapi_client.models.user_model_all_of_links import UserModelAllOfLinks as UserModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.values_property_model import ValuesPropertyModel as ValuesPropertyModel
from auto_slopp.openproject.openapi_client.models.values_property_model_links import ValuesPropertyModelLinks as ValuesPropertyModelLinks
from auto_slopp.openproject.openapi_client.models.version_collection_model import VersionCollectionModel as VersionCollectionModel
from auto_slopp.openproject.openapi_client.models.version_collection_model_all_of_embedded import VersionCollectionModelAllOfEmbedded as VersionCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.version_collection_model_all_of_links import VersionCollectionModelAllOfLinks as VersionCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.version_read_model import VersionReadModel as VersionReadModel
from auto_slopp.openproject.openapi_client.models.version_read_model_all_of_links import VersionReadModelAllOfLinks as VersionReadModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.version_write_model import VersionWriteModel as VersionWriteModel
from auto_slopp.openproject.openapi_client.models.version_write_model_all_of_links import VersionWriteModelAllOfLinks as VersionWriteModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.versions_by_workspace_model import VersionsByWorkspaceModel as VersionsByWorkspaceModel
from auto_slopp.openproject.openapi_client.models.versions_by_workspace_model_all_of_embedded import VersionsByWorkspaceModelAllOfEmbedded as VersionsByWorkspaceModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.versions_by_workspace_model_all_of_embedded_elements import VersionsByWorkspaceModelAllOfEmbeddedElements as VersionsByWorkspaceModelAllOfEmbeddedElements
from auto_slopp.openproject.openapi_client.models.versions_by_workspace_model_all_of_links import VersionsByWorkspaceModelAllOfLinks as VersionsByWorkspaceModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.watchers_model import WatchersModel as WatchersModel
from auto_slopp.openproject.openapi_client.models.watchers_model_all_of_embedded import WatchersModelAllOfEmbedded as WatchersModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.watchers_model_all_of_embedded_elements import WatchersModelAllOfEmbeddedElements as WatchersModelAllOfEmbeddedElements
from auto_slopp.openproject.openapi_client.models.watchers_model_all_of_links import WatchersModelAllOfLinks as WatchersModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.week_day_collection_model import WeekDayCollectionModel as WeekDayCollectionModel
from auto_slopp.openproject.openapi_client.models.week_day_collection_model_all_of_embedded import WeekDayCollectionModelAllOfEmbedded as WeekDayCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.week_day_collection_model_all_of_links import WeekDayCollectionModelAllOfLinks as WeekDayCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.week_day_collection_write_model import WeekDayCollectionWriteModel as WeekDayCollectionWriteModel
from auto_slopp.openproject.openapi_client.models.week_day_collection_write_model_embedded import WeekDayCollectionWriteModelEmbedded as WeekDayCollectionWriteModelEmbedded
from auto_slopp.openproject.openapi_client.models.week_day_collection_write_model_embedded_elements_inner import WeekDayCollectionWriteModelEmbeddedElementsInner as WeekDayCollectionWriteModelEmbeddedElementsInner
from auto_slopp.openproject.openapi_client.models.week_day_model import WeekDayModel as WeekDayModel
from auto_slopp.openproject.openapi_client.models.week_day_self_link_model import WeekDaySelfLinkModel as WeekDaySelfLinkModel
from auto_slopp.openproject.openapi_client.models.week_day_write_model import WeekDayWriteModel as WeekDayWriteModel
from auto_slopp.openproject.openapi_client.models.wiki_page_model import WikiPageModel as WikiPageModel
from auto_slopp.openproject.openapi_client.models.wiki_page_model_links import WikiPageModelLinks as WikiPageModelLinks
from auto_slopp.openproject.openapi_client.models.work_package_form_model import WorkPackageFormModel as WorkPackageFormModel
from auto_slopp.openproject.openapi_client.models.work_package_form_model_embedded import WorkPackageFormModelEmbedded as WorkPackageFormModelEmbedded
from auto_slopp.openproject.openapi_client.models.work_package_form_model_links import WorkPackageFormModelLinks as WorkPackageFormModelLinks
from auto_slopp.openproject.openapi_client.models.work_package_model import WorkPackageModel as WorkPackageModel
from auto_slopp.openproject.openapi_client.models.work_package_model_all_of_links import WorkPackageModelAllOfLinks as WorkPackageModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.work_package_model_all_of_links_ancestors import WorkPackageModelAllOfLinksAncestors as WorkPackageModelAllOfLinksAncestors
from auto_slopp.openproject.openapi_client.models.work_package_model_all_of_links_children import WorkPackageModelAllOfLinksChildren as WorkPackageModelAllOfLinksChildren
from auto_slopp.openproject.openapi_client.models.work_package_model_all_of_links_custom_actions import WorkPackageModelAllOfLinksCustomActions as WorkPackageModelAllOfLinksCustomActions
from auto_slopp.openproject.openapi_client.models.work_package_patch_model import WorkPackagePatchModel as WorkPackagePatchModel
from auto_slopp.openproject.openapi_client.models.work_package_schema_model import WorkPackageSchemaModel as WorkPackageSchemaModel
from auto_slopp.openproject.openapi_client.models.work_package_schema_model_links import WorkPackageSchemaModelLinks as WorkPackageSchemaModelLinks
from auto_slopp.openproject.openapi_client.models.work_package_write_model import WorkPackageWriteModel as WorkPackageWriteModel
from auto_slopp.openproject.openapi_client.models.work_package_write_model_links import WorkPackageWriteModelLinks as WorkPackageWriteModelLinks
from auto_slopp.openproject.openapi_client.models.work_package_write_model_meta import WorkPackageWriteModelMeta as WorkPackageWriteModelMeta
from auto_slopp.openproject.openapi_client.models.work_packages_model import WorkPackagesModel as WorkPackagesModel
from auto_slopp.openproject.openapi_client.models.work_packages_model_all_of_embedded import WorkPackagesModelAllOfEmbedded as WorkPackagesModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.work_packages_model_all_of_links import WorkPackagesModelAllOfLinks as WorkPackagesModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.workspace_collection_model import WorkspaceCollectionModel as WorkspaceCollectionModel
from auto_slopp.openproject.openapi_client.models.workspace_collection_model_all_of_embedded import WorkspaceCollectionModelAllOfEmbedded as WorkspaceCollectionModelAllOfEmbedded
from auto_slopp.openproject.openapi_client.models.workspace_collection_model_all_of_embedded_elements import WorkspaceCollectionModelAllOfEmbeddedElements as WorkspaceCollectionModelAllOfEmbeddedElements
from auto_slopp.openproject.openapi_client.models.workspace_collection_model_all_of_links import WorkspaceCollectionModelAllOfLinks as WorkspaceCollectionModelAllOfLinks
from auto_slopp.openproject.openapi_client.models.workspaces_schema_model import WorkspacesSchemaModel as WorkspacesSchemaModel
from auto_slopp.openproject.openapi_client.models.workspaces_schema_model_attribute_groups_inner import WorkspacesSchemaModelAttributeGroupsInner as WorkspacesSchemaModelAttributeGroupsInner
from auto_slopp.openproject.openapi_client.models.workspaces_schema_model_links import WorkspacesSchemaModelLinks as WorkspacesSchemaModelLinks
from auto_slopp.openproject.openapi_client.models.workspaces_schema_model_links_self import WorkspacesSchemaModelLinksSelf as WorkspacesSchemaModelLinksSelf

