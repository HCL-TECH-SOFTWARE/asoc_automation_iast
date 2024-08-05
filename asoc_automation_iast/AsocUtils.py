#!/usr/bin/env python3
#######################################################################################################################
# Licensed Materials –Property of HCL Technologies Ltd.
# © Copyright HCL Technologies Ltd. 2022.
# All rights reserved. See product license for details. US Government Users Restricted Rights. Use, duplication,
# or disclosure restricted by GSA ADP Schedule Contract with HCL Technologies Ltd. Java and all Java-based trademarks
# and logos are trademarks or registered trademarks of Oracle and/or its affiliates. HCL, the HCL logo,
# and Tivoli are registered trademarks of HCL Technologies in the United States, other countries, or both.
#######################################################################################################################

import inspect
import json
import logging
import time

import requests

from .IastUtils import IastException
from .RequestApi import post_request, get_request, delete_request, download_request, put_request

ASOC_IAST_API = "https://cloud.appscan.com/IAST/"
ASOC_API = "https://cloud.appscan.com/api/v4"

zip_filename = 'IASTAgent.zip'


####################################################################
# ASOC - IAST API https://stage.cloud.appscan.com/IAST/swagger/ui/
####################################################################
def url_join(*arguments):
    return '/'.join([arg.strip('/') if isinstance(arg, str) else arg for arg in arguments])


# start new execution directly from ASoC IAST interface
# request URL : POST https://cloud.appscan.com/IAST/api/StartNewExecution
#     headers: "Authorization=Bearer <accessToken>"
def start_new_execution(agent_key: str, host=ASOC_IAST_API, retries=0) -> str:
    url = url_join(host, "api/StartNewExecution")
    headers = {"Authorization": "Bearer " + agent_key}
    json_response = None
    try:
        response = post_request(url, headers=headers, timeout=30, retries=retries)
        json_response = json.loads(response.text)
        logging.info("Started new execution with id: " + json_response["ExecutionId"])
        return json_response["ExecutionId"]
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException(inspect.currentframe().f_code.co_name + "failed:" + "KeyError:" + str(e) +
                            " not in response: " + str(json_response))


# stop current execution directly from ASoC IAST interface
# request URL : POST https://cloud.appscan.com/IAST/api/StopExecution
#     headers: "Authorization=Bearer <accessToken>"
def stop_execution(agent_key: str, host=ASOC_IAST_API, retries=0) -> None:
    url = url_join(host, "/api/StopExecution")
    headers = {"Authorization": "Bearer " + agent_key}
    try:
        post_request(url, headers=headers, timeout=30, retries=retries)
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")


# Downloads zip file with IAST agent war inside - no asoc-config.json - need to set manually token
# request URL : GET https://cloud.appscan.com/IAST/api/DownloadVersion
#     headers: "Authorization=Bearer <accessToken>"
def download_agent_iast_api(agent_key: str, host=ASOC_IAST_API, retries=0) -> None:
    url = url_join(host, "/api/DownloadVersion")
    headers = {"Authorization": "Bearer " + agent_key}
    try:
        download_request(url, headers=headers, timeout=30, retries=retries)
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")


# Downloads zip file with IAST agent war inside - with asoc-config.json - ready to work
# note it will disable previous token for this scan
# request URL : GET https://cloud.appscan.com/api/V4/Tools/IastAgentWithKey
#     headers: "Authorization=Bearer <accessToken>"
def download_agent_with_key(token: str, scan_id: str, host=ASOC_API) -> None:
    url = url_join(host, "/Tools/IastAgentWithKey")
    headers = {"Accept": "text/plain", "Authorization": "Bearer " + token}
    params = {'scanId': scan_id}
    try:
        download_request(url, headers=headers, timeout=30, params=params)
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")


# Downloads zip file with IAST agent war inside - with asoc-config.json - ready to work
# note it will disable previous token for this scan
# request URL : GET https://cloud.appscan.com/api/V4/Tools/IastAgent
#     headers: "Authorization=Bearer <accessToken>"
def download_agent(token: str, agent_type: str, host=ASOC_API) -> None:
    url = url_join(host, "Tools/IastAgent")
    headers = {"Accept": "text/plain", "Authorization": "Bearer " + token}
    params = {'type': agent_type}
    try:
        download_request(url, headers=headers, timeout=30, params=params)
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")


