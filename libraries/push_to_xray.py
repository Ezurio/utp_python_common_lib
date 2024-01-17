import sys
import argparse
from upload_robot_xray import upload_robot_to_xray

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload Robot Framework XML reports to Xray Cloud')
    parser.add_argument('project', help='Xray Cloud project key')
    parser.add_argument('test_plan', help='Xray Cloud test plan key')
    parser.add_argument('test_file', help='Robot test result file')
    args = parser.parse_args()
    project = args.project
    test_plan = args.test_plan
    result_file = args.test_file
    print("Uploading Robot Framework XML reports to Xray Cloud: Project: "+project+" Test Plan: "+test_plan+"...")
    result = upload_robot_to_xray(project, test_plan, result_file)
    print(result)
