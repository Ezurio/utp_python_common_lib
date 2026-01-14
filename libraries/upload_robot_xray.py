#!/usr/bin/env python3
import requests
import json
import os
import yaml
import logging
import argparse
import time
from pathlib import Path
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

XRAY_CLOUD_BASE_URL = "https://xray.cloud.getxray.app/api/v2"
PROJECT_ID_PROD = '10277'
ISSUE_TYPE_TEST_EXECUTION = '10058'

def upload_robot_to_xray(machine: str, version: str, result_file: str, test_plan: str = None):
    # Validate the input parameters
    if not machine or not version:
        raise Exception("machine and version parameters must be provided")
    if not result_file:
        raise Exception("result_file parameter must be provided")

    # Validate the environment variables
    client_id = os.environ.get('XRAY_CLIENT_ID')
    client_secret = os.environ.get('XRAY_CLIENT_SECRET')
    if not client_id:
        raise Exception("XRAY_CLIENT_ID environment variable not set")
    if not client_secret:
        raise Exception("XRAY_CLIENT_SECRET environment variable not set")

    # Get the test plan for the specified machine
    if not test_plan:
        test_plan = get_test_set_value(machine)
        if not test_plan:
            raise Exception(f"Could not determine test plan ID for machine {machine}")

    print(f"Uploading Robot Results {result_file} to Xray Cloud for test plan {test_plan}")
    date = time.ctime()
    test = Path(result_file).stem

    # Authenticate to obtain a token from Xray Cloud
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    auth_data = {'client_id': client_id, 'client_secret': client_secret}
    response = requests.post(f'{XRAY_CLOUD_BASE_URL}/authenticate',
        data=json.dumps(auth_data), headers=headers)
    auth_token = response.json()

    # endpoint API for importing multiport Robot Framework XML reports
    test_info = {
        'fields': {
            'project': { 'id': PROJECT_ID_PROD }
        }
    }
    test_execution_info = {
        'xrayFields': {
            'testPlanKey': test_plan,
        },
        'fields': {
            'project': { 'id': PROJECT_ID_PROD },
            'summary': f"TE-{machine}-{version}-{test}-{date}",
            'issuetype': { 'id': ISSUE_TYPE_TEST_EXECUTION }
        }
    }
    headers = {'Authorization': 'Bearer ' + auth_token }
    files = {
        'results' : ('results.xml', open(result_file, 'rb'), 'application/xml'),
        'testInfo': ('testinfo.json', json.dumps(test_info).encode('utf-8'), 'application/json'),
        'info': ('test.json', json.dumps(test_execution_info).encode('utf-8'), 'application/json')
    }
    response = requests.post(f'{XRAY_CLOUD_BASE_URL}/import/execution/robot/multipart',
                             files=files, headers=headers)

    if response.status_code != 200:
        raise Exception("Error uploading Robot Framework XML reports to Xray Cloud: " +
                        response.text+" Status Code: "+str(response.status_code))
    else:
        print(response.text)
    print("Upload completed!")


def get_test_set_value(machine_name: str, test_plan_file: str ="test_plans.yml") -> str:
    test_plan = None

    try:
        with open(test_plan_file, 'r') as stream:
            dictionary = yaml.load(stream, Loader)
            for key, value in dictionary.items():
                if key in machine_name:
                    test_plan = f"PROD-{value['test_plan']}"

    except FileNotFoundError:
        logging.warning(f"No {test_plan_file} file found")

    except Exception as e:
        raise e

    return test_plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Upload Robot Framework XML reports to Xray Cloud')
    parser.add_argument('-m', '--machine', required=True,
                        help="Machine to report test execution against")
    parser.add_argument('-v', '--version', required=True,
                        help="Firmware version to report test execution against")
    parser.add_argument('-r', '--results', required=True,
                        help="Robot Framework XML results file")
    parser.add_argument('-t', '--test_plan', required=False, default=None,
                        help="Test plan ID to report test execution against")
    args = parser.parse_args()

    upload_robot_to_xray(args.machine, args.version, args.results, args.test_plan)
