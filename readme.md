# asoc_automation_iast
This repository includes two python scripts and a python library to facilitate automation of working with AppScan IAST product.
Find out more about the [AppScan IAST solution](https://s3.amazonaws.com/help.hcltechsw.com/appscan/ASoC/appseccloud_scanning_IAST_main.html).

## ConfigureIastAgent.py

### Description:
  Downloads an IAST agent that communicates with ASoC.  
  The IAST agent communicates with ASoC using an agent key, unique to every IAST scan.
  This agent key is automatically embedded inside the downloaded IAST agent. 
   
  Each IAST agent is associated with a single IAST scan, which is configured in a application in ASoC.
  It is possible to connect multiple agents to a single IAST scan. 
  Based on user input, the script can perform the following actions:
  * Associate the IAST agent with an existing scan.
  * Create a new scan for the IAST agent, associated to an existing application.
  * Create a new application and a new scan for the IAST agent.
  
  The result is `IASTAgent.zip` file, with the IAST agent deployment file `Secagent.war` inside. Information about deploying the agent can be found [here](https://s3.amazonaws.com/help.hcltechsw.com/appscan/ASoC/IAST_Deploy.html).

### Usage: 
`ConfigureIastAgent.py --id=value --secret=value [--app_id=value --app_name=value --scan_id=value --scan_name=value --asset_group=value --war_path=value --to_file=value --host=host_url --host=host_url]`

###### id: 
key id (required)

###### secret: 
key secret (required)

**NOTE**: KeyId/KeySecret pair can be obtained in the [ASoC UI](https://cloud.appscan.com/AsoCUI/serviceui/main/myapps/portfolio), in the settings section. See more information [here](https://help.hcltechsw.com/appscan/ASoC/appseccloud_rest_apis.html#ent_rest_apis).

###### app_id: 
Application id. If an application with such an id exists, it will be used, otherwise, the script will exit with an error. Use either app_name or app_id. (optional)

###### app_name: 
Application name. If an application with such a name exists, it will be used, otherwise, the script will create a new application with the specified name. If not present, a generated name will be used. (optional)

###### scan_id: 
Scan id to use. If a scan with such an id exists, it will be used, otherwise, the script will exit with an error. Use either scan_name or scan_id.(optional)

**IMPORTANT NOTE**: Using an existing scan will create a new access token, which will invalidate existing agents that are associated with the same scan
 
###### scan_name: 
Scan name. If a scan with such a name exists, it will be used, otherwise, the script will create a new scan with the specified name. If not present, a generated name will be used. (optional)  

**IMPORTANT NOTE**: Using an existing scan will create a new access token, which will invalidate existing agents that are associated with the same scan 

###### asset_group: 
Asset group to use for generating an application. If not specified, the organization's default asset group will be used. If an existing application is provided, this value is ignored. (optional)

###### war_path: 
Path to download the Secagent.war. If not specified, the current directory will be used. (optional)

###### host:
ASoC host url. If not specified, the default value will be ASoc US. (optional)

###### Examples: 
--host=https://cloud.appscan.com/,

--host=https://eu.cloud.appscan.com/

--host=https://as360.example.com,

### Examples:
```ConfigureIastAgent.py --id=abcd --secret=efgh --host=host_url```  
A new application and a new IAST scan will be generated.

```ConfigureIastAgent.py --id=abcd --secret=efgh --app_id=12345 --host=host_url```  
A new IAST scan will be generated, associated with an existing app with id 12345.

```ConfigureIastAgent.py --id=abcd --secret=efgh  --app_name=my-app --host=host_url``` 
A new IAST scan will be generated, if an application named my-app exists, it will be associated with it. Otherwise, a new application named my-app will be created, associated with the default asset group.

```ConfigureIastAgent.py --id=abcd --secret=efgh --app_name=my-app --asset_group=67890 --host=host_url```  
A new IAST scan will be generated, if an application named my-app exists, it will be associated with it. Otherwise, a new application named my-app will be created, associated with asset group 67890.

```ConfigureIastAgent.py --id=abcd --secret=efgh --asset_group=67890 --host=host_url```  
A new application with generated name will be created, associated to asset group 67890.

```ConfigureIastAgent.py --id=abcd --secret=efgh --scan_id=12345 --host=host_url```  
scan with id 12345 will be used. 

```ConfigureIastAgent.py --id=abcd --secret=efgh --scan_name=my-scan --host=host_url```  
If a scan named my-scan exists, it will be used. Otherwise, a new application with generated name, and a new scan named my-scan will be created.

```ConfigureIastAgent.py --id=abcd --secret=efgh --scan_name=my-scan --app_id=12345 --host=host_url```  
If a scan named my-scan exists, it will be used. Otherwise, a new application named my-scan will be created, associated with app 12345.

```ConfigureIastAgent.py --id=abcd --secret=efgh --scan_name=my-scan --app_id=12345 --host=host_url```  
If a scan named my-scan exists, it will be used. Otherwise, a new application named my-scan will be created, associated with app 12345.

### asoc-config.json
The access token used to communicate with ASoC is saved in the downloaded IAST agent war file in the following format:
```json
{
    "accessToken": "1234abcd567890efghijk=-"
}
```

## AddAgentKeyToWar.py

### Description
The script adds a given ASoC agent key to a given war file.  
It is useful when creating a scan and choosing to get `key only` in the `Download Options` step, or when generating a new agent key to an existing scan.
It is not required when downloading an IAST agent using ConfigureIastAgent.py. 


### Usage
`AddAgentKeyToWar.py --war=<path/to/war> --key=access_token --host=host_url`
