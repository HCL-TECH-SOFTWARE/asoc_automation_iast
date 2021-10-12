#######################################################################################################################
# Licensed Materials –Property of HCL Technologies Ltd.
# © Copyright HCL Technologies Ltd. 2020.
# All rights reserved. See product license for details. US Government Users Restricted Rights. Use, duplication,
# or disclosure restricted by GSA ADP Schedule Contract with HCL Technologies Ltd. Java and all Java-based trademarks
# and logos are trademarks or registered trademarks of Oracle and/or its affiliates. HCL, the HCL logo,
# and Tivoli are registered trademarks of HCL Technologies in the United States, other countries, or both.
#######################################################################################################################
import getopt
import json
import os
import subprocess
import sys

# python -m pip install --upgrade git+git://github.com/hclproducts/asoc_automation_iast
import asoc_automation_iast.IastUtils as IastUtils


def print_usage():
    print(f"Description: Inject agen key from ASoC to an IAST agent war file")
    print(f"Usage: {sys.argv[0]} --key=1234abcd5678efgh --war=/path/to/war [--host=asoc/ase host]")


def main():
    agent_key = None
    path_to_war = None
    host = "https://cloud.appscan.com/IAST/"
    try:
        # get parameters from user
        opts, args = getopt.getopt(sys.argv[1:], "", ['key=', "war=", "host="])
        for opt, arg in opts:
            if opt == '--key':
                agent_key = arg
            if opt == '--war':
                path_to_war = arg
            if opt == '--host':
                host = arg
    except getopt.GetoptError as e:
        sys.stderr.write(f"Invalid command line: {sys.argv[1:]}")
        sys.stderr.write(str(e))
        exit(1)

    if agent_key is None or path_to_war is None:
        sys.stderr.write(f"Wrong or missing input arguments: {sys.argv[1:]}")
        print_usage()
        exit(1)

    # create a user config file
    with open(IastUtils.asoc_config_filename, 'w') as user_config_file:
        json.dump({'accessToken': agent_key, 'host': host}, user_config_file)

    # allow for path with or without the filename
    if not path_to_war.endswith(IastUtils.war_name):
        path_to_war += "/" + IastUtils.war_name

    # add the json file to the war
    command = f'jar -uvf "{path_to_war}" "{IastUtils.asoc_config_filename}"'
    result = subprocess.run(command, stderr=subprocess.PIPE, shell=True)
    if result.returncode != 0:
        sys.stderr.write(f'Error - command [{command}] failed')
        sys.stderr.write(str(result.stderr))
        exit(1)
    print(f"Copied {IastUtils.asoc_config_filename} to {path_to_war}")

    # remove the json file
    os.remove(IastUtils.asoc_config_filename)
    exit(0)


if __name__ == "__main__":
    exit(main())
