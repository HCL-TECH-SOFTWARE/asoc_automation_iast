#######################################################################################################################
# Licensed Materials –Property of HCL Technologies Ltd.
# © Copyright HCL Technologies Ltd. 2020.
# All rights reserved. See product license for details. US Government Users Restricted Rights. Use, duplication,
# or disclosure restricted by GSA ADP Schedule Contract with HCL Technologies Ltd. Java and all Java-based trademarks
# and logos are trademarks or registered trademarks of Oracle and/or its affiliates. HCL, the HCL logo,
# and Tivoli are registered trademarks of HCL Technologies in the United States, other countries, or both.
#######################################################################################################################
import json
import os
import subprocess
import sys

asoc_config_filename = "asoc-config.json"
user_config_filename = "user-config.json"
war_name = "Secagent.war"


def create_asoc_config_file(agent_key):
    with open(asoc_config_filename, 'w') as asoc_config_file:
        json.dump({'accessToken': agent_key}, asoc_config_file)


def remove_asoc_config_file():
    os.remove(asoc_config_filename)


def read_existing_user_config(path_to_existing_file):
    if not path_to_existing_file.endswith(asoc_config_filename):
        path_to_existing_file += "/" + asoc_config_filename
    return json.loads(path_to_existing_file)


def add_user_config_to_war(path_to_war):
    command = f"jar -uvf \"{path_to_war}\" {asoc_config_filename}"
    result = subprocess.run(command, stderr=subprocess.PIPE, shell=True)
    if result.returncode != 0:
        print(f'Error - command [{command}] failed')
        print(result.stderr)
        sys.exit(1)
    print(f"Copied {asoc_config_filename} to {war_name}")


def get_token_from_configfile():
    token = None
    with open(asoc_config_filename) as json_file:
        data = json.load(json_file)
        if 'accessToken' in data:
            token = data["accessToken"]
    return token


class IastException(Exception):
    pass
