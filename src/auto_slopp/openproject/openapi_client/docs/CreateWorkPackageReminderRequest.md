# CreateWorkPackageReminderRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**remind_at** | **datetime** | The date and time when the reminder is due | 
**note** | **str** | The note of the reminder | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.create_work_package_reminder_request import CreateWorkPackageReminderRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateWorkPackageReminderRequest from a JSON string
create_work_package_reminder_request_instance = CreateWorkPackageReminderRequest.from_json(json)
# print the JSON string representation of the object
print(CreateWorkPackageReminderRequest.to_json())

# convert the object into a dict
create_work_package_reminder_request_dict = create_work_package_reminder_request_instance.to_dict()
# create an instance of CreateWorkPackageReminderRequest from a dict
create_work_package_reminder_request_from_dict = CreateWorkPackageReminderRequest.from_dict(create_work_package_reminder_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


