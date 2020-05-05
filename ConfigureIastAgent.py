#######################################################################################################################
# Licensed Materials –Property of HCL Technologies Ltd.
# © Copyright HCL Technologies Ltd. 2020.
# All rights reserved. See product license for details. US Government Users Restricted Rights. Use, duplication,
# or disclosure restricted by GSA ADP Schedule Contract with HCL Technologies Ltd. Java and all Java-based trademarks
# and logos are trademarks or registered trademarks of Oracle and/or its affiliates. HCL, the HCL logo,
# and Tivoli are registered trademarks of HCL Technologies in the United States, other countries, or both.
#######################################################################################################################
import contextlib
import getopt
import shutil
from datetime import datetime
from zipfile import ZipFile

import urllib3

# python -m pip install --upgrade git+git://github.com/hclproducts/asoc_automation_iast
from asoc_automation_iast.AsocUtils import *
from asoc_automation_iast.IastUtils import *
from asoc_automation_iast.Usage import input_options, usage

key_id = None
key_secret = None
app_id = None
app_name = None
scan_id = None
scan_name = None
asset_group = None


def get_user_args():
    global key_id
    global key_secret
    global app_id
    global app_name
    global scan_id
    global scan_name
    global asset_group

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", [option + '=' for option in input_options.keys()])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt == '--id':
            key_id = arg
        elif opt == '--secret':
            key_secret = arg
        elif opt == '--app_id':
            app_id = arg
        elif opt == '--app_name':
            app_name = arg
        elif opt == '--scan_id':
            scan_id = arg
        elif opt == '--scan_name':
            scan_name = arg
        elif opt == '--asset_group':
            asset_group = arg
        elif opt == '-h':
            usage()
            sys.exit(0)

    if key_id is None or key_secret is None:
        print("Error: input parameters key and secret are required")
        usage()
        sys.exit(1)

    print(f"Done reading user input: app_id={app_id}, app_name: {app_name}, scan_id: {scan_id}, scan_name:{scan_name}")


def get_new_iast_key(token):
    #new_token = input(
    print(
        "WARNING! You are asking to use an existing ASoC scan. A new access token will be generated and invalidate "
        "previous token. If you have running agents that use the previous token, they will not be able to communicate "
        "with ASoC anymore. ")#Continue? Y/N")
    #print("answer is", new_token)
#    if new_token.lower() == 'y':
    agent_key = get_new_iast_key_for_scan(scan_id, token)
    return agent_key
    # else:
    #     print("Exiting.")
    #     sys.exit(0)