#####################################################
# ASOC - API https://cloud.appscan.com/swagger/ui/
#####################################################

# Authenticate using the API Key ID / Secret.Return a Bearer Token used for all other REST APIs
# request URL : POST https://cloud.appscan.com/api/V4/Account/ApiKeyLogin
#    json: { "KeyId" : "aaa" , "KeySecret" : "bbb" }
def get_api_key_login(key_id, key_secret, host=ASOC_API, retries=0):
    api_key = {
        "KeyId": key_id,
        "KeySecret": key_secret
    }
    url = url_join(host, "/Account/ApiKeyLogin")
    headers = {"Accept": "application/json"}
    json_response = None
    try:
        response = post_request(url, headers=headers, json_body=api_key, retries=retries, timeout=30)
        json_response = json.loads(response.text)
        token = json_response["Token"]
        logging.info("token: " + token)
        return token
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException(inspect.currentframe().f_code.co_name + "failed:" + "KeyError:" + str(e) +
                            " not in response: " + str(json_response))


# request URL : GET https://cloud.appscan.com/api/V4/AssetGroups
#     params: "$filter=IsDefault eq true, $select=Id, $count: true"
#     headers: "Authorization=Bearer <token>"
def get_default_asset_group(token, host=ASOC_API):
    url = url_join(host, "/AssetGroups")
    params = {"$filter": "IsDefault eq true", "$select": "Id", "$count": "true"}
    headers = {"Accept": "application/json", "Authorization": "Bearer " + token}
    try:
        response = get_request(url, params=params, headers=headers, timeout=30)
        json_response = json.loads(response.text)
        if json_response["Count"] == 0:
            raise IastException("Error - No default asset group found.")
        asset_group_id = json_response["Items"][0]["Id"]
        return asset_group_id
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException(inspect.currentframe().f_code.co_name + "failed:" + "KeyError:" + str(e) +
                            " not in response: " + str(json_response))


#####################################################
# ASOC - Apps API
#####################################################
# request URL : POST https://cloud.appscan.com/api/V4/Apps
#     headers: "Authorization=Bearer <token>"
def create_app(token, app_name, asset_group, host=ASOC_API, retries=0):
    app_model = {
        "Name": app_name,
        "AssetGroupId": asset_group
    }
    url = url_join(host, "/Apps")
    headers = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Bearer " + token}
    json_response = None
    try:
        response = post_request(url, headers=headers, json_body=app_model, retries=retries, timeout=30)
        json_response = json.loads(response.text)
        app_id = json_response["Id"]
        return app_id
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException(inspect.currentframe().f_code.co_name + " failed:" + "KeyError:" + str(e) +
                            " not in response: " + str(json_response))


# request URL : GET https://cloud.appscan.com/api/V4/Apps
#     headers: "Authorization=Bearer <token>"
#     params: "$filter: Id eq <appId>"
def get_app_name_by_id(app_id, token, host=ASOC_API):
    url = url_join(host, "/Apps")
    headers = {"Accept": "application/json", "Authorization": "Bearer " + token}
    params = {"$filter": f"Id eq {app_id}"}
    try:
        response = get_request(url, params=params, headers=headers, timeout=30)
        json_response = json.loads(response.text)
        app_name = json_response["Items"][0]["Name"]
        return app_name
    except IastException as e:
        if 'Client Error: 400' in str(e):
            return None
        else:
            raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException(inspect.currentframe().f_code.co_name + " failed:" + "KeyError:" + str(e) +
                            " not in response: " + str(json_response))


# request URL : GET https://cloud.appscan.com/api/V4/Apps
#     headers: "Authorization=Bearer <token>"
#     params: "$filter=Name eq <appName>, $select=Id, , $count: true"
def get_app_id_by_name(app_name, token, host=ASOC_API):
    url = url_join(host, "/Apps")
    headers = {"Accept": "application/json", "Authorization": "Bearer " + token}
    params = {"$filter": f"Name eq '{app_name}'", "$select": "Id", "$count": "true"}
    try:
        response = get_request(url, params=params, headers=headers, timeout=30)
        json_response = json.loads(response.text)
        if json_response["Count"] == 0:
            return None
        app_id = json_response["Items"][0]["Id"]
        return app_id
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException(inspect.currentframe().f_code.co_name + " failed:" + "KeyError:" + str(e) +
                            " not in response: " + str(json_response))


