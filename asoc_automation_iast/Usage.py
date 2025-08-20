#######################################################################################################################
# Licensed Materials –Property of HCL Technologies Ltd.
# © Copyright HCL Technologies Ltd. 2020.
# All rights reserved. See product license for details. US Government Users Restricted Rights. Use, duplication,
# or disclosure restricted by GSA ADP Schedule Contract with HCL Technologies Ltd. Java and all Java-based trademarks
# and logos are trademarks or registered trademarks of Oracle and/or its affiliates. HCL, the HCL logo,
# and Tivoli are registered trademarks of HCL Technologies in the United States, other countries, or both.
#######################################################################################################################
import sys

input_options = {
    "id": ("key id", "required"),
    "secret": ("key secret", "required"),
    "app_id": (
        "Application id. If an application with such id exists, it will be used, otherwise, will exit with an error. "
        "May only use one of: app_name, app_id.",
        "optional"),
    "app_name": (
        "Application name. If an application with such name exists, it will be used, otherwise, create a new "
        "application with the specified name. If not present, a generated name will be used.",
        "optional"),
    "scan_id": (
        "scan id to use. If a scan with such id exists, it will be used, otherwise, will exit with an error. May only "
        "use one of: scan_name, scan_id. "
        "IMPORTANT NOTE: using an existing scan will create a new access token, which will invalidate existing "
        "agents that are associated with the same scan",
        "optional"),
    "scan_name": (
        "scan name. If a scan with such name exists, it will be used, otherwise, create a new scan with the specified "
        "name. If not present, a generated name will be used. "
        "IMPORTANT NOTE: using an existing scan will careet a new access token, which will invalidate existing agents "
        "that are associated with the same scan",
        "optional"),
    "asset_group": (
        "Asset group to use for generating an application. If not specified, the organization's default asset group "
        "will be used. If an existing application is provided, this value is ignored.",
        "optional"),
    "host": (
        "host url. If not specified, the default value will be ASoc North America.",
        "optional")
}


def usage():
    print("\n"+sys.argv[0]+":")
    required = [key for key, value in input_options.items() if value[1] == "required"]
    optional = [key for key, value in input_options.items() if value[1] == "optional"]
    usage_line = sys.argv[0] + " "
    for req in required:
        usage_line += req + "=value "
    usage_line += "["
    for req in optional:
        usage_line += req + "=value "
    usage_line += "]"
    print("Description:")
    print(
        """
  Downloads an IAST agent that communicates with ASoC.  
  The IAST agent communicates with ASoC using an agent key, unique to every IAST scan.
  This agent key is automatically embedded inside the downloaded IAST agent. 
   
  Each IAST agent is associated with a single IAST scan, which is configured in a application in ASoC.
  It is possible to connect multiple agents to a single IAST scan. 
  Based on user input, the script can perform the following actions:
  * Associate the IAST agent with an existing scan.
  * Create a new scan for the IAST agent, associated to an existing application.
  * Create a new application and a new scan for the IAST agent.
  """
    )
    print(f"Usage: {usage_line}")
    for key, value in input_options.items():
        print(f"{key}: {value[0]} ({value[1]})")

    print("\nExamples:")
    print(sys.argv[0] + " --id=abcd --secret=efgh")
    print("A new application and a new IAST scan will be generated.\n")
    print(sys.argv[0] + " --id=abcd --secret=efgh --app_id=12345")
    print("A new IAST scan will be generated, associated with an existing app with id 12345.\n")
    print(sys.argv[0] + " --id=abcd --secret=efgh  --app_name=my-app")
    print("A new IAST scan will be generated, if an application named my-app exists, it will be associated with it. Otherwise, a new application named my-app will be created, associated with the default asset group.\n")
    print(sys.argv[0] + " --id=abcd --secret=efgh --app_name=my-app --asset_group=67890")
    print("A new IAST scan will be generated, if an application named my-app exists, it will be associated with it. Otherwise, a new application named my-app will be created, associated with asset group 67890.\n")
    print(sys.argv[0] + " --id=abcd --secret=efgh --asset_group=67890")
    print("A new application with generated name will be created, associated to asset group 67890.\n")
    print(sys.argv[0] + " --id=abcd --secret=efgh --scan_id=12345")
    print("scan with id 12345 will be used.\n")
    print(sys.argv[0] + " --id=abcd --secret=efgh --scan_name=my-scan")
    print("If a scan named my-scan exists, it will be used. Otherwise, a new application with generated name, and a new scan named my-scan will be created.\n")
    print(sys.argv[0] + " --id=abcd --secret=efgh --scan_name=my-scan --app_id=12345")
    print("If a scan named my-scan exists, it will be used. Otherwise, a new application named my-scan will be created, associated with app 12345.\n")
