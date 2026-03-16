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
from openproject_client.models.link import Link
from openproject_client.models.portfolio_model_all_of_links_ancestors import PortfolioModelAllOfLinksAncestors
from openproject_client.models.portfolio_model_all_of_links_storages import PortfolioModelAllOfLinksStorages
from typing import Optional, Set
from typing_extensions import Self

class PortfolioModelAllOfLinks(BaseModel):
    """
    PortfolioModelAllOfLinks
    """ # noqa: E501
    update: Optional[Link] = Field(default=None, description="Form endpoint that aids in updating this portfolio  # Conditions  **Permission**: edit workspace")
    update_immediately: Optional[Link] = Field(default=None, description="Directly update this portfolio  # Conditions  **Permission**: edit workspace", alias="updateImmediately")
    delete: Optional[Link] = Field(default=None, description="Delete this portfolio  # Conditions  **Permission**: admin")
    favor: Optional[Link] = Field(default=None, description="Mark this portfolio as favorited by the current user  # Conditions  Only present if the portfolio is not yet favorited  Permission**: none but login is required")
    disfavor: Optional[Link] = Field(default=None, description="Mark this portfolio as not favorited by the current user  # Conditions Only present if the portfolio is favorited by the current user  Permission**: none but login is required")
    create_work_package: Optional[Link] = Field(default=None, description="Form endpoint that aids in preparing and creating a work package  # Conditions  **Permission**: add work packages", alias="createWorkPackage")
    create_work_package_immediately: Optional[Link] = Field(default=None, description="Directly creates a work package in the portfolio  # Conditions  **Permission**: add work packages", alias="createWorkPackageImmediately")
    var_self: Link = Field(description="This portfolio  **Resource**: Portfolio", alias="self")
    categories: Link = Field(description="Categories available in this portfolio  **Resource**: Collection")
    types: Optional[Link] = Field(default=None, description="Types available in this portfolio  **Resource**: Collection  # Conditions  **Permission**: view work packages or manage types")
    versions: Optional[Link] = Field(default=None, description="Versions available in this portfolio  **Resource**: Collection  # Conditions  **Permission**: view work packages or manage versions")
    memberships: Optional[Link] = Field(default=None, description="Memberships in the  portfolio  **Resource**: Collection  # Conditions  **Permission**: view members")
    work_packages: Optional[Link] = Field(default=None, description="Work Packages of this portfolio  **Resource**: Collection", alias="workPackages")
    parent: Optional[Link] = Field(default=None, description="Parent of the portfolio  **Resource**: Portfolio  # Conditions  **Permission** edit workspace")
    status: Optional[Link] = Field(default=None, description="Denotes the status of the portfolio, so whether the portfolio is on track, at risk or is having trouble.  **Resource**: ProjectStatus  # Conditions  **Permission** edit workspace")
    storages: Optional[List[PortfolioModelAllOfLinksStorages]] = None
    project_storages: Optional[Link] = Field(default=None, description="The project storage collection of this portfolio.  **Resource**: Collection  # Conditions  **Permission**: view_file_links", alias="projectStorages")
    ancestors: Optional[List[PortfolioModelAllOfLinksAncestors]] = None
    __properties: ClassVar[List[str]] = ["update", "updateImmediately", "delete", "favor", "disfavor", "createWorkPackage", "createWorkPackageImmediately", "self", "categories", "types", "versions", "memberships", "workPackages", "parent", "status", "storages", "projectStorages", "ancestors"]

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
        """Create an instance of PortfolioModelAllOfLinks from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of update
        if self.update:
            _dict['update'] = self.update.to_dict()
        # override the default output from pydantic by calling `to_dict()` of update_immediately
        if self.update_immediately:
            _dict['updateImmediately'] = self.update_immediately.to_dict()
        # override the default output from pydantic by calling `to_dict()` of delete
        if self.delete:
            _dict['delete'] = self.delete.to_dict()
        # override the default output from pydantic by calling `to_dict()` of favor
        if self.favor:
            _dict['favor'] = self.favor.to_dict()
        # override the default output from pydantic by calling `to_dict()` of disfavor
        if self.disfavor:
            _dict['disfavor'] = self.disfavor.to_dict()
        # override the default output from pydantic by calling `to_dict()` of create_work_package
        if self.create_work_package:
            _dict['createWorkPackage'] = self.create_work_package.to_dict()
        # override the default output from pydantic by calling `to_dict()` of create_work_package_immediately
        if self.create_work_package_immediately:
            _dict['createWorkPackageImmediately'] = self.create_work_package_immediately.to_dict()
        # override the default output from pydantic by calling `to_dict()` of var_self
        if self.var_self:
            _dict['self'] = self.var_self.to_dict()
        # override the default output from pydantic by calling `to_dict()` of categories
        if self.categories:
            _dict['categories'] = self.categories.to_dict()
        # override the default output from pydantic by calling `to_dict()` of types
        if self.types:
            _dict['types'] = self.types.to_dict()
        # override the default output from pydantic by calling `to_dict()` of versions
        if self.versions:
            _dict['versions'] = self.versions.to_dict()
        # override the default output from pydantic by calling `to_dict()` of memberships
        if self.memberships:
            _dict['memberships'] = self.memberships.to_dict()
        # override the default output from pydantic by calling `to_dict()` of work_packages
        if self.work_packages:
            _dict['workPackages'] = self.work_packages.to_dict()
        # override the default output from pydantic by calling `to_dict()` of parent
        if self.parent:
            _dict['parent'] = self.parent.to_dict()
        # override the default output from pydantic by calling `to_dict()` of status
        if self.status:
            _dict['status'] = self.status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in storages (list)
        _items = []
        if self.storages:
            for _item_storages in self.storages:
                if _item_storages:
                    _items.append(_item_storages.to_dict())
            _dict['storages'] = _items
        # override the default output from pydantic by calling `to_dict()` of project_storages
        if self.project_storages:
            _dict['projectStorages'] = self.project_storages.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in ancestors (list)
        _items = []
        if self.ancestors:
            for _item_ancestors in self.ancestors:
                if _item_ancestors:
                    _items.append(_item_ancestors.to_dict())
            _dict['ancestors'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PortfolioModelAllOfLinks from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "update": Link.from_dict(obj["update"]) if obj.get("update") is not None else None,
            "updateImmediately": Link.from_dict(obj["updateImmediately"]) if obj.get("updateImmediately") is not None else None,
            "delete": Link.from_dict(obj["delete"]) if obj.get("delete") is not None else None,
            "favor": Link.from_dict(obj["favor"]) if obj.get("favor") is not None else None,
            "disfavor": Link.from_dict(obj["disfavor"]) if obj.get("disfavor") is not None else None,
            "createWorkPackage": Link.from_dict(obj["createWorkPackage"]) if obj.get("createWorkPackage") is not None else None,
            "createWorkPackageImmediately": Link.from_dict(obj["createWorkPackageImmediately"]) if obj.get("createWorkPackageImmediately") is not None else None,
            "self": Link.from_dict(obj["self"]) if obj.get("self") is not None else None,
            "categories": Link.from_dict(obj["categories"]) if obj.get("categories") is not None else None,
            "types": Link.from_dict(obj["types"]) if obj.get("types") is not None else None,
            "versions": Link.from_dict(obj["versions"]) if obj.get("versions") is not None else None,
            "memberships": Link.from_dict(obj["memberships"]) if obj.get("memberships") is not None else None,
            "workPackages": Link.from_dict(obj["workPackages"]) if obj.get("workPackages") is not None else None,
            "parent": Link.from_dict(obj["parent"]) if obj.get("parent") is not None else None,
            "status": Link.from_dict(obj["status"]) if obj.get("status") is not None else None,
            "storages": [PortfolioModelAllOfLinksStorages.from_dict(_item) for _item in obj["storages"]] if obj.get("storages") is not None else None,
            "projectStorages": Link.from_dict(obj["projectStorages"]) if obj.get("projectStorages") is not None else None,
            "ancestors": [PortfolioModelAllOfLinksAncestors.from_dict(_item) for _item in obj["ancestors"]] if obj.get("ancestors") is not None else None
        })
        return _obj