# request URL : DELETE https://cloud.appscan.com/api/V4/Apps/<app_id>
#     headers: "Authorization=Bearer <token>"
#     params: "id=<appId>"
def delete_app(app_id, token, host=ASOC_API, retries=0):
    url = url_join(host, "Apps", app_id)
    headers = {"Accept": "text/plain", "Authorization": "Bearer " + token}
    try:
        delete_request(url, headers=headers, retries=retries, timeout=60)
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")


#####################################################
# ASOC - scan API
#####################################################
# request URL : POST https://cloud.appscan.com/api/V4/Scans/Iast
#     headers: "Authorization=Bearer <token>, Accept: application/json, Content-Type: application/json"
#     json: {
#         "ConnLostStopTimer": "",
#         "ScanName": <scanName>,
#         "EnableMailNotification": True,
#         "Locale": "en-US",
#         "AppId": <appId>,
#         "Personal": False,
#         "AgentType": "Java" - one of: Java, DotNet, NodeJS
#     }
def create_scan(app_id, token, scan_name, host=ASOC_API, retries=0, is_personal=False, agent_type='Java',
                config_file_id=None, stop_scan=1000, enable_email_notification=False):
    scan_model = {
        "ConnLostStopTimer": stop_scan,  # Timeout in minutes to stop scan after agent connection lost
        "ScanName": scan_name,
        "EnableMailNotification": enable_email_notification,
        "Locale": "en-US",
        "AppId": app_id,
        "Personal": is_personal,
        "AgentType": agent_type,
    }
    if config_file_id != None:
        scan_model.update({"ConfigFileId": config_file_id})
    url = url_join(host, "/Scans/Iast")
    headers = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Bearer " + token}
    json_response = None
    try:
        response = post_request(url, headers=headers, json_body=scan_model, retries=retries, timeout=60)
        json_response = json.loads(response.text)
        agent_key = json_response["Agentkey"]
        scan_id = json_response["Id"]
        logging.info("agent_key: " + agent_key)
        logging.info("scan_id: " + scan_id)
        return agent_key, scan_id
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException(inspect.currentframe().f_code.co_name + " failed:" + "KeyError:" + str(e) +
                            " not in response: " + str(json_response))


# request URL : GET https://cloud.appscan.com/api/V4/Scans
#     headers: "Authorization=Bearer <token>"
#     params: "$filter: Id eq <scanId>"
def get_scan_info_by_id(scan_id, token, host=ASOC_API):
    url = url_join(host,  "/Scans")
    headers = {"Accept": "application/json", "Authorization": "Bearer " + token}
    params = {"$filter": f"Id eq {scan_id}"}
    try:
        response = get_request(url, params=params, headers=headers, timeout=30)
        json_response = json.loads(response.text)
        scan_name = json_response["Name"]
        app_name = json_response["AppName"]
        app_id = json_response["AppId"]
        return scan_name, app_name, app_id
    except IastException as e:
        if 'Client Error: 400' in str(e):
            return None
        else:
            raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException("KeyError:" + str(e) + " not in response: " + str(json_response))


# request URL : GET https://cloud.appscan.com/api/V4/Scans
#     headers: "Authorization=Bearer <token>"
#     params: "$filter: Id eq <scanName>, $count: true"
def get_scan_info_by_name(scan_name, token, host=ASOC_API):
    url = url_join(host, "Scans")
    headers = {"Accept": "application/json", "Authorization": "Bearer " + token}
    params = {"$filter": f"Name eq '{scan_name}'", "$count": "true"}
    try:
        response = get_request(url, params=params, headers=headers, timeout=30)
        json_response = json.loads(response.text)
        if json_response["Count"] == 0:
            return None, None, None
        scan_id = json_response["Items"][0]["Id"]
        app_name = json_response["Items"][0]["AppName"]
        app_id = json_response["Items"][0]["AppId"]
        return scan_id, app_name, app_id
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException(inspect.currentframe().f_code.co_name + " failed:" + "KeyError:" + str(e) +
                            " not in response: " + str(json_response))


