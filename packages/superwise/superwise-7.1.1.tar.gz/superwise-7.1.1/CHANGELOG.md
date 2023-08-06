# Changelog
Here you will find a changelog of all the SDK releases.

## [7.1.1] 2022-08-09
- Added support for on-prem environment with all functions available

## [7.0.1] 2022-07-17
- Added support for on-prem environment

## [7.0.0] 2022-05-12
- Model - support Project
- Project - added Project

## [6.5.1] 2022-05-23
- loosen required packages range
- skip pandas 1.3.* during installation [(astype datetime object deprecation)](https://pandas.pydata.org/pandas-docs/dev/whatsnew/v1.3.0.html#:~:text=Deprecated%20the%20astype()%20method%20of%20datetimelike%20(timedelta64%5Bns%5D%2C%20datetime64%5Bns%5D%2C%20Datetime64TZDtype%2C%20PeriodDtype)%20to%20convert%20to%20integer%20dtypes%2C%20use%20values.view(...)%20instead%20(GH38544).%20This%20deprecation%20was%20later%20reverted%20in%20pandas%201.4.0.)

## [6.5.0] 2022-05-04
- Transaction - support for metadata

## [6.4.8] 2022-05-11
- Add default Feature importance mapping

## [6.3.7] 2022-05-04
- Add the ability to create,get byt id, get by name, delete Project

## [6.3.6] 2022-05-04
- Transaction - support for metadata

## [6.3.3] 2022-04-25
- Change Segment definition to support OR condition between conditions

## [6.3.2] 2022-04-24
- Add validate_dtypes function in EntitiesValidator
- Refactor error messages

## [6.3.1] 2022-04-19
- Add model_id and model_id as params to transaction.log_* functions
- Add support for archive model

## [6.2.7] 2022-04-10
- Support for uploading a file from a local machine

## [6.2.6] 2022-03-20
- Support for rename/update object
- Cleanup

## [6.1.1] 2022-03-22
- Add the ability to create policy from a template

## [6.2.0] 2022-03-20
- Add support for delete a model

## [6.1.0] 2022-03-20
- Add the ability to create email notification channel.
- Add the ability to get notification channel by name.

## [6.0.10] 2022-02-27
- Model creation - monitor_delay deprecation warning.

## [6.0.9] 2022-02-21
- Transaction now also support passing version_id, added
  deprecation warnings about passing version_name

## [6.0.8] 2022-02-03
- Model schema now supports active_version_id from BE

## [6.0.7] 2022-02-07
This release has breaking changes
- Some SDK improvements:
  1. improve validation when creating a segment
  2. improve SDK install
  3. better exception when numeric column contain inf / -inf values
  4. support for upper case in features names
  5. change segment creation parameters to be more consistent with other models

## [6.0.2] 2022-01-17
Bug fix - typo in model response parsing (is_archived flag)

## [6.0.1] 2022-01-17
This release has breaking changes
- Change Task api to Model.
  1. superwise.task -> superwise.model
  2. task_id fields changed to model_id

## [5.3.5] 2022-01-06
- Bug fix - log transaction path

## [5.3.4] 2021-12-23
- Better error handling, remove code duplications in _check_res and parse_response functions
- Imrprove docstrings

## [5.3.1] 2021-12-22
- Changed requirments.txt file to have better and more flexible versioning.
- Improve docstrings for better API documentation

## [5.2.15] 2021-12-22
This release does not have any breaking changes.
This release optimize the transaction log from s3 method

## [5.2.0] 2021-12-14
This release has breaking changes
- added get_by_name support for task and version
- Changed DataEntityRole enum to DataTypesRoles
- support for suppling DataEntityRole as enum object
-
- few bug fixes and small improvements
- improve docstrings

## [5.1.1] 2021-12-14
Added support for infer dtypes

## [5.0.3] 2021-12-14
This release does not have any breaking changes.
This release adds an SDK reference guide to our SDK.

## [5.0.1] 2021-12-01
This release has breaking changes - change schema creation mechanism
- Drop support for data_entity.generate_summary() and replace with improved data_entity.summarise()
- Drop support for upload models using baseline_files list of files
- Improved feature importance feature: new parameters in summarize():
  - importance_sample - a float value, used to sample the data while calculate the Feature importance
  - importance_target_label - an option to pass a label field name
- Remove deprecated task as a param to EntitiesValidator

## [4.2.3] 2021-12-07
- fix bug in binning for numeric features with null values

## [4.2.2] 2021-12-01
- Change the binning mechanism for numeric data entities

## [4.1.0] 2021-11-28
This release has breaking changes - add functionality for transaction:
- add functionality to upload data from s3 to superwise
- add functionality to upload data from gcs to superwise

## [4.0.0] 2021-11-23
This release has breaking changes - task changed following properties:
- task_description &rarr; description
- title &rarr; name
- task_type &rarr; removed

## [3.2.0] - 2021-11-16
This release has breaking changes.
Refactor tasks model

## [3.1.2] - 2021-11-15
Improve requirements.txt - lock versions and added jwt as a requirement.

remove DEBUG mode

log.debug added for each API call

## [3.1.0] - 2021-11-11
This release has breaking changes.
removed client_name as a param from superwise object

## [3.0.0] - 2021-10-19
This release has breaking changes.
We define new entity named transaction, which responsible to manage all the data send to superwise.

### Added
- Add Class Transaction, which have 2 methods to send data to superwise (file , batch).

### Removed
- Removed Data Class and send_file methods, for send data to superwise you should use the Transaction class.
