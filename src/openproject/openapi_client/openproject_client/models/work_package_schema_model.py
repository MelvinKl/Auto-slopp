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

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from openproject_client.models.schema_property_model import SchemaPropertyModel
from openproject_client.models.work_package_schema_model_links import WorkPackageSchemaModelLinks
from typing import Optional, Set
from typing_extensions import Self

class WorkPackageSchemaModel(BaseModel):
    """
    A schema for a work package. This schema defines the attributes of a work package.  TODO: Incomplete, needs to be updated with the real behaviour of schemas (when does which attribute appear?).
    """ # noqa: E501
    type: Optional[StrictStr] = Field(default=None, alias="_type")
    dependencies: Optional[List[StrictStr]] = Field(default=None, description="TBD", alias="_dependencies")
    attribute_groups: Optional[List[Dict[str, Any]]] = Field(default=None, description="TBD (WorkPackageFormAttributeGroup)", alias="_attributeGroups")
    lock_version: Optional[SchemaPropertyModel] = Field(default=None, alias="lockVersion")
    id: Optional[SchemaPropertyModel] = None
    subject: Optional[SchemaPropertyModel] = None
    description: Optional[SchemaPropertyModel] = None
    duration: Optional[SchemaPropertyModel] = None
    schedule_manually: Optional[SchemaPropertyModel] = Field(default=None, alias="scheduleManually")
    ignore_non_working_days: Optional[SchemaPropertyModel] = Field(default=None, alias="ignoreNonWorkingDays")
    start_date: Optional[SchemaPropertyModel] = Field(default=None, alias="startDate")
    due_date: Optional[SchemaPropertyModel] = Field(default=None, alias="dueDate")
    derived_start_date: Optional[SchemaPropertyModel] = Field(default=None, alias="derivedStartDate")
    derived_due_date: Optional[SchemaPropertyModel] = Field(default=None, alias="derivedDueDate")
    estimated_time: Optional[SchemaPropertyModel] = Field(default=None, alias="estimatedTime")
    derived_estimated_time: Optional[SchemaPropertyModel] = Field(default=None, alias="derivedEstimatedTime")
    remaining_time: Optional[SchemaPropertyModel] = Field(default=None, alias="remainingTime")
    derived_remaining_time: Optional[SchemaPropertyModel] = Field(default=None, alias="derivedRemainingTime")
    percentage_done: Optional[SchemaPropertyModel] = Field(default=None, alias="percentageDone")
    derived_percentage_done: Optional[SchemaPropertyModel] = Field(default=None, alias="derivedPercentageDone")
    readonly: Optional[SchemaPropertyModel] = None
    created_at: Optional[SchemaPropertyModel] = Field(default=None, alias="createdAt")
    updated_at: Optional[SchemaPropertyModel] = Field(default=None, alias="updatedAt")
    author: Optional[SchemaPropertyModel] = None
    project: Optional[SchemaPropertyModel] = None
    project_phase: Optional[SchemaPropertyModel] = Field(default=None, alias="projectPhase")
    project_phase_definition: Optional[SchemaPropertyModel] = Field(default=None, alias="projectPhaseDefinition")
    parent: Optional[SchemaPropertyModel] = None
    assignee: Optional[SchemaPropertyModel] = None
    responsible: Optional[SchemaPropertyModel] = None
    type: Optional[SchemaPropertyModel] = None
    status: Optional[SchemaPropertyModel] = None
    category: Optional[SchemaPropertyModel] = None
    version: Optional[SchemaPropertyModel] = None
    priority: Optional[SchemaPropertyModel] = None
    links: Optional[WorkPackageSchemaModelLinks] = Field(default=None, alias="_links")
    __properties: ClassVar[List[str]] = ["_type", "_dependencies", "_attributeGroups", "lockVersion", "id", "subject", "description", "duration", "scheduleManually", "ignoreNonWorkingDays", "startDate", "dueDate", "derivedStartDate", "derivedDueDate", "estimatedTime", "derivedEstimatedTime", "remainingTime", "derivedRemainingTime", "percentageDone", "derivedPercentageDone", "readonly", "createdAt", "updatedAt", "author", "project", "projectPhase", "projectPhaseDefinition", "parent", "assignee", "responsible", "type", "status", "category", "version", "priority", "_links"]

    @field_validator('type')
    def type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Schema']):
            raise ValueError("must be one of enum values ('Schema')")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of WorkPackageSchemaModel from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of lock_version
        if self.lock_version:
            _dict['lockVersion'] = self.lock_version.to_dict()
        # override the default output from pydantic by calling `to_dict()` of id
        if self.id:
            _dict['id'] = self.id.to_dict()
        # override the default output from pydantic by calling `to_dict()` of subject
        if self.subject:
            _dict['subject'] = self.subject.to_dict()
        # override the default output from pydantic by calling `to_dict()` of description
        if self.description:
            _dict['description'] = self.description.to_dict()
        # override the default output from pydantic by calling `to_dict()` of duration
        if self.duration:
            _dict['duration'] = self.duration.to_dict()
        # override the default output from pydantic by calling `to_dict()` of schedule_manually
        if self.schedule_manually:
            _dict['scheduleManually'] = self.schedule_manually.to_dict()
        # override the default output from pydantic by calling `to_dict()` of ignore_non_working_days
        if self.ignore_non_working_days:
            _dict['ignoreNonWorkingDays'] = self.ignore_non_working_days.to_dict()
        # override the default output from pydantic by calling `to_dict()` of start_date
        if self.start_date:
            _dict['startDate'] = self.start_date.to_dict()
        # override the default output from pydantic by calling `to_dict()` of due_date
        if self.due_date:
            _dict['dueDate'] = self.due_date.to_dict()
        # override the default output from pydantic by calling `to_dict()` of derived_start_date
        if self.derived_start_date:
            _dict['derivedStartDate'] = self.derived_start_date.to_dict()
        # override the default output from pydantic by calling `to_dict()` of derived_due_date
        if self.derived_due_date:
            _dict['derivedDueDate'] = self.derived_due_date.to_dict()
        # override the default output from pydantic by calling `to_dict()` of estimated_time
        if self.estimated_time:
            _dict['estimatedTime'] = self.estimated_time.to_dict()
        # override the default output from pydantic by calling `to_dict()` of derived_estimated_time
        if self.derived_estimated_time:
            _dict['derivedEstimatedTime'] = self.derived_estimated_time.to_dict()
        # override the default output from pydantic by calling `to_dict()` of remaining_time
        if self.remaining_time:
            _dict['remainingTime'] = self.remaining_time.to_dict()
        # override the default output from pydantic by calling `to_dict()` of derived_remaining_time
        if self.derived_remaining_time:
            _dict['derivedRemainingTime'] = self.derived_remaining_time.to_dict()
        # override the default output from pydantic by calling `to_dict()` of percentage_done
        if self.percentage_done:
            _dict['percentageDone'] = self.percentage_done.to_dict()
        # override the default output from pydantic by calling `to_dict()` of derived_percentage_done
        if self.derived_percentage_done:
            _dict['derivedPercentageDone'] = self.derived_percentage_done.to_dict()
        # override the default output from pydantic by calling `to_dict()` of readonly
        if self.readonly:
            _dict['readonly'] = self.readonly.to_dict()
        # override the default output from pydantic by calling `to_dict()` of created_at
        if self.created_at:
            _dict['createdAt'] = self.created_at.to_dict()
        # override the default output from pydantic by calling `to_dict()` of updated_at
        if self.updated_at:
            _dict['updatedAt'] = self.updated_at.to_dict()
        # override the default output from pydantic by calling `to_dict()` of author
        if self.author:
            _dict['author'] = self.author.to_dict()
        # override the default output from pydantic by calling `to_dict()` of project
        if self.project:
            _dict['project'] = self.project.to_dict()
        # override the default output from pydantic by calling `to_dict()` of project_phase
        if self.project_phase:
            _dict['projectPhase'] = self.project_phase.to_dict()
        # override the default output from pydantic by calling `to_dict()` of project_phase_definition
        if self.project_phase_definition:
            _dict['projectPhaseDefinition'] = self.project_phase_definition.to_dict()
        # override the default output from pydantic by calling `to_dict()` of parent
        if self.parent:
            _dict['parent'] = self.parent.to_dict()
        # override the default output from pydantic by calling `to_dict()` of assignee
        if self.assignee:
            _dict['assignee'] = self.assignee.to_dict()
        # override the default output from pydantic by calling `to_dict()` of responsible
        if self.responsible:
            _dict['responsible'] = self.responsible.to_dict()
        # override the default output from pydantic by calling `to_dict()` of type
        if self.type:
            _dict['type'] = self.type.to_dict()
        # override the default output from pydantic by calling `to_dict()` of status
        if self.status:
            _dict['status'] = self.status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of category
        if self.category:
            _dict['category'] = self.category.to_dict()
        # override the default output from pydantic by calling `to_dict()` of version
        if self.version:
            _dict['version'] = self.version.to_dict()
        # override the default output from pydantic by calling `to_dict()` of priority
        if self.priority:
            _dict['priority'] = self.priority.to_dict()
        # override the default output from pydantic by calling `to_dict()` of links
        if self.links:
            _dict['_links'] = self.links.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of WorkPackageSchemaModel from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "_type": obj.get("_type"),
            "_dependencies": obj.get("_dependencies"),
            "_attributeGroups": obj.get("_attributeGroups"),
            "lockVersion": SchemaPropertyModel.from_dict(obj["lockVersion"]) if obj.get("lockVersion") is not None else None,
            "id": SchemaPropertyModel.from_dict(obj["id"]) if obj.get("id") is not None else None,
            "subject": SchemaPropertyModel.from_dict(obj["subject"]) if obj.get("subject") is not None else None,
            "description": SchemaPropertyModel.from_dict(obj["description"]) if obj.get("description") is not None else None,
            "duration": SchemaPropertyModel.from_dict(obj["duration"]) if obj.get("duration") is not None else None,
            "scheduleManually": SchemaPropertyModel.from_dict(obj["scheduleManually"]) if obj.get("scheduleManually") is not None else None,
            "ignoreNonWorkingDays": SchemaPropertyModel.from_dict(obj["ignoreNonWorkingDays"]) if obj.get("ignoreNonWorkingDays") is not None else None,
            "startDate": SchemaPropertyModel.from_dict(obj["startDate"]) if obj.get("startDate") is not None else None,
            "dueDate": SchemaPropertyModel.from_dict(obj["dueDate"]) if obj.get("dueDate") is not None else None,
            "derivedStartDate": SchemaPropertyModel.from_dict(obj["derivedStartDate"]) if obj.get("derivedStartDate") is not None else None,
            "derivedDueDate": SchemaPropertyModel.from_dict(obj["derivedDueDate"]) if obj.get("derivedDueDate") is not None else None,
            "estimatedTime": SchemaPropertyModel.from_dict(obj["estimatedTime"]) if obj.get("estimatedTime") is not None else None,
            "derivedEstimatedTime": SchemaPropertyModel.from_dict(obj["derivedEstimatedTime"]) if obj.get("derivedEstimatedTime") is not None else None,
            "remainingTime": SchemaPropertyModel.from_dict(obj["remainingTime"]) if obj.get("remainingTime") is not None else None,
            "derivedRemainingTime": SchemaPropertyModel.from_dict(obj["derivedRemainingTime"]) if obj.get("derivedRemainingTime") is not None else None,
            "percentageDone": SchemaPropertyModel.from_dict(obj["percentageDone"]) if obj.get("percentageDone") is not None else None,
            "derivedPercentageDone": SchemaPropertyModel.from_dict(obj["derivedPercentageDone"]) if obj.get("derivedPercentageDone") is not None else None,
            "readonly": SchemaPropertyModel.from_dict(obj["readonly"]) if obj.get("readonly") is not None else None,
            "createdAt": SchemaPropertyModel.from_dict(obj["createdAt"]) if obj.get("createdAt") is not None else None,
            "updatedAt": SchemaPropertyModel.from_dict(obj["updatedAt"]) if obj.get("updatedAt") is not None else None,
            "author": SchemaPropertyModel.from_dict(obj["author"]) if obj.get("author") is not None else None,
            "project": SchemaPropertyModel.from_dict(obj["project"]) if obj.get("project") is not None else None,
            "projectPhase": SchemaPropertyModel.from_dict(obj["projectPhase"]) if obj.get("projectPhase") is not None else None,
            "projectPhaseDefinition": SchemaPropertyModel.from_dict(obj["projectPhaseDefinition"]) if obj.get("projectPhaseDefinition") is not None else None,
            "parent": SchemaPropertyModel.from_dict(obj["parent"]) if obj.get("parent") is not None else None,
            "assignee": SchemaPropertyModel.from_dict(obj["assignee"]) if obj.get("assignee") is not None else None,
            "responsible": SchemaPropertyModel.from_dict(obj["responsible"]) if obj.get("responsible") is not None else None,
            "type": SchemaPropertyModel.from_dict(obj["type"]) if obj.get("type") is not None else None,
            "status": SchemaPropertyModel.from_dict(obj["status"]) if obj.get("status") is not None else None,
            "category": SchemaPropertyModel.from_dict(obj["category"]) if obj.get("category") is not None else None,
            "version": SchemaPropertyModel.from_dict(obj["version"]) if obj.get("version") is not None else None,
            "priority": SchemaPropertyModel.from_dict(obj["priority"]) if obj.get("priority") is not None else None,
            "_links": WorkPackageSchemaModelLinks.from_dict(obj["_links"]) if obj.get("_links") is not None else None
        })
        return _obj