# request URL : GET https://cloud.appscan.com/api/V4/Scans
#     headers: "Authorization=Bearer <token>"
#     params: "$select=<Id>, $count: true"
def get_scans(token, host=ASOC_API):
    url = url_join(host, "/Scans")
    headers = {"Accept": "application/json", "Authorization": "Bearer " + token}
    params = {"$select": "Id", "$count": "true"}
    try:
        response = get_request(url, params=params, headers=headers, timeout=30)
        json_response = json.loads(response.text)
        return json_response
    except IastException as e:
        if 'Client Error: 400' in str(e):
            return None
        else:
            raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException("KeyError:" + str(e) + " not in response: " + str(json_response))


# request URL : GET https://https://cloud.appscan.com/api/v4/Apps/<app_id>/Scans
#     headers: "Authorization=Bearer <token>"
#     params: "$select=<Id>, $count: true"
def get_scans_for_app(token, app_id, host=ASOC_API):
    url = url_join(host, "Apps", app_id, "Scans")
    headers = {"Accept": "application/json", "Authorization": "Bearer " + token}
    params = {"$select": "Id", "$count": "true"}
    try:
        response = get_request(url, params=params, headers=headers, timeout=30)
        json_response = json.loads(response.text)
        return json_response
    except IastException as e:
        if 'Client Error: 400' in str(e):
            return None
        else:
            raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException("KeyError:" + str(e) + " not in response: " + str(json_response))


# request URL : DELETE https://cloud.appscan.com/api/V4/Scans/<scan_id>
#     headers: "Authorization=Bearer <token>"
#     params: "scanId=<scanId>, deleteIssues=True"
def delete_scan(scan_id, token, host=ASOC_API, retries=0):
    if scan_id is not None:
        url = url_join(host, "Scans", scan_id)
        headers = {"Accept": "text/plain", "Authorization": "Bearer " + token}
        params = {"deleteIssues": True}
        try:
            delete_request(url, headers=headers, params=params, retries=retries, timeout=60)
        except IastException as e:
            raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")


# request URL : POST https://cloud.appscan.com/api/V4/Scans/NewIASTKey/<scan_id>
#     headers: "Authorization=Bearer <token>"
#     params: "scanId=<scanId>"
def get_new_iast_key_for_scan(scan_id, token, host=ASOC_API):
    url = url_join(host, "/Scans/NewIASTKey/", scan_id)
    headers = {"Accept": "application/json", "Authorization": "Bearer " + token}
    try:
        response = post_request(url, headers=headers, timeout=30)
        json_response = json.loads(response.text)
        key = json_response["Key"]
        return key
    except IastException as e:
        if 'Client Error: 400' in str(e):
            return None
        else:
            raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException("KeyError:" + str(e) + " not in response: " + str(json_response))


# request URL : POST https://cloud.appscan.com/api/v4/FileUpload
#     headers: "Authorization=Bearer <token>"
#     params: "uploadedFile=<filePath>"
def upload_file(token, file_to_upload, host=ASOC_API, timeout=60, retries=2):
    url = url_join(host, "/FileUpload")
    headers = {"Authorization": "Bearer " + token, "Accept": "text/plain"}
    json_response = ""
    try:
        with open(file_to_upload, "rb") as file:
            response = post_request(url, headers=headers, files={"uploadedFile": file}, timeout=timeout, retries=retries)
        json_response = json.loads(response.text)
        file_id = json_response["FileId"]
        return file_id
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException(inspect.currentframe().f_code.co_name + " failed:" + "KeyError:" + str(e) +
                            " not in response: " + str(json_response))


# request URL : PUT https://cloud.appscan.com/api/v4/Scans/UpdateIastScan/{scanId}
#     headers: "Authorization=Bearer <token>"
#     params: "scanId=<scanId>, scanData=<scanData>"
def update_iast_scan(scan_id, token, file_id, host=ASOC_API, retries=0):
    scan_model = {
        "ConfigFileId": file_id
    }
    url = url_join(host, "Scans", "UpdateIastScan", scan_id)
    headers = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Bearer " + token}
    try:
        put_request(url, headers=headers, params={"scanId": scan_id}, json_body=scan_model, retries=retries, timeout=30)
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")