def main():
    global app_id
    global app_name
    global scan_id
    global scan_name
    global asset_group

    app_created = False
    scan_created = False
    agent_key = None
    token = None

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    current_time = datetime.now().time().strftime('%H-%M-%S')
    # get input parameters from user
    get_user_args()

    try:
        token = get_api_key_login(key_id, key_secret, retries=3)

        #############################################################################
        # part 1 - figure out which parameters are given and what should be created:
        # - new or existing application
        # - new or existing scan
        #############################################################################

        # if scan_id is provided, verify it exists and matches other parameters (if provided)
        if scan_id is not None:
            asoc_scan_name, asoc_app_name, asoc_app_id = get_scan_info_by_id(scan_id, token)
            if scan_name is not None and scan_name != asoc_scan_name:
                exit_with_error(f"Error - given scan name \'{scan_name}\' does not match the given scan id {scan_id}")
            if app_id is not None and app_id != asoc_app_id:
                exit_with_error(f"Error - given app id {app_id} does not match the given scan id {scan_id}")
            if app_name is not None and app_name != asoc_app_name:
                exit_with_error(f"Error - given app name \'{app_name}\' does not match the given scan id {scan_id}")
            scan_name, app_name, app_id = asoc_scan_name, asoc_app_name, asoc_app_id
            print(f"Configuring IAST agent to associate to existing scan {scan_name} with id {scan_id}")
            agent_key = get_new_iast_key(token)

        # if scan_id is not provided and scan_name is provided,
        # it may refer to an existing scan. if yes - verify it exists and matches other parameters (if provided)
        elif scan_name is not None:
            asoc_scan_id, asoc_app_name, asoc_app_id = get_scan_info_by_name(scan_name, token)
            if asoc_scan_id is not None:
                if app_id is not None and app_id != asoc_app_id:
                    exit_with_error(f"Error - given app id {app_id} does not match the given scan name {scan_name}")
                if app_name is not None and app_name != asoc_app_name:
                    exit_with_error(f"Error - given app name {app_name} does not match the given scan name {scan_name}")
                scan_id, app_name, app_id = asoc_scan_id, asoc_app_name, asoc_app_id
                print(f"Configuring IAST agent to associate to existing scan {scan_name} with id {scan_id}")
                agent_key = get_new_iast_key(token)

        # if scan_id and scan_name are not provided and app_id is provided,
        # verify it exists and matches other parameters (if provided)
        if app_id is not None:
            asoc_app_name = get_app_name_by_id(app_id, token)
            if asoc_app_name is None:
                exit_with_error(f"Error - given app id {app_id} not found for the given credentials")
            if app_name is not None and asoc_app_name != app_name:
                exit_with_error(f"Error - given app name {app_name} does not match the given app id {app_id}")
            app_name = asoc_app_name
            print(f"Configuring IAST agent to associate to existing application {app_name} with id {app_id}")

        # if only app_name is provided,
        # it may refer to an existing app. if yes - update app_id
        elif app_name is not None:  # app_id is not provided
            # check if this app exists
            app_id = get_app_id_by_name(app_name, token)
            if app_id is not None:
                print(f"Configuring IAST agent to associate to existing application {app_name} with id {app_id}")

        #############################################################################
        # part 2 - create new app/scan if needed
        #############################################################################

        # generate a new app
        if app_id is None:
            print(f"Creating a new app.")
            # if user did not provide asset group, use default
            if asset_group is None:
                asset_group = get_default_asset_group(token)
            # if user did not provide app name, generate one
            if app_name is None:
                app_name = "iast-app-" + current_time
            app_id = create_app(token, app_name, asset_group)
            app_created = True
            print(f"Created a new application {app_name} with id {app_id}")

        # generate a new IAST scan
        if scan_id is None:
            print(f"Creating a new scan.")
            # if user did not provide app name, generate one
            if scan_name is None:
                scan_name = "iast-scan-" + current_time
            agent_key, scan_id = create_scan(app_id, token, scan_name)
            scan_created = True
            print(f"Created a new scan {scan_name} with id {scan_id}")

        #############################################################################
        # part 3 - download Secagent war and update it with access token
        #############################################################################

        temp_zip_filename = 'IASTAgent.temp.zip'

        with temp_directory('temp'):
            # download IASTAgent.zip, which holds the secagent.war
            download_agent(agent_key)

            # extract the downloaded zip file to temp directory
            print("extracting zip file")
            with ZipFile(temp_zip_filename) as orig_zip:
                ZipFile.extractall(orig_zip)

            # create asoc-config.json file
            print(f"copying {asoc_config_filename} file to {war_name}")
            create_asoc_config_file(agent_key)
            # add the asoc-config.json to the war file
            command = f"jar -uvf \"{war_name}\" \"{asoc_config_filename}\""
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    shell=True)
            if result.returncode != 0:
                print(f'command [{command}] failed')
                print(result.stdout)

            remove_asoc_config_file()

            # zip the files again
            print(f"Zipping {zip_filename}")
            with ZipFile(zip_filename, 'w') as zipObj:
                # Iterate over all the files in directory
                for folderName, subfolders, filenames in os.walk("."):
                    for filename in filenames:
                        if not filename.endswith(".zip"):
                            # create complete filepath of file in directory
                            file_path = os.path.join(folderName, filename)
                            # Add file to zip
                            zipObj.write(file_path)

            shutil.copyfile(zip_filename, os.path.join('../', zip_filename))

    except IastException as e:
        sys.stderr.write("\nAn error has occurred:")
        sys.stderr.write("\n" + str(e))
        # if we created a new app or scan and failed, delete them
        if app_created:
            sys.stderr.write(f"\nDeleting application {app_name} with id {app_id}.\n")
            delete_app(app_id, token)
        if scan_created:
            sys.stderr.write(f"\nDeleting scan {scan_name} with id {scan_id}.\n")
            delete_scan(scan_id, token)
        exit_with_error("\nExiting.")


def exit_with_error(text):
    sys.stderr.write(text)
    sys.exit(1)


@contextlib.contextmanager
def temp_directory(dir_name):
    orig_dir = os.getcwd()
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    os.chdir(dir_name)
    yield
    os.chdir(orig_dir)
    shutil.rmtree(dir_name)


if __name__ == "__main__":
    exit(main())
