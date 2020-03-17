#######################################################################################################################
# Licensed Materials –Property of HCL Technologies Ltd.
# © Copyright HCL Technologies Ltd. 2020.
# All rights reserved. See product license for details. US Government Users Restricted Rights. Use, duplication,
# or disclosure restricted by GSA ADP Schedule Contract with HCL Technologies Ltd. Java and all Java-based trademarks
# and logos are trademarks or registered trademarks of Oracle and/or its affiliates. HCL, the HCL logo,
# and Tivoli are registered trademarks of HCL Technologies in the United States, other countries, or both.
#######################################################################################################################
import requests
from .IastUtils import IastException

default_num_of_retries = 80
retry_wait_time = 5


def get_request(url, params=None, headers=None, timeout=5, stream=False, retries=0):
    if headers is None:
        headers = {}
    if params is None:
        params = {}
    print_url(url, params, 'GET')
    error = None
    response = None
    try:
        response = requests.get(url, verify=False, params=params, headers=headers, timeout=timeout, stream=stream)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        error = f"request to {url} timed out."
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidSchema) as e:
        error = f"request to {url} failed with connection error: {str(e)}"
    except requests.exceptions.TooManyRedirects:
        error = "Too many redirects!"
    except requests.exceptions.HTTPError as e:
        error = str(e) + " : " + response.content.decode('utf-8')
    if error is not None:
        if retries > 0:
            print(error + ". Retrying request.")
            get_request(url, params=params, headers=headers, timeout=timeout, stream=stream, retries=retries - 1)
        else:
            raise IastException(error)
    else:
        return response


def post_request(url, params=None, headers=None, json_body=None, data=None, files=None, timeout=5, retries=0):
    if headers is None:
        headers = {}
    if params is None:
        params = {}
    print_url(url, params, 'POST')
    error = None
    response = None
    try:
        response = requests.post(
            url, verify=False, params=params, headers=headers, json=json_body, data=data, files=files, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        error = f"request to {url} timed out."
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidSchema) as e:
        error = f"request to {url} failed with connection error: {str(e)}"
    except requests.exceptions.TooManyRedirects:
        error = "Too many redirects!"
    except requests.exceptions.HTTPError as e:
        try:
            error = str(e) + " : " + response.content.decode('utf-8')
        except UnicodeDecodeError:
            error = str(e)
    if error is not None:
        if retries > 0:
            print(error + ". Retrying request.")
            post_request(url, params=params, headers=headers, json_body=json_body, data=data, files=files,
                         timeout=timeout, retries=retries-1)
        else:
            raise IastException(error)
    else:
        return response


def delete_request(url, params=None, headers=None, timeout=5, retries=0):
    if headers is None:
        headers = {}
    if params is None:
        params = {}
    error = None
    print_url(url, params, 'DELETE')
    try:
        response = requests.delete(
            url, verify=False, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        error = f"request to {url} timed out."
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidSchema) as e:
        error = f"request to {url} failed with connection error: {str(e)}"
    except requests.exceptions.TooManyRedirects:
        error = "Too many redirects!"
    except requests.exceptions.HTTPError as e:
        error = str(e) + " : " + response.content.decode('utf-8')
    if error is not None:
        if retries > 0:
            print(error + ". Retrying request.")
            delete_request(url, params=params, headers=headers, timeout=timeout, retries=retries-1)
        else:
            raise IastException(error)


def print_url(url, params, http_method):
    if len(params) > 0:
        print(f"{http_method} {url}, params: {params}")
    else:
        print(f"{http_method} {url}")


# spceial method to download zip file, as in this case the response can't be returned
def download_request(url, params=None, headers=None, timeout=5, stream=False, retries=0):
    if headers is None:
        headers = {}
    if params is None:
        params = {}
    print_url(url, params, 'GET')
    error = None
    response = None
    try:
        response = requests.get(url, verify=False, params=params, headers=headers, timeout=timeout, stream=stream)
        print("response.status_code:", response.status_code)
        with open('IASTAgent.temp.zip', 'wb') as f:
            for chunk in response:
                f.write(chunk)
    except requests.exceptions.Timeout:
        error = f"request to {url} timed out."
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidSchema) as e:
        error = f"request to {url} failed with connection error: {str(e)}"
    except requests.exceptions.TooManyRedirects:
        error = "Too many redirects!"
    if error is not None:
        if retries > 0:
            print(error + ". Retrying request.")
            get_request(url, params=params, headers=headers, timeout=timeout, stream=stream, retries=retries - 1)
        else:
            raise IastException(error)
    else:
        return response