#####################################################
# ASOC - report API https://cloud.appscan.com/swagger/ui/
#####################################################


# starts a report creation
# request URL : POST https://cloud.appscan.com/api/V4/Reports/Security/<scope>/<id>
#     headers: "Authorization=Bearer <token>"
#     params: "scope=Scan, id=<scanId>"
#     json: {
#         "Summary": True,
#         "Details": True,
#         "Discussion": False,
#         "Overview": False,
#         "TableOfContent": True,
#         "Advisories": False,
#         "FixRecommendation": False,
#         "History": True,
#         "IsTrialReport": True,
#         "ReportFileType": Xml
#     }
def create_report(scan_id, token, host=ASOC_API):
    # url
    scope = "Scan"  # one of: Application/Scan/ScanExecution (ScanExecution not supported)
    url = url_join(host, "/Reports/Security/", scope, scan_id)

    # headers
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json", "Accept": "text/plain"}

    # body
    report_type = "Xml"  # one of: Xml/Html/Pdf - xml is quick, html slower, pdf VERY slow
    configuration = {
        "Summary": True,
        "Details": True,
        "Discussion": False,
        "Overview": False,
        "TableOfContent": True,
        "Advisories": False,
        "FixRecommendation": False,
        "History": True,
        "IsTrialReport": True,
        "ReportFileType": report_type
    }
    body = {"Configuration": configuration}
    json_response = None
    try:
        response = post_request(url, json_body=body, headers=headers, timeout=30)
        json_response = json.loads(response.text)
        print(json_response)
        logging.info("report id: " + json_response["Id"])
        return json_response["Id"]
    except IastException as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException(inspect.currentframe().f_code.co_name + " failed:" + "KeyError:" + str(e) +
                            " not in response: " + str(json_response))


# returns the status of report preparation
# request URL : GET https://cloud.appscan.com/api/V4/Reports
#     headers: "Authorization=Bearer <token>"
#     params: "$filter: Id eq <reportId>"
def get_report_status(report_id, token, host=ASOC_API):
    url = url_join(host, "/Reports")
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    params = {"$filter": f"Id eq {report_id}"}
    json_response = None
    try:
        response = get_request(url, headers=headers, params=params, timeout=60)
        json_response = json.loads(response.text)
        print(json_response)
        report_status = json_response["Items"][0]["Status"]
        logging.info("report status: " + report_status)
        if report_status == 'failed':
            raise IastException("Report creation failed!")
        return report_status
    except requests.exceptions.HTTPError as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
    except KeyError as e:
        raise IastException(inspect.currentframe().f_code.co_name + " failed:" + "KeyError:" + str(e) +
                            " not in response: " + str(json_response))


# polls asoc until report is ready
def wait_for_report_ready(report_id, token, max_retries=100, host=ASOC_API):
    counter = max_retries
    while counter > 0:
        report_status = get_report_status(report_id=report_id, token=token, host=host)
        if report_status == 'Ready':
            return
        if report_status == 'Failed':
            raise IastException(inspect.currentframe().f_code.co_name + " failed:" + "asoc report generation failed")
        time.sleep(2)
        counter -= 1
    raise IastException(inspect.currentframe().f_code.co_name + " failed:" + "Timed out waiting for report ready")


# returns the status of report preparation
# request URL : GET https://cloud.appscan.com/api/V4/Reports/<report_id>/Download
#     headers: "Authorization=Bearer <token>"
#     params: "id=<reportId>"
def download_report(report_id, token, host=ASOC_API):
    url = url_join(host, "/Reports/", report_id, "/Download")
    headers = {"Authorization": "Bearer " + token, "Accept": "text/plain"}
    try:
        response = get_request(url, headers=headers, stream=False, timeout=30)
        report = ""
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                #  report.append(chunk)
                report += chunk.decode("utf-8")
        return report
    except requests.exceptions.HTTPError as e:
        raise IastException(f"{inspect.currentframe().f_code.co_name} failed: {str(e)}")
