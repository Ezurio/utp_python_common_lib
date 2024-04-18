#!/usr/bin/env python3

import requests
import json
import os
import yaml
import logging
import argparse
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

XRAY_CLOUD_BASE_URL = "https://xray.cloud.getxray.app/api/v2"
ENV_XRAY_CLIENT_ID = 'XRAY_CLIENT_ID'
ENV_XRAY_CLIENT_SECRET = 'XRAY_CLIENT_SECRET'


def upload_robot_to_xray(project, test_plan, result_file):
    if not project or not test_plan:
        raise Exception("Please provide project and test plan keys")
    if not result_file:
        raise Exception("Please provide result file")

    client_id = os.environ.get(ENV_XRAY_CLIENT_ID)
    client_secret = os.environ.get(ENV_XRAY_CLIENT_SECRET)
    if not client_id:
        raise Exception(f"{ENV_XRAY_CLIENT_ID} environment variable not set")
    if not client_secret:
        raise Exception(
            f"{ENV_XRAY_CLIENT_SECRET} environment variable not set")

    # endpoint API for authenticating and obtaining token from Xray Cloud
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    auth_data = {"client_id": client_id, "client_secret": client_secret}
    response = requests.post(
        f'{XRAY_CLOUD_BASE_URL}/authenticate', data=json.dumps(auth_data), headers=headers)
    auth_token = response.json()

    # endpoint API for importing Robot Framework XML reports
    params = (('projectKey', project), ('testPlanKey', test_plan))
    report_content = open(result_file, 'rb')
    headers = {'Authorization': 'Bearer ' +
               auth_token, 'Content-Type': 'application/xml'}
    response = requests.post(f'{XRAY_CLOUD_BASE_URL}/import/execution/robot',
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Upload Robot Framework XML reports to Xray Cloud')
    parser.add_argument('-p', '--project', default="PROD",
                        help="Jira project key")
    parser.add_argument('-t', '--test_plan', required=True,
                        help="Jira test plan issue key")
    parser.add_argument('-r', '--results', required=True,
                        help="Robot Framework XML results file")
    args = parser.parse_args()
    project = args.project
    test_plan = args.test_plan
    result_file = args.results
    print(
        f"""Uploading Robot Framework results {result_file} to Xray Cloud
        \tProject: {project} Test Plan: {test_plan} ...""")
    upload_robot_to_xray(project, test_plan, result_file)
    print("Upload completed!")
