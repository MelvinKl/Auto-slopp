# coding: utf-8

"""
    OpenProject API V3 (Stable)

    You're looking at the current **stable** documentation of the OpenProject APIv3. If you're interested in the current development version, please go to [github.com/opf](https://github.com/opf/openproject/tree/dev/docs/api/apiv3).  ## Introduction  The documentation for the APIv3 is written according to the [OpenAPI 3.1 Specification](https://swagger.io/specification/). You can either view the static version of this documentation on the [website](https://www.openproject.org/docs/api/introduction/) or the interactive version, rendered with [OpenAPI Explorer](https://github.com/Rhosys/openapi-explorer/blob/main/README.md), in your OpenProject installation under `/api/docs`. In the latter you can try out the various API endpoints directly interacting with our OpenProject data. Moreover you can access the specification source itself under `/api/v3/spec.json` and `/api/v3/spec.yml` (e.g. [here](https://community.openproject.org/api/v3/spec.yml)).  The APIv3 is a hypermedia REST API, a shorthand for \"Hypermedia As The Engine Of Application State\" (HATEOAS). This means that each endpoint of this API will have links to other resources or actions defined in the resulting body.  These related resources and actions for any given resource will be context sensitive. For example, only actions that the authenticated user can take are being rendered. This can be used to dynamically identify actions that the user might take for any given response.  As an example, if you fetch a work package through the [Work Package endpoint](https://www.openproject.org/docs/api/endpoints/work-packages/), the `update` link will only be present when the user you authenticated has been granted a permission to update the work package in the assigned project.  ## HAL+JSON  HAL is a simple format that gives a consistent and easy way to hyperlink between resources in your API. Read more in the following specification: [https://tools.ietf.org/html/draft-kelly-json-hal-08](https://tools.ietf.org/html/draft-kelly-json-hal-08)  **OpenProject API implementation of HAL+JSON format** enriches JSON and introduces a few meta properties:  - `_type` - specifies the type of the resource (e.g.: WorkPackage, Project) - `_links` - contains all related resource and action links available for the resource - `_embedded` - contains all embedded objects  HAL does not guarantee that embedded resources are embedded in their full representation, they might as well be partially represented (e.g. some properties can be left out). However in this API you have the guarantee that whenever a resource is **embedded**, it is embedded in its **full representation**.  ## API response structure  All API responses contain a single HAL+JSON object, even collections of objects are technically represented by a single HAL+JSON object that itself contains its members. More details on collections can be found in the [Collections Section](https://www.openproject.org/docs/api/collections/).  ## Authentication  The API supports the following authentication schemes:  * Session-based authentication * API tokens     * passed as Bearer token     * passed via Basic auth * OAuth 2.0     * using built-in authorization server     * using an external authorization server (RFC 9068)  Depending on the settings of the OpenProject instance many resources can be accessed without being authenticated. In case the instance requires authentication on all requests the client will receive an **HTTP 401** status code in response to any request.  Otherwise unauthenticated clients have all the permissions of the anonymous user.  ### Session-based authentication  This means you have to login to OpenProject via the Web-Interface to be authenticated in the API. This method is well-suited for clients acting within the browser, like the Angular-Client built into OpenProject.  In this case, you always need to pass the HTTP header `X-Requested-With \"XMLHttpRequest\"` for authentication.  ### API token as bearer token  Users can authenticate towards the API v3 using an API token as a bearer token.  For example:  ```shell API_KEY=opapi-2519132cdf62dcf5a66fd96394672079f9e9cad1 curl -H \"Authorization: Bearer $API_KEY\" https://community.openproject.org/api/v3/users/42 ```  Users can generate API tokens on their account page.  ### API token through Basic Auth  API tokens can also be used with basic auth, using the user name `apikey` (NOT your login) and the API token as the password.  For example:  ```shell API_KEY=opapi-2519132cdf62dcf5a66fd96394672079f9e9cad1 curl -u apikey:$API_KEY https://community.openproject.org/api/v3/users/42 ```  ### OAuth 2.0 authentication  OpenProject allows authentication and authorization with OAuth2 with *Authorization code flow*, as well as *Client credentials* operation modes.  To get started, you first need to register an application in the OpenProject OAuth administration section of your installation. This will save an entry for your application with a client unique identifier (`client_id`) and an accompanying secret key (`client_secret`).  You can then use one the following guides to perform the supported OAuth 2.0 flows:  - [Authorization code flow](https://oauth.net/2/grant-types/authorization-code)  - [Authorization code flow with PKCE](https://doorkeeper.gitbook.io/guides/ruby-on-rails/pkce-flow), recommended for clients unable to keep the client_secret confidential  - [Client credentials](https://oauth.net/2/grant-types/client-credentials/) - Requires an application to be bound to an impersonating user for non-public access  ### OAuth 2.0 using an external authorization server  There is a possibility to use JSON Web Tokens (JWT) generated by an OIDC provider configured in OpenProject as a bearer token to do authenticated requests against the API. The following requirements must be met:  - OIDC provider must be configured in OpenProject with **jwks_uri** - JWT must be signed using RSA algorithm - JWT **iss** claim must be equal to OIDC provider **issuer** - JWT **aud** claim must contain the OpenProject **client ID** used at the OIDC provider - JWT **scope** claim must include a valid scope to access the desired API (e.g. `api_v3` for APIv3) - JWT must be actual (neither expired or too early to be used) - JWT must be passed in Authorization header like: `Authorization: Bearer {jwt}` - User from **sub** claim must be linked to OpenProject before (e.g. by logging in), otherwise it will be not authenticated  In more general terms, OpenProject should be compliant to [RFC 9068](https://www.rfc-editor.org/rfc/rfc9068) when validating access tokens.  ### Why not username and password?  The simplest way to do basic auth would be to use a user's username and password naturally. However, OpenProject already has supported API keys in the past for the API v2, though not through basic auth.  Using **username and password** directly would have some advantages:  * It is intuitive for the user who then just has to provide those just as they would when logging into OpenProject.  * No extra logic for token management necessary.  On the other hand using **API keys** has some advantages too, which is why we went for that:  * If compromised while saved on an insecure client the user only has to regenerate the API key instead of changing their password, too.  * They are naturally long and random which makes them invulnerable to dictionary attacks and harder to crack in general.  Most importantly users may not actually have a password to begin with. Specifically when they have registered through an OpenID Connect provider.  ## Cross-Origin Resource Sharing (CORS)  By default, the OpenProject API is _not_ responding with any CORS headers. If you want to allow cross-domain AJAX calls against your OpenProject instance, you need to enable CORS headers being returned.  Please see [our API settings documentation](https://www.openproject.org/docs/system-admin-guide/api-and-webhooks/) on how to selectively enable CORS.  ## Allowed HTTP methods  - `GET` - Get a single resource or collection of resources  - `POST` - Create a new resource or perform  - `PATCH` - Update a resource  - `DELETE` - Delete a resource  ## Compression  Responses are compressed if requested by the client. Currently [gzip](https://www.gzip.org/) and [deflate](https://tools.ietf.org/html/rfc1951) are supported. The client signals the desired compression by setting the [`Accept-Encoding` header](https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.3). If no `Accept-Encoding` header is send, `Accept-Encoding: identity` is assumed which will result in the API responding uncompressed.

    The version of the OpenAPI document: 3
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from openproject_client.models.notification_collection_model import NotificationCollectionModel

class TestNotificationCollectionModel(unittest.TestCase):
    """NotificationCollectionModel unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> NotificationCollectionModel:
        """Test NotificationCollectionModel
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `NotificationCollectionModel`
        """
        model = NotificationCollectionModel()
        if include_optional:
            return NotificationCollectionModel(
                type = 'Collection',
                total = 0,
                count = 0,
                links = openproject_client.models.notification_collection_model_all_of__links.NotificationCollectionModel_allOf__links(
                    self = null, 
                    jump_to = null, 
                    change_size = null, ),
                embedded = openproject_client.models.notification_collection_model_all_of__embedded.NotificationCollectionModel_allOf__embedded(
                    elements = [
                        openproject_client.models.notification_model.NotificationModel(
                            _type = 'Notification', 
                            id = 1, 
                            reason = 'assigned', 
                            read_ian = True, 
                            details = [
                                openproject_client.models.values_property_model.ValuesPropertyModel(
                                    _type = 'Values::Property', 
                                    property = '', 
                                    value = '', 
                                    _links = openproject_client.models.values_property_model__links.ValuesPropertyModel__links(
                                        self = null, 
                                        schema = null, ), )
                                ], 
                            created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            updated_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            _embedded = openproject_client.models.notification_model__embedded.NotificationModel__embedded(
                                actor = null, 
                                project = null, 
                                activity = {id=1, _type=Activity::Comment, _embedded={attachments={_type=Collection, total=1, count=1, _embedded={elements=[{_type=Attachment, id=30388, fileName=Task_Ensure_financing___4___OpenProject_DEV.jpeg, fileSize=540992, description={format=plain, raw=, html=}, status=uploaded, contentType=image/jpeg, digest={algorithm=md5, hash=d02d312b25383b595a9fa10f1a8999fe}, createdAt=2025-04-08T15:37:19.275Z, _links={self={href=/api/v3/attachments/30388, title=Task_Ensure_financing___4___OpenProject_DEV.jpeg}, author={href=/api/v3/users/435, title=Firstname}, container={href=/api/v3/activities/79090}, staticDownloadLocation={href=/api/v3/attachments/30388/content}, downloadLocation={href=/api/v3/attachments/30388/content}, delete={href=/api/v3/attachments/30388, method=delete}}}]}, _links={self={href=/api/v3/activities/79090/attachments}}}, emojiReactions={_type=Collection, total=2, count=2, _embedded={elements=[{_type=EmojiReaction, id=1-thumbs_up, reaction=thumbs_up, emoji=👍, reactionsCount=3, firstReactionAt=2024-04-08T15:37:19.275Z, _links={self={href=/api/v3/emoji_reactions/1-thumbs_up}, reactable={href=/api/v3/activities/1}, reactingUsers=[{href=/api/v3/users/435, title=John Doe}, {href=/api/v3/users/436, title=Jane Smith}, {href=/api/v3/users/437, title=Bob Johnson}]}}, {_type=EmojiReaction, id=1-heart, reaction=heart, emoji=❤️, reactionsCount=1, firstReactionAt=2024-04-08T15:38:19.275Z, _links={self={href=/api/v3/emoji_reactions/1-heart}, reactable={href=/api/v3/activities/1}, reactingUsers=[{href=/api/v3/users/435, title=John Doe}]}}]}, _links={self={href=/api/v3/activities/1/emoji_reactions}}}, workPackage={_type=WorkPackage, id=10403, lockVersion=2, subject=Ensure financing, description={format=markdown, raw=Lorem ipsum dolor sit amet., html=<p>Lorem ipsum dolor sit amet.</p>}, scheduleManually=true, startDate=null, dueDate=null, derivedStartDate=null, derivedDueDate=null, estimatedTime=null, derivedEstimatedTime=null, derivedRemainingTime=null, duration=null, ignoreNonWorkingDays=false, percentageDone=null, derivedPercentageDone=null, createdAt=2025-03-24T13:11:09.480Z, updatedAt=2025-04-14T11:00:02.411Z, _links={self={href=/api/v3/work_packages/10403, title=Ensure financing}, type={href=/api/v3/types/1, title=Task}, status={href=/api/v3/statuses/1, title=New}, project={href=/api/v3/projects/918, title=RVC Test}, schema={href=/api/v3/work_packages/schemas/11-2}, author={href=/api/v3/users/1, title=OpenProject Admin - admin}, priority={href=/api/v3/priorities/2, title=Normal}, ancestors=[]}}}, _links={self={href=/api/v3/activity/1, title=Priority changed from High to Low}, workPackage={href=/api/v3/work_packages/1, title=quis numquam qui voluptatum quia praesentium blanditiis nisi}, user={href=/api/v3/users/1, title=John Sheppard - admin}, attachments={href=/api/v3/activities/1/attachments}, emojiReactions={href=/api/v3/activities/1/emoji_reactions}, addAttachment={href=/api/v3/activities/1/attachments, method=post}, update={href=/api/v3/activities/1, method=patch}}, details=[{format=markdown, raw=Lorem ipsum dolor sit amet., html=<p>Lorem ipsum dolor sit amet.</p>}], comment={format=markdown, raw=Lorem ipsum dolor sit amet., html=<p>Lorem ipsum dolor sit amet.</p>}, createdAt=2014-05-21T08:51:20.721Z, updatedAt=2014-05-21T09:14:02.929Z, version=31}, 
                                resource = {_type=WorkPackage, _links={self={href=/api/v3/work_packages/1528, title=Develop API}, schema={href=/api/v3/work_packages/schemas/11-2}, update={href=/api/v3/work_packages/1528, method=patch, title=Update Develop API}, delete={href=/work_packages/bulk?ids=1528, method=delete, title=Delete Develop API}, logTime={href=/work_packages/1528/time_entries/new, type=text/html, title=Log time on Develop API}, move={href=/work_packages/1528/move/new, type=text/html, title=Move Develop API}, attachments={href=/api/v3/work_packages/1528/attachments}, addAttachment={href=/api/v3/work_packages/1528/attachments, method=post}, author={href=/api/v3/users/1, title=OpenProject Admin - admin}, customActions=[{href=/api/v3/work_packages/1528/custom_actions/153/execute, method=post, title=Reset}, {href=/api/v3/work_packages/1528/custom_actions/94/execute, method=post, title=Forward to accounting}], responsible={href=/api/v3/users/23, title=Laron Leuschke - Alaina5788}, relations={href=/api/v3/work_packages/1528/relations, title=Show relations}, revisions={href=/api/v3/work_packages/1528/revisions}, assignee={href=/api/v3/users/11, title=Emmie Okuneva - Adele5450}, priority={href=/api/v3/priorities/2, title=Normal}, project={href=/api/v3/portfolio/1, title=A Test Portfolio}, status={href=/api/v3/statuses/1, title=New}, type={href=/api/v3/types/1, title=A Type}, version={href=/api/v3/versions/1, title=Version 1}, availableWatchers={href=/api/v3/work_packages/1528/available_watchers}, watch={href=/api/v3/work_packages/1528/watchers, method=post, payload={user={href=/api/v3/users/1}}}, addWatcher={href=/api/v3/work_packages/1528/watchers, method=post, payload={user={href=/api/v3/users/{user_id}}}, templated=true}, removeWatcher={href=/api/v3/work_packages/1528/watchers/{user_id}, method=delete, templated=true}, addRelation={href=/api/v3/relations, method=post, title=Add relation}, changeParent={href=/api/v3/work_packages/694, method=patch, title=Change parent of Bug in OpenProject}, addComment={href=/api/v3/work_packages/1528/activities, method=post, title=Add comment}, parent={href=/api/v3/work_packages/1298, title=nisi eligendi officiis eos delectus quis voluptas dolores}, category={href=/api/v3/categories/1298, title=eligend isi}, children=[{href=/api/v3/work_packages/1529, title=Write API documentation}], ancestors=[{href=/api/v3/work_packages/1290, title=Root node of hierarchy}, {href=/api/v3/work_packages/1291, title=Intermediate node of hierarchy}, {href=/api/v3/work_packages/1298, title=nisi eligendi officiis eos delectus quis voluptas dolores}], timeEntries={href=/work_packages/1528/time_entries, type=text/html, title=Time entries}, watchers={href=/api/v3/work_packages/1528/watchers}, customField3={href=api/v3/users/14}}, id=1528, subject=Develop API, description={format=markdown, raw=Develop super cool OpenProject API., html=<p>Develop super cool OpenProject API.</p>}, scheduleManually=false, readonly=false, startDate=null, dueDate=null, derivedStartDate=null, derivedDueDate=null, estimatedTime=PT2H, derivedEstimatedTime=PT10H, percentageDone=0, customField1=Foo, customField2=42, createdAt=2014-08-29T12:40:53.373Z, updatedAt=2014-08-29T12:44:41.981Z}, ), 
                            _links = openproject_client.models.notification_model__links.NotificationModel__links(
                                self = null, 
                                read_ian = null, 
                                unread_ian = null, 
                                project = null, 
                                actor = null, 
                                resource = null, 
                                activity = null, ), )
                        ], 
                    details_schemas = [
                        openproject_client.models.schema_model.SchemaModel(
                            _type = 'Schema', 
                            _dependencies = [
                                ''
                                ], 
                            _links = openproject_client.models.schema_model__links.SchemaModel__links(
                                self = null, ), )
                        ], )
            )
        else:
            return NotificationCollectionModel(
                type = 'Collection',
                total = 0,
                count = 0,
                links = openproject_client.models.notification_collection_model_all_of__links.NotificationCollectionModel_allOf__links(
                    self = null, 
                    jump_to = null, 
                    change_size = null, ),
                embedded = openproject_client.models.notification_collection_model_all_of__embedded.NotificationCollectionModel_allOf__embedded(
                    elements = [
                        openproject_client.models.notification_model.NotificationModel(
                            _type = 'Notification', 
                            id = 1, 
                            reason = 'assigned', 
                            read_ian = True, 
                            details = [
                                openproject_client.models.values_property_model.ValuesPropertyModel(
                                    _type = 'Values::Property', 
                                    property = '', 
                                    value = '', 
                                    _links = openproject_client.models.values_property_model__links.ValuesPropertyModel__links(
                                        self = null, 
                                        schema = null, ), )
                                ], 
                            created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            updated_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            _embedded = openproject_client.models.notification_model__embedded.NotificationModel__embedded(
                                actor = null, 
                                project = null, 
                                activity = {id=1, _type=Activity::Comment, _embedded={attachments={_type=Collection, total=1, count=1, _embedded={elements=[{_type=Attachment, id=30388, fileName=Task_Ensure_financing___4___OpenProject_DEV.jpeg, fileSize=540992, description={format=plain, raw=, html=}, status=uploaded, contentType=image/jpeg, digest={algorithm=md5, hash=d02d312b25383b595a9fa10f1a8999fe}, createdAt=2025-04-08T15:37:19.275Z, _links={self={href=/api/v3/attachments/30388, title=Task_Ensure_financing___4___OpenProject_DEV.jpeg}, author={href=/api/v3/users/435, title=Firstname}, container={href=/api/v3/activities/79090}, staticDownloadLocation={href=/api/v3/attachments/30388/content}, downloadLocation={href=/api/v3/attachments/30388/content}, delete={href=/api/v3/attachments/30388, method=delete}}}]}, _links={self={href=/api/v3/activities/79090/attachments}}}, emojiReactions={_type=Collection, total=2, count=2, _embedded={elements=[{_type=EmojiReaction, id=1-thumbs_up, reaction=thumbs_up, emoji=👍, reactionsCount=3, firstReactionAt=2024-04-08T15:37:19.275Z, _links={self={href=/api/v3/emoji_reactions/1-thumbs_up}, reactable={href=/api/v3/activities/1}, reactingUsers=[{href=/api/v3/users/435, title=John Doe}, {href=/api/v3/users/436, title=Jane Smith}, {href=/api/v3/users/437, title=Bob Johnson}]}}, {_type=EmojiReaction, id=1-heart, reaction=heart, emoji=❤️, reactionsCount=1, firstReactionAt=2024-04-08T15:38:19.275Z, _links={self={href=/api/v3/emoji_reactions/1-heart}, reactable={href=/api/v3/activities/1}, reactingUsers=[{href=/api/v3/users/435, title=John Doe}]}}]}, _links={self={href=/api/v3/activities/1/emoji_reactions}}}, workPackage={_type=WorkPackage, id=10403, lockVersion=2, subject=Ensure financing, description={format=markdown, raw=Lorem ipsum dolor sit amet., html=<p>Lorem ipsum dolor sit amet.</p>}, scheduleManually=true, startDate=null, dueDate=null, derivedStartDate=null, derivedDueDate=null, estimatedTime=null, derivedEstimatedTime=null, derivedRemainingTime=null, duration=null, ignoreNonWorkingDays=false, percentageDone=null, derivedPercentageDone=null, createdAt=2025-03-24T13:11:09.480Z, updatedAt=2025-04-14T11:00:02.411Z, _links={self={href=/api/v3/work_packages/10403, title=Ensure financing}, type={href=/api/v3/types/1, title=Task}, status={href=/api/v3/statuses/1, title=New}, project={href=/api/v3/projects/918, title=RVC Test}, schema={href=/api/v3/work_packages/schemas/11-2}, author={href=/api/v3/users/1, title=OpenProject Admin - admin}, priority={href=/api/v3/priorities/2, title=Normal}, ancestors=[]}}}, _links={self={href=/api/v3/activity/1, title=Priority changed from High to Low}, workPackage={href=/api/v3/work_packages/1, title=quis numquam qui voluptatum quia praesentium blanditiis nisi}, user={href=/api/v3/users/1, title=John Sheppard - admin}, attachments={href=/api/v3/activities/1/attachments}, emojiReactions={href=/api/v3/activities/1/emoji_reactions}, addAttachment={href=/api/v3/activities/1/attachments, method=post}, update={href=/api/v3/activities/1, method=patch}}, details=[{format=markdown, raw=Lorem ipsum dolor sit amet., html=<p>Lorem ipsum dolor sit amet.</p>}], comment={format=markdown, raw=Lorem ipsum dolor sit amet., html=<p>Lorem ipsum dolor sit amet.</p>}, createdAt=2014-05-21T08:51:20.721Z, updatedAt=2014-05-21T09:14:02.929Z, version=31}, 
                                resource = {_type=WorkPackage, _links={self={href=/api/v3/work_packages/1528, title=Develop API}, schema={href=/api/v3/work_packages/schemas/11-2}, update={href=/api/v3/work_packages/1528, method=patch, title=Update Develop API}, delete={href=/work_packages/bulk?ids=1528, method=delete, title=Delete Develop API}, logTime={href=/work_packages/1528/time_entries/new, type=text/html, title=Log time on Develop API}, move={href=/work_packages/1528/move/new, type=text/html, title=Move Develop API}, attachments={href=/api/v3/work_packages/1528/attachments}, addAttachment={href=/api/v3/work_packages/1528/attachments, method=post}, author={href=/api/v3/users/1, title=OpenProject Admin - admin}, customActions=[{href=/api/v3/work_packages/1528/custom_actions/153/execute, method=post, title=Reset}, {href=/api/v3/work_packages/1528/custom_actions/94/execute, method=post, title=Forward to accounting}], responsible={href=/api/v3/users/23, title=Laron Leuschke - Alaina5788}, relations={href=/api/v3/work_packages/1528/relations, title=Show relations}, revisions={href=/api/v3/work_packages/1528/revisions}, assignee={href=/api/v3/users/11, title=Emmie Okuneva - Adele5450}, priority={href=/api/v3/priorities/2, title=Normal}, project={href=/api/v3/portfolio/1, title=A Test Portfolio}, status={href=/api/v3/statuses/1, title=New}, type={href=/api/v3/types/1, title=A Type}, version={href=/api/v3/versions/1, title=Version 1}, availableWatchers={href=/api/v3/work_packages/1528/available_watchers}, watch={href=/api/v3/work_packages/1528/watchers, method=post, payload={user={href=/api/v3/users/1}}}, addWatcher={href=/api/v3/work_packages/1528/watchers, method=post, payload={user={href=/api/v3/users/{user_id}}}, templated=true}, removeWatcher={href=/api/v3/work_packages/1528/watchers/{user_id}, method=delete, templated=true}, addRelation={href=/api/v3/relations, method=post, title=Add relation}, changeParent={href=/api/v3/work_packages/694, method=patch, title=Change parent of Bug in OpenProject}, addComment={href=/api/v3/work_packages/1528/activities, method=post, title=Add comment}, parent={href=/api/v3/work_packages/1298, title=nisi eligendi officiis eos delectus quis voluptas dolores}, category={href=/api/v3/categories/1298, title=eligend isi}, children=[{href=/api/v3/work_packages/1529, title=Write API documentation}], ancestors=[{href=/api/v3/work_packages/1290, title=Root node of hierarchy}, {href=/api/v3/work_packages/1291, title=Intermediate node of hierarchy}, {href=/api/v3/work_packages/1298, title=nisi eligendi officiis eos delectus quis voluptas dolores}], timeEntries={href=/work_packages/1528/time_entries, type=text/html, title=Time entries}, watchers={href=/api/v3/work_packages/1528/watchers}, customField3={href=api/v3/users/14}}, id=1528, subject=Develop API, description={format=markdown, raw=Develop super cool OpenProject API., html=<p>Develop super cool OpenProject API.</p>}, scheduleManually=false, readonly=false, startDate=null, dueDate=null, derivedStartDate=null, derivedDueDate=null, estimatedTime=PT2H, derivedEstimatedTime=PT10H, percentageDone=0, customField1=Foo, customField2=42, createdAt=2014-08-29T12:40:53.373Z, updatedAt=2014-08-29T12:44:41.981Z}, ), 
                            _links = openproject_client.models.notification_model__links.NotificationModel__links(
                                self = null, 
                                read_ian = null, 
                                unread_ian = null, 
                                project = null, 
                                actor = null, 
                                resource = null, 
                                activity = null, ), )
                        ], 
                    details_schemas = [
                        openproject_client.models.schema_model.SchemaModel(
                            _type = 'Schema', 
                            _dependencies = [
                                ''
                                ], 
                            _links = openproject_client.models.schema_model__links.SchemaModel__links(
                                self = null, ), )
                        ], ),
        )
        """

    def testNotificationCollectionModel(self):
        """Test NotificationCollectionModel"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
