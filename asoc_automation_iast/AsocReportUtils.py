#!/usr/bin/env python3
#######################################################################################################################
# Licensed Materials –Property of HCL Technologies Ltd.
# © Copyright HCL Technologies Ltd. 2022.
# All rights reserved. See product license for details. US Government Users Restricted Rights. Use, duplication,
# or disclosure restricted by GSA ADP Schedule Contract with HCL Technologies Ltd. Java and all Java-based trademarks
# and logos are trademarks or registered trademarks of Oracle and/or its affiliates. HCL, the HCL logo,
# and Tivoli are registered trademarks of HCL Technologies in the United States, other countries, or both.
#######################################################################################################################

import json
from typing import Any

import requests

from IastUtils import IastException
from RequestApi import post_request, get_request, delete_request, download_request, put_request


#####################################################
# Report API
#####################################################

# Swagger: https://cloud.appscan.com/swagger/ui/index#!/Issues/Issues_GetIssuesForScopeByScopeAndScopeid
# request URL : POST https://cloud.appscan.com/api/V2/Issues/Scan/<scan_id>
#     headers: "Authorization=Bearer <token>, Accept=application/json"
#     params: "$select=AsmHash,IssueType,Id, $inlinecount=allpages"
def get_issues_for_scan(scan_id, token, host) -> Any:
    url = host + "/Issues/Scan/" + scan_id
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    params = {"$select": "AsmHash,IssueTypeId,Id,Path,ScanName,ApplicationId,Api,SourceFile", "$inlinecount": "allpages"}
    try:
        response = get_request(url, headers=headers, stream=False, params=params, timeout=30)
        json_response = json.loads(response.text)
        return json_response
    except requests.exceptions.Timeout:
        print(f"request to {url} timed out.")
        return json.dumps({"Count": 0, "Items": {}})
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidSchema) as e:
        print(f"request to {url} failed with connection error: {str(e)}")
        return json.dumps({"Count": 0, "Items": {}})
    except requests.exceptions.HTTPError as e:
        raise IastException(e)


# Swagger: https://cloud.appscan.com/swagger/ui/index#!/Issues/Issues_GetIssuesForScopeByScopeAndScopeid
# request URL : POST https://cloud.appscan.com/api/V2/Issues/ScanExecution/<execution_id>
#     headers: "Authorization=Bearer <token>, Accept=application/json"
#     params: "$select=AsmHash,IssueType,Id, $inlinecount=allpages"
def get_issues_for_execution(execution_id, token, host):
    url = host + "/Issues/ScanExecution/" + execution_id
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    params = {"$select": "AsmHash,IssueTypeId,Id,Path,Api", "$inlinecount": "allpages"}
    try:
        response = get_request(url, headers=headers, stream=False, params=params, timeout=30)
        json_response = json.loads(response.text)
        return json_response
    except requests.exceptions.HTTPError as e:
        raise IastException(e)


# Swagger: https://cloud.appscan.com/swagger/ui/index#!/Issues/Issues_GetIssueById
# request URL : POST https://cloud.appscan.com/api/V2/Issues/<issue_id>
#     headers: "Authorization=Bearer <token>, Accept=application/json"
def get_issue(issue_id, token, host):
    url = host + "/Issues/" + issue_id
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    try:
        response = get_request(url, headers=headers, stream=False, timeout=30)
        json_response = json.loads(response.text)
        return json_response
    except requests.exceptions.HTTPError as e:
        raise IastException(e)


# Swagger: https://cloud.appscan.com/swagger/ui/index#!/Issues/Issues_Artifacts
# request URL : POST https://cloud.appscan.com//api/v2/Issues/{issueId}/Artifacts
#     headers: "Authorization=Bearer <token>, Accept=text/xml"
def get_issue_details_from_asoc(issue_id, token, host):
    url = host + "/Issues/" + issue_id + "/Artifacts"
    headers = {"Authorization": "Bearer " + token, "Accept": "text/xml"}
    try:
        response = get_request(url, headers=headers, stream=False, timeout=30)
        return response.content.decode("utf-8")
    except requests.exceptions.HTTPError as e:
        raise IastException(e)


# Swagger: https://cloud.appscan.com/swagger/ui/index#!/Apps/Apps_GetApps
# request URL : POST https://cloud.appscan.com/api/V2/Apps
#     headers: "Authorization=Bearer <token>, Accept=application/json"
#     params:  "$filter=Name ne 'IAST-testing'&$orderby=TotalIssues&$select=Name,Id"
def get_apps(token, host):
    url = host + "/Apps"
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    params = {"$filter": "Name ne 'IAST-testing'", "$orderby": "TotalIssues", "$select": "Name,Id"}
    try:
        response = get_request(url, headers=headers, stream=False, params=params, timeout=30)
        json_response = json.loads(response.text)
        return json_response
    except requests.exceptions.HTTPError as e:
        raise IastException(e)
