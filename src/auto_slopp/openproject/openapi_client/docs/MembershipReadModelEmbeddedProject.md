# MembershipReadModelEmbeddedProject


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**id** | **int** | Portfolios&#39; id | [optional] 
**identifier** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**active** | **bool** | Indicates whether the portfolio is currently active or already archived | [optional] 
**favorited** | **bool** | Indicates whether the portfolio is favorited by the current user | [optional] 
**status_explanation** | [**Formattable**](Formattable.md) | A text detailing and explaining why the portfolio has the reported status | [optional] 
**public** | **bool** | Indicates whether the portfolio is accessible for everybody | [optional] 
**description** | [**Formattable**](Formattable.md) |  | [optional] 
**created_at** | **datetime** | Time of creation. Can be writable by admins with the &#x60;apiv3_write_readonly_attributes&#x60; setting enabled. | [optional] 
**updated_at** | **datetime** | Time of the most recent change to the portfolio | [optional] 
**links** | [**PortfolioModelAllOfLinks**](PortfolioModelAllOfLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.membership_read_model_embedded_project import MembershipReadModelEmbeddedProject

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipReadModelEmbeddedProject from a JSON string
membership_read_model_embedded_project_instance = MembershipReadModelEmbeddedProject.from_json(json)
# print the JSON string representation of the object
print(MembershipReadModelEmbeddedProject.to_json())

# convert the object into a dict
membership_read_model_embedded_project_dict = membership_read_model_embedded_project_instance.to_dict()
# create an instance of MembershipReadModelEmbeddedProject from a dict
membership_read_model_embedded_project_from_dict = MembershipReadModelEmbeddedProject.from_dict(membership_read_model_embedded_project_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


