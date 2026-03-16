# coding: utf-8

"""
    OpenProject API V3 (Stable)

    You're looking at the current **stable** documentation of the OpenProject APIv3. If you're interested in the current development version, please go to [github.com/opf](https://github.com/opf/openproject/tree/dev/docs/api/apiv3).  ## Introduction  The documentation for the APIv3 is written according to the [OpenAPI 3.1 Specification](https://swagger.io/specification/). You can either view the static version of this documentation on the [website](https://www.openproject.org/docs/api/introduction/) or the interactive version, rendered with [OpenAPI Explorer](https://github.com/Rhosys/openapi-explorer/blob/main/README.md), in your OpenProject installation under `/api/docs`. In the latter you can try out the various API endpoints directly interacting with our OpenProject data. Moreover you can access the specification source itself under `/api/v3/spec.json` and `/api/v3/spec.yml` (e.g. [here](https://community.openproject.org/api/v3/spec.yml)).  The APIv3 is a hypermedia REST API, a shorthand for \"Hypermedia As The Engine Of Application State\" (HATEOAS). This means that each endpoint of this API will have links to other resources or actions defined in the resulting body.  These related resources and actions for any given resource will be context sensitive. For example, only actions that the authenticated user can take are being rendered. This can be used to dynamically identify actions that the user might take for any given response.  As an example, if you fetch a work package through the [Work Package endpoint](https://www.openproject.org/docs/api/endpoints/work-packages/), the `update` link will only be present when the user you authenticated has been granted a permission to update the work package in the assigned project.  ## HAL+JSON  HAL is a simple format that gives a consistent and easy way to hyperlink between resources in your API. Read more in the following specification: [https://tools.ietf.org/html/draft-kelly-json-hal-08](https://tools.ietf.org/html/draft-kelly-json-hal-08)  **OpenProject API implementation of HAL+JSON format** enriches JSON and introduces a few meta properties:  - `_type` - specifies the type of the resource (e.g.: WorkPackage, Project) - `_links` - contains all related resource and action links available for the resource - `_embedded` - contains all embedded objects  HAL does not guarantee that embedded resources are embedded in their full representation, they might as well be partially represented (e.g. some properties can be left out). However in this API you have the guarantee that whenever a resource is **embedded**, it is embedded in its **full representation**.  ## API response structure  All API responses contain a single HAL+JSON object, even collections of objects are technically represented by a single HAL+JSON object that itself contains its members. More details on collections can be found in the [Collections Section](https://www.openproject.org/docs/api/collections/).  ## Authentication  The API supports the following authentication schemes:  * Session-based authentication * API tokens     * passed as Bearer token     * passed via Basic auth * OAuth 2.0     * using built-in authorization server     * using an external authorization server (RFC 9068)  Depending on the settings of the OpenProject instance many resources can be accessed without being authenticated. In case the instance requires authentication on all requests the client will receive an **HTTP 401** status code in response to any request.  Otherwise unauthenticated clients have all the permissions of the anonymous user.  ### Session-based authentication  This means you have to login to OpenProject via the Web-Interface to be authenticated in the API. This method is well-suited for clients acting within the browser, like the Angular-Client built into OpenProject.  In this case, you always need to pass the HTTP header `X-Requested-With \"XMLHttpRequest\"` for authentication.  ### API token as bearer token  Users can authenticate towards the API v3 using an API token as a bearer token.  For example:  ```shell API_KEY=opapi-2519132cdf62dcf5a66fd96394672079f9e9cad1 curl -H \"Authorization: Bearer $API_KEY\" https://community.openproject.org/api/v3/users/42 ```  Users can generate API tokens on their account page.  ### API token through Basic Auth  API tokens can also be used with basic auth, using the user name `apikey` (NOT your login) and the API token as the password.  For example:  ```shell API_KEY=opapi-2519132cdf62dcf5a66fd96394672079f9e9cad1 curl -u apikey:$API_KEY https://community.openproject.org/api/v3/users/42 ```  ### OAuth 2.0 authentication  OpenProject allows authentication and authorization with OAuth2 with *Authorization code flow*, as well as *Client credentials* operation modes.  To get started, you first need to register an application in the OpenProject OAuth administration section of your installation. This will save an entry for your application with a client unique identifier (`client_id`) and an accompanying secret key (`client_secret`).  You can then use one the following guides to perform the supported OAuth 2.0 flows:  - [Authorization code flow](https://oauth.net/2/grant-types/authorization-code)  - [Authorization code flow with PKCE](https://doorkeeper.gitbook.io/guides/ruby-on-rails/pkce-flow), recommended for clients unable to keep the client_secret confidential  - [Client credentials](https://oauth.net/2/grant-types/client-credentials/) - Requires an application to be bound to an impersonating user for non-public access  ### OAuth 2.0 using an external authorization server  There is a possibility to use JSON Web Tokens (JWT) generated by an OIDC provider configured in OpenProject as a bearer token to do authenticated requests against the API. The following requirements must be met:  - OIDC provider must be configured in OpenProject with **jwks_uri** - JWT must be signed using RSA algorithm - JWT **iss** claim must be equal to OIDC provider **issuer** - JWT **aud** claim must contain the OpenProject **client ID** used at the OIDC provider - JWT **scope** claim must include a valid scope to access the desired API (e.g. `api_v3` for APIv3) - JWT must be actual (neither expired or too early to be used) - JWT must be passed in Authorization header like: `Authorization: Bearer {jwt}` - User from **sub** claim must be linked to OpenProject before (e.g. by logging in), otherwise it will be not authenticated  In more general terms, OpenProject should be compliant to [RFC 9068](https://www.rfc-editor.org/rfc/rfc9068) when validating access tokens.  ### Why not username and password?  The simplest way to do basic auth would be to use a user's username and password naturally. However, OpenProject already has supported API keys in the past for the API v2, though not through basic auth.  Using **username and password** directly would have some advantages:  * It is intuitive for the user who then just has to provide those just as they would when logging into OpenProject.  * No extra logic for token management necessary.  On the other hand using **API keys** has some advantages too, which is why we went for that:  * If compromised while saved on an insecure client the user only has to regenerate the API key instead of changing their password, too.  * They are naturally long and random which makes them invulnerable to dictionary attacks and harder to crack in general.  Most importantly users may not actually have a password to begin with. Specifically when they have registered through an OpenID Connect provider.  ## Cross-Origin Resource Sharing (CORS)  By default, the OpenProject API is _not_ responding with any CORS headers. If you want to allow cross-domain AJAX calls against your OpenProject instance, you need to enable CORS headers being returned.  Please see [our API settings documentation](https://www.openproject.org/docs/system-admin-guide/api-and-webhooks/) on how to selectively enable CORS.  ## Allowed HTTP methods  - `GET` - Get a single resource or collection of resources  - `POST` - Create a new resource or perform  - `PATCH` - Update a resource  - `DELETE` - Delete a resource  ## Compression  Responses are compressed if requested by the client. Currently [gzip](https://www.gzip.org/) and [deflate](https://tools.ietf.org/html/rfc1951) are supported. The client signals the desired compression by setting the [`Accept-Encoding` header](https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.3). If no `Accept-Encoding` header is send, `Accept-Encoding: identity` is assumed which will result in the API responding uncompressed.

    The version of the OpenAPI document: 3
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, ClassVar, Dict, List, Optional
from auto_slopp.openproject.openapi_client.models.link import Link
from auto_slopp.openproject.openapi_client.models.work_package_model_all_of_links_ancestors import WorkPackageModelAllOfLinksAncestors
from auto_slopp.openproject.openapi_client.models.work_package_model_all_of_links_children import WorkPackageModelAllOfLinksChildren
from auto_slopp.openproject.openapi_client.models.work_package_model_all_of_links_custom_actions import WorkPackageModelAllOfLinksCustomActions
from typing import Optional, Set
from typing_extensions import Self
from pydantic_core import to_jsonable_python

class WorkPackageModelAllOfLinks(BaseModel):
    """
    WorkPackageModelAllOfLinks
    """ # noqa: E501
    add_comment: Optional[Link] = Field(default=None, description="Post comment to WP  # Conditions  **Permission**: add work package notes", alias="addComment")
    add_relation: Optional[Link] = Field(default=None, description="Adds a relation to this work package.  # Conditions  **Permission**: manage wp relations", alias="addRelation")
    add_watcher: Optional[Link] = Field(default=None, description="Add any user to WP watchers  # Conditions  **Permission**: add watcher", alias="addWatcher")
    custom_actions: Optional[List[WorkPackageModelAllOfLinksCustomActions]] = Field(default=None, alias="customActions")
    preview_markup: Optional[Link] = Field(default=None, description="Post markup (in markdown) here to receive an HTML-rendered response", alias="previewMarkup")
    remove_watcher: Optional[Link] = Field(default=None, description="Remove any user from WP watchers  # Conditions  **Permission**: delete watcher", alias="removeWatcher")
    delete: Optional[Link] = Field(default=None, description="Delete this work package  # Conditions  **Permission**: delete_work_packages")
    log_time: Optional[Link] = Field(default=None, description="Create time entries on the work package  # Conditions  **Permission**: log_time or log_own_time", alias="logTime")
    move: Optional[Link] = Field(default=None, description="Link to page for moving this work package  # Conditions  **Permission**: move_work_packages")
    copy: Optional[Link] = Field(default=None, description="Link to page for copying this work package  # Conditions  **Permission**: add_work_packages")
    unwatch: Optional[Link] = Field(default=None, description="Remove current user from WP watchers  # Conditions  logged in; watching")
    update: Optional[Link] = Field(default=None, description="Form endpoint that aids in preparing and performing edits on a work package  # Conditions  **Permission**: edit work package")
    update_immediately: Optional[Link] = Field(default=None, description="Directly perform edits on a work package  # Conditions  **Permission**: edit work package", alias="updateImmediately")
    watch: Optional[Link] = Field(default=None, description="Add current user to WP watchers  # Conditions  logged in; not watching")
    var_self: Link = Field(description="This work package  **Resource**: WorkPackage", alias="self")
    var_schema: Link = Field(description="The schema of this work package  **Resource**: Schema", alias="schema")
    ancestors: List[WorkPackageModelAllOfLinksAncestors]
    attachments: Optional[Link] = Field(default=None, description="The files attached to this work package  **Resource**: Collection  # Conditions  - **Setting**: deactivate_work_package_attachments set to false in related workspace")
    add_attachment: Optional[Link] = Field(default=None, description="Attach a file to the work package  # Conditions  - **Permission**: edit work package", alias="addAttachment")
    prepare_attachment: Optional[Link] = Field(default=None, description="Attach a file to the work package  # Conditions  - **Setting**: direct uploads enabled", alias="prepareAttachment")
    author: Link = Field(description="The person that created the work package  **Resource**: User")
    assignee: Optional[Link] = Field(default=None, description="The person that is intended to work on the work package  **Resource**: User")
    available_watchers: Optional[Link] = Field(default=None, description="All users that can be added to the work package as watchers.  **Resource**: User  # Conditions  **Permission** add work package watchers", alias="availableWatchers")
    budget: Optional[Link] = Field(default=None, description="The budget this work package is associated to  **Resource**: Budget  # Conditions  **Permission** view cost objects")
    category: Optional[Link] = Field(default=None, description="The category of the work package  **Resource**: Category")
    children: Optional[List[WorkPackageModelAllOfLinksChildren]] = None
    add_file_link: Optional[Link] = Field(default=None, description="Add a file link to the work package  # Conditions  **Permission**: manage_file_links", alias="addFileLink")
    file_links: Optional[Link] = Field(default=None, description="Gets the file link collection of this work package  # Conditions  **Permission**: view_file_links", alias="fileLinks")
    parent: Optional[Link] = Field(default=None, description="Parent work package  **Resource**: WorkPackage")
    priority: Link = Field(description="The priority of the work package  **Resource**: Priority")
    project: Link = Field(description="The workspace to which the work package belongs  **Resource**: Workspace")
    project_phase: Optional[Link] = Field(default=None, description="The project phase to which the work package belongs  **Resource**: ProjectPhase", alias="projectPhase")
    project_phase_definition: Optional[Link] = Field(default=None, description="The definition of the project phase the work package belongs to  **Resource**: ProjectPhaseDefinition", alias="projectPhaseDefinition")
    responsible: Optional[Link] = Field(default=None, description="The person that is responsible for the overall outcome  **Resource**: User")
    relations: Optional[Link] = Field(default=None, description="Relations this work package is involved in  **Resource**: Relation  # Conditions  **Permission** view work packages")
    revisions: Optional[Link] = Field(default=None, description="Revisions that are referencing the work package  **Resource**: Revision  # Conditions  **Permission** view changesets")
    status: Link = Field(description="The current status of the work package  **Resource**: Status")
    time_entries: Optional[Link] = Field(default=None, description="All time entries logged on the work package. Please note that this is a link to an HTML resource for now and as such, the link is subject to change.  **Resource**: N/A  # Conditions  **Permission** view time entries", alias="timeEntries")
    type: Link = Field(description="The type of the work package  **Resource**: Type")
    version: Optional[Link] = Field(default=None, description="The version associated to the work package  **Resource**: Version")
    watchers: Optional[Link] = Field(default=None, description="All users that are currently watching this work package  **Resource**: Collection  # Conditions  **Permission** view work package watchers")
    __properties: ClassVar[List[str]] = ["addComment", "addRelation", "addWatcher", "customActions", "previewMarkup", "removeWatcher", "delete", "logTime", "move", "copy", "unwatch", "update", "updateImmediately", "watch", "self", "schema", "ancestors", "attachments", "addAttachment", "prepareAttachment", "author", "assignee", "availableWatchers", "budget", "category", "children", "addFileLink", "fileLinks", "parent", "priority", "project", "projectPhase", "projectPhaseDefinition", "responsible", "relations", "revisions", "status", "timeEntries", "type", "version", "watchers"]

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(to_jsonable_python(self.to_dict()))

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of WorkPackageModelAllOfLinks from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "add_comment",
            "add_relation",
            "add_watcher",
            "custom_actions",
            "preview_markup",
            "remove_watcher",
            "delete",
            "log_time",
            "move",
            "copy",
            "unwatch",
            "update",
            "update_immediately",
            "watch",
            "var_self",
            "var_schema",
            "ancestors",
            "add_attachment",
            "prepare_attachment",
            "author",
            "available_watchers",
            "children",
            "relations",
            "revisions",
            "time_entries",
            "watchers",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of add_comment
        if self.add_comment:
            _dict['addComment'] = self.add_comment.to_dict()
        # override the default output from pydantic by calling `to_dict()` of add_relation
        if self.add_relation:
            _dict['addRelation'] = self.add_relation.to_dict()
        # override the default output from pydantic by calling `to_dict()` of add_watcher
        if self.add_watcher:
            _dict['addWatcher'] = self.add_watcher.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in custom_actions (list)
        _items = []
        if self.custom_actions:
            for _item_custom_actions in self.custom_actions:
                if _item_custom_actions:
                    _items.append(_item_custom_actions.to_dict())
            _dict['customActions'] = _items
        # override the default output from pydantic by calling `to_dict()` of preview_markup
        if self.preview_markup:
            _dict['previewMarkup'] = self.preview_markup.to_dict()
        # override the default output from pydantic by calling `to_dict()` of remove_watcher
        if self.remove_watcher:
            _dict['removeWatcher'] = self.remove_watcher.to_dict()
        # override the default output from pydantic by calling `to_dict()` of delete
        if self.delete:
            _dict['delete'] = self.delete.to_dict()
        # override the default output from pydantic by calling `to_dict()` of log_time
        if self.log_time:
            _dict['logTime'] = self.log_time.to_dict()
        # override the default output from pydantic by calling `to_dict()` of move
        if self.move:
            _dict['move'] = self.move.to_dict()
        # override the default output from pydantic by calling `to_dict()` of copy
        if self.copy:
            _dict['copy'] = self.copy.to_dict()
        # override the default output from pydantic by calling `to_dict()` of unwatch
        if self.unwatch:
            _dict['unwatch'] = self.unwatch.to_dict()
        # override the default output from pydantic by calling `to_dict()` of update
        if self.update:
            _dict['update'] = self.update.to_dict()
        # override the default output from pydantic by calling `to_dict()` of update_immediately
        if self.update_immediately:
            _dict['updateImmediately'] = self.update_immediately.to_dict()
        # override the default output from pydantic by calling `to_dict()` of watch
        if self.watch:
            _dict['watch'] = self.watch.to_dict()
        # override the default output from pydantic by calling `to_dict()` of var_self
        if self.var_self:
            _dict['self'] = self.var_self.to_dict()
        # override the default output from pydantic by calling `to_dict()` of var_schema
        if self.var_schema:
            _dict['schema'] = self.var_schema.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in ancestors (list)
        _items = []
        if self.ancestors:
            for _item_ancestors in self.ancestors:
                if _item_ancestors:
                    _items.append(_item_ancestors.to_dict())
            _dict['ancestors'] = _items
        # override the default output from pydantic by calling `to_dict()` of attachments
        if self.attachments:
            _dict['attachments'] = self.attachments.to_dict()
        # override the default output from pydantic by calling `to_dict()` of add_attachment
        if self.add_attachment:
            _dict['addAttachment'] = self.add_attachment.to_dict()
        # override the default output from pydantic by calling `to_dict()` of prepare_attachment
        if self.prepare_attachment:
            _dict['prepareAttachment'] = self.prepare_attachment.to_dict()
        # override the default output from pydantic by calling `to_dict()` of author
        if self.author:
            _dict['author'] = self.author.to_dict()
        # override the default output from pydantic by calling `to_dict()` of assignee
        if self.assignee:
            _dict['assignee'] = self.assignee.to_dict()
        # override the default output from pydantic by calling `to_dict()` of available_watchers
        if self.available_watchers:
            _dict['availableWatchers'] = self.available_watchers.to_dict()
        # override the default output from pydantic by calling `to_dict()` of budget
        if self.budget:
            _dict['budget'] = self.budget.to_dict()
        # override the default output from pydantic by calling `to_dict()` of category
        if self.category:
            _dict['category'] = self.category.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in children (list)
        _items = []
        if self.children:
            for _item_children in self.children:
                if _item_children:
                    _items.append(_item_children.to_dict())
            _dict['children'] = _items
        # override the default output from pydantic by calling `to_dict()` of add_file_link
        if self.add_file_link:
            _dict['addFileLink'] = self.add_file_link.to_dict()
        # override the default output from pydantic by calling `to_dict()` of file_links
        if self.file_links:
            _dict['fileLinks'] = self.file_links.to_dict()
        # override the default output from pydantic by calling `to_dict()` of parent
        if self.parent:
            _dict['parent'] = self.parent.to_dict()
        # override the default output from pydantic by calling `to_dict()` of priority
        if self.priority:
            _dict['priority'] = self.priority.to_dict()
        # override the default output from pydantic by calling `to_dict()` of project
        if self.project:
            _dict['project'] = self.project.to_dict()
        # override the default output from pydantic by calling `to_dict()` of project_phase
        if self.project_phase:
            _dict['projectPhase'] = self.project_phase.to_dict()
        # override the default output from pydantic by calling `to_dict()` of project_phase_definition
        if self.project_phase_definition:
            _dict['projectPhaseDefinition'] = self.project_phase_definition.to_dict()
        # override the default output from pydantic by calling `to_dict()` of responsible
        if self.responsible:
            _dict['responsible'] = self.responsible.to_dict()
        # override the default output from pydantic by calling `to_dict()` of relations
        if self.relations:
            _dict['relations'] = self.relations.to_dict()
        # override the default output from pydantic by calling `to_dict()` of revisions
        if self.revisions:
            _dict['revisions'] = self.revisions.to_dict()
        # override the default output from pydantic by calling `to_dict()` of status
        if self.status:
            _dict['status'] = self.status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of time_entries
        if self.time_entries:
            _dict['timeEntries'] = self.time_entries.to_dict()
        # override the default output from pydantic by calling `to_dict()` of type
        if self.type:
            _dict['type'] = self.type.to_dict()
        # override the default output from pydantic by calling `to_dict()` of version
        if self.version:
            _dict['version'] = self.version.to_dict()
        # override the default output from pydantic by calling `to_dict()` of watchers
        if self.watchers:
            _dict['watchers'] = self.watchers.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of WorkPackageModelAllOfLinks from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "addComment": Link.from_dict(obj["addComment"]) if obj.get("addComment") is not None else None,
            "addRelation": Link.from_dict(obj["addRelation"]) if obj.get("addRelation") is not None else None,
            "addWatcher": Link.from_dict(obj["addWatcher"]) if obj.get("addWatcher") is not None else None,
            "customActions": [WorkPackageModelAllOfLinksCustomActions.from_dict(_item) for _item in obj["customActions"]] if obj.get("customActions") is not None else None,
            "previewMarkup": Link.from_dict(obj["previewMarkup"]) if obj.get("previewMarkup") is not None else None,
            "removeWatcher": Link.from_dict(obj["removeWatcher"]) if obj.get("removeWatcher") is not None else None,
            "delete": Link.from_dict(obj["delete"]) if obj.get("delete") is not None else None,
            "logTime": Link.from_dict(obj["logTime"]) if obj.get("logTime") is not None else None,
            "move": Link.from_dict(obj["move"]) if obj.get("move") is not None else None,
            "copy": Link.from_dict(obj["copy"]) if obj.get("copy") is not None else None,
            "unwatch": Link.from_dict(obj["unwatch"]) if obj.get("unwatch") is not None else None,
            "update": Link.from_dict(obj["update"]) if obj.get("update") is not None else None,
            "updateImmediately": Link.from_dict(obj["updateImmediately"]) if obj.get("updateImmediately") is not None else None,
            "watch": Link.from_dict(obj["watch"]) if obj.get("watch") is not None else None,
            "self": Link.from_dict(obj["self"]) if obj.get("self") is not None else None,
            "schema": Link.from_dict(obj["schema"]) if obj.get("schema") is not None else None,
            "ancestors": [WorkPackageModelAllOfLinksAncestors.from_dict(_item) for _item in obj["ancestors"]] if obj.get("ancestors") is not None else None,
            "attachments": Link.from_dict(obj["attachments"]) if obj.get("attachments") is not None else None,
            "addAttachment": Link.from_dict(obj["addAttachment"]) if obj.get("addAttachment") is not None else None,
            "prepareAttachment": Link.from_dict(obj["prepareAttachment"]) if obj.get("prepareAttachment") is not None else None,
            "author": Link.from_dict(obj["author"]) if obj.get("author") is not None else None,
            "assignee": Link.from_dict(obj["assignee"]) if obj.get("assignee") is not None else None,
            "availableWatchers": Link.from_dict(obj["availableWatchers"]) if obj.get("availableWatchers") is not None else None,
            "budget": Link.from_dict(obj["budget"]) if obj.get("budget") is not None else None,
            "category": Link.from_dict(obj["category"]) if obj.get("category") is not None else None,
            "children": [WorkPackageModelAllOfLinksChildren.from_dict(_item) for _item in obj["children"]] if obj.get("children") is not None else None,
            "addFileLink": Link.from_dict(obj["addFileLink"]) if obj.get("addFileLink") is not None else None,
            "fileLinks": Link.from_dict(obj["fileLinks"]) if obj.get("fileLinks") is not None else None,
            "parent": Link.from_dict(obj["parent"]) if obj.get("parent") is not None else None,
            "priority": Link.from_dict(obj["priority"]) if obj.get("priority") is not None else None,
            "project": Link.from_dict(obj["project"]) if obj.get("project") is not None else None,
            "projectPhase": Link.from_dict(obj["projectPhase"]) if obj.get("projectPhase") is not None else None,
            "projectPhaseDefinition": Link.from_dict(obj["projectPhaseDefinition"]) if obj.get("projectPhaseDefinition") is not None else None,
            "responsible": Link.from_dict(obj["responsible"]) if obj.get("responsible") is not None else None,
            "relations": Link.from_dict(obj["relations"]) if obj.get("relations") is not None else None,
            "revisions": Link.from_dict(obj["revisions"]) if obj.get("revisions") is not None else None,
            "status": Link.from_dict(obj["status"]) if obj.get("status") is not None else None,
            "timeEntries": Link.from_dict(obj["timeEntries"]) if obj.get("timeEntries") is not None else None,
            "type": Link.from_dict(obj["type"]) if obj.get("type") is not None else None,
            "version": Link.from_dict(obj["version"]) if obj.get("version") is not None else None,
            "watchers": Link.from_dict(obj["watchers"]) if obj.get("watchers") is not None else None
        })
        return _obj


