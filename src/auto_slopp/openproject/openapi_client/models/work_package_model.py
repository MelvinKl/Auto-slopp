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

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from auto_slopp.openproject.openapi_client.models.formattable import Formattable
from auto_slopp.openproject.openapi_client.models.work_package_model_all_of_links import WorkPackageModelAllOfLinks
from typing import Optional, Set
from typing_extensions import Self
from pydantic_core import to_jsonable_python

class WorkPackageModel(BaseModel):
    """
    WorkPackageModel
    """ # noqa: E501
    id: Optional[Annotated[int, Field(strict=True, ge=1)]] = Field(default=None, description="Work package id")
    lock_version: Optional[StrictInt] = Field(default=None, description="The version of the item as used for optimistic locking", alias="lockVersion")
    subject: StrictStr = Field(description="Work package subject")
    type: Optional[StrictStr] = Field(default=None, alias="_type")
    description: Optional[Formattable] = Field(default=None, description="The work package description")
    schedule_manually: Optional[StrictBool] = Field(default=None, description="Uses manual scheduling mode when true (default). Uses automatic scheduling mode when false. Can be automatic only when predecessors or children are present.", alias="scheduleManually")
    readonly: Optional[StrictBool] = Field(default=None, description="If true, the work package is in a readonly status so with the exception of the status, no other property can be altered.")
    start_date: Optional[date] = Field(default=None, description="Scheduled beginning of a work package", alias="startDate")
    due_date: Optional[date] = Field(default=None, description="Scheduled end of a work package", alias="dueDate")
    var_date: Optional[date] = Field(default=None, description="Date on which a milestone is achieved", alias="date")
    derived_start_date: Optional[date] = Field(default=None, description="Similar to start date but is not set by a client but rather deduced by the work packages' descendants. If manual scheduleManually is active, the two dates can deviate.", alias="derivedStartDate")
    derived_due_date: Optional[date] = Field(default=None, description="Similar to due date but is not set by a client but rather deduced by the work packages' descendants. If manual scheduleManually is active, the two dates can deviate.", alias="derivedDueDate")
    duration: Optional[StrictStr] = Field(default=None, description="**(NOT IMPLEMENTED)** The amount of time in hours the work package needs to be completed. Not available for milestone type of work packages.")
    estimated_time: Optional[StrictStr] = Field(default=None, description="Time a work package likely needs to be completed excluding its descendants", alias="estimatedTime")
    derived_estimated_time: Optional[StrictStr] = Field(default=None, description="Time a work package likely needs to be completed including its descendants", alias="derivedEstimatedTime")
    ignore_non_working_days: Optional[StrictBool] = Field(default=None, description="**(NOT IMPLEMENTED)** When scheduling, whether or not to ignore the non working days being defined. A work package with the flag set to true will be allowed to be scheduled to a non working day.", alias="ignoreNonWorkingDays")
    spent_time: Optional[StrictStr] = Field(default=None, description="The time booked for this work package by users working on it  # Conditions  **Permission** view time entries", alias="spentTime")
    percentage_done: Optional[Annotated[int, Field(le=100, strict=True, ge=0)]] = Field(default=None, description="Amount of total completion for a work package", alias="percentageDone")
    derived_percentage_done: Optional[Annotated[int, Field(le=100, strict=True, ge=0)]] = Field(default=None, description="Amount of total completion for a work package derived from itself and its descendant work packages", alias="derivedPercentageDone")
    created_at: Optional[datetime] = Field(default=None, description="Time of creation. Can be writable by admins with the `apiv3_write_readonly_attributes` setting enabled.", alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, description="Time of the most recent change to the work package.", alias="updatedAt")
    links: WorkPackageModelAllOfLinks = Field(alias="_links")
    __properties: ClassVar[List[str]] = ["id", "lockVersion", "subject", "_type", "description", "scheduleManually", "readonly", "startDate", "dueDate", "date", "derivedStartDate", "derivedDueDate", "duration", "estimatedTime", "derivedEstimatedTime", "ignoreNonWorkingDays", "spentTime", "percentageDone", "derivedPercentageDone", "createdAt", "updatedAt", "_links"]

    @field_validator('type')
    def type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['WorkPackage']):
            raise ValueError("must be one of enum values ('WorkPackage')")
        return value

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
        """Create an instance of WorkPackageModel from a JSON string"""
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
        """
        excluded_fields: Set[str] = set([
            "id",
            "lock_version",
            "type",
            "derived_start_date",
            "derived_due_date",
            "duration",
            "derived_estimated_time",
            "ignore_non_working_days",
            "spent_time",
            "derived_percentage_done",
            "created_at",
            "updated_at",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of description
        if self.description:
            _dict['description'] = self.description.to_dict()
        # override the default output from pydantic by calling `to_dict()` of links
        if self.links:
            _dict['_links'] = self.links.to_dict()
        # set to None if start_date (nullable) is None
        # and model_fields_set contains the field
        if self.start_date is None and "start_date" in self.model_fields_set:
            _dict['startDate'] = None

        # set to None if due_date (nullable) is None
        # and model_fields_set contains the field
        if self.due_date is None and "due_date" in self.model_fields_set:
            _dict['dueDate'] = None

        # set to None if var_date (nullable) is None
        # and model_fields_set contains the field
        if self.var_date is None and "var_date" in self.model_fields_set:
            _dict['date'] = None

        # set to None if derived_start_date (nullable) is None
        # and model_fields_set contains the field
        if self.derived_start_date is None and "derived_start_date" in self.model_fields_set:
            _dict['derivedStartDate'] = None

        # set to None if derived_due_date (nullable) is None
        # and model_fields_set contains the field
        if self.derived_due_date is None and "derived_due_date" in self.model_fields_set:
            _dict['derivedDueDate'] = None

        # set to None if duration (nullable) is None
        # and model_fields_set contains the field
        if self.duration is None and "duration" in self.model_fields_set:
            _dict['duration'] = None

        # set to None if estimated_time (nullable) is None
        # and model_fields_set contains the field
        if self.estimated_time is None and "estimated_time" in self.model_fields_set:
            _dict['estimatedTime'] = None

        # set to None if derived_estimated_time (nullable) is None
        # and model_fields_set contains the field
        if self.derived_estimated_time is None and "derived_estimated_time" in self.model_fields_set:
            _dict['derivedEstimatedTime'] = None

        # set to None if percentage_done (nullable) is None
        # and model_fields_set contains the field
        if self.percentage_done is None and "percentage_done" in self.model_fields_set:
            _dict['percentageDone'] = None

        # set to None if derived_percentage_done (nullable) is None
        # and model_fields_set contains the field
        if self.derived_percentage_done is None and "derived_percentage_done" in self.model_fields_set:
            _dict['derivedPercentageDone'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of WorkPackageModel from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "lockVersion": obj.get("lockVersion"),
            "subject": obj.get("subject"),
            "_type": obj.get("_type"),
            "description": Formattable.from_dict(obj["description"]) if obj.get("description") is not None else None,
            "scheduleManually": obj.get("scheduleManually"),
            "readonly": obj.get("readonly"),
            "startDate": obj.get("startDate"),
            "dueDate": obj.get("dueDate"),
            "date": obj.get("date"),
            "derivedStartDate": obj.get("derivedStartDate"),
            "derivedDueDate": obj.get("derivedDueDate"),
            "duration": obj.get("duration"),
            "estimatedTime": obj.get("estimatedTime"),
            "derivedEstimatedTime": obj.get("derivedEstimatedTime"),
            "ignoreNonWorkingDays": obj.get("ignoreNonWorkingDays"),
            "spentTime": obj.get("spentTime"),
            "percentageDone": obj.get("percentageDone"),
            "derivedPercentageDone": obj.get("derivedPercentageDone"),
            "createdAt": obj.get("createdAt"),
            "updatedAt": obj.get("updatedAt"),
            "_links": WorkPackageModelAllOfLinks.from_dict(obj["_links"]) if obj.get("_links") is not None else None
        })
        return _obj


