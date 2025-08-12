# AsocReportUtils.py

This module provides utility functions for interacting with the AppScan on Cloud (ASoC) API, specifically for retrieving scan issues, issue details, and application information.

## Features

- Fetch issues for a specific scan or scan execution.
- Retrieve details for a specific issue.
- List applications, excluding test applications.

## Usage

Import the required functions in your Python code:

```python
from asoc_automation_iast.AsocReportUtils import (
    get_issues_for_scan,
    get_issues_for_execution,
    get_issue,
    get_issue_details_from_asoc,
    get_apps
)
```

Each function requires authentication (`token`) and the ASoC API `host` URL.

## Example

```python
issues = get_issues_for_scan(scan_id, token, host)
issue_details = get_issue_details_from_asoc(issue_id, token, host)
apps = get_apps(token, host)
```

## Error Handling

Exceptions from the `requests` library are caught and handled. Custom exceptions are raised using `IastException` for HTTP errors.

## License

Licensed Materials – Property of HCL Technologies Ltd.

---

# AsocUtils.py

This module contains utility functions for managing applications, scans, agents, and reports in AppScan on Cloud (ASoC) via its REST API.

## Features

- Authenticate and obtain API tokens.
- Create, delete, and query applications and scans.
- Download IAST agents and agent configurations.
- Upload files and update scan configurations.
- Generate and download security reports.
- Poll for report status and handle report generation.

## Usage

Import the required functions in your Python code:

```python
from asoc_automation_iast.AsocUtils import (
    get_api_key_login,
    create_app,
    get_app_id_by_name,
    create_scan,
    get_scan_info_by_id,
    get_scans,
    delete_scan,
    create_report,
    wait_for_report_ready,
    download_report,
    # ...other functions as needed
)
```

## Example

```python
token = get_api_key_login(key_id, key_secret)
app_id = create_app(token, "MyApp", asset_group_id)
agent_key, scan_id = create_scan(app_id, token, "MyScan")
report_id = create_report(scan_id, token)
wait_for_report_ready(report_id, token)
report_content = download_report(report_id, token)
```

## Error Handling

Functions raise `IastException` for API errors and handle common issues such as missing keys or failed requests.

## License

Licensed Materials – Property of HCL Technologies Ltd.

---

# IastUtils.py

This module provides utility functions to manage config files.

## Features

- Create/remove asoc config 
- Read user config
- Add user config to war
- Get token from user config
- Defines the `IastException` class for custom exception handling.
- Provides helper functions for logging and error reporting.

## Usage

- Import the required functions in your Python code:

```python
from asoc_automation_iast.IastUtils import (
    create_asoc_config_file,
    remove_asoc_config_file,
    read_existing_user_config,
    add_user_config_to_war,
    get_token_from_configfile
)
```
- Import the exception class to handle errors from ASoC API calls:

```python
from asoc_automation_iast.IastUtils import IastException

try:
    # some ASoC API call
except IastException as e:
    print("Error:", e)
```

## Example

```python
token = get_token_from_configfile()
remove_asoc_config_file()
create_asoc_config_file(agent_key)
file = read_existing_user_config(path_to_existing_file)
add_user_config_to_war(path_to_war)
```

## License

Licensed Materials – Property of HCL Technologies Ltd.

---

# RequestApi.py

This module abstracts HTTP request logic for interacting with the ASoC REST API.

## Features

- Provides wrapper functions for HTTP GET, POST, PUT, DELETE, and file download requests.
- Handles retries, timeouts, and error handling for API calls.

## Usage

Import and use the request functions in your modules:

```python
from asoc_automation_iast.RequestApi import (
    get_request,
    post_request,
    put_request,
    delete_request,
    download_request
)

response = get_request(url, headers=headers, params=params)
```
