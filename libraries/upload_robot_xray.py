import requests
import json
import os
import yaml
import logging
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def upload_robot_to_xray(project, test_plan, result_file):
    xray_cloud_base_url = "https://xray.cloud.getxray.app/api/v2"

    if project == None or test_plan == None:
        raise Exception("Please provide project and test plan keys")

    client_id = os.environ.get('XRAY_CLIENT_ID')
    client_secret = os.environ.get('XRAY_CLIENT_SECRET')

    if client_id == None or client_secret == None:
        raise Exception("Please provide client id and client secret")

    if result_file == None:
        raise Exception("Please provide result file")

    # endpoint doc for authenticating and obtaining token from Xray Cloud
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    auth_data = {"client_id": client_id, "client_secret": client_secret}
    response = requests.post(
        f'{xray_cloud_base_url}/authenticate', data=json.dumps(auth_data), headers=headers)
    auth_token = response.json()

    # endpoint doc for importing Robot Framework XML reports
    params = (('projectKey', project), ('testPlanKey', test_plan))
    report_content = open(result_file, 'rb')
    headers = {'Authorization': 'Bearer ' +
               auth_token, 'Content-Type': 'application/xml'}
    response = requests.post(f'{xray_cloud_base_url}/import/execution/robot',
                             params=params, data=report_content, headers=headers)

    if response.status_code != 200:
        raise Exception("Error uploading Robot Framework XML reports to Xray Cloud: " +
                        response.text+" Status Code: "+str(response.status_code))


def get_test_set_value(machine_name, test_plan_file="test_plans.yml"):
    test_plan = None

    try:
        with open(test_plan_file, 'r') as stream:
            dictionary = yaml.load(stream, Loader)
            for key, value in dictionary.items():
                if key in machine_name:
                    test_plan = value["test_plan"]

    except FileNotFoundError:
        logging.warn(f"No {test_plan_file} file found")

    except Exception as e:
        raise e

    return test_plan
