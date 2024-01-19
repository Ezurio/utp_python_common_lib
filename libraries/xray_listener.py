import os.path
import tempfile
from upload_robot_xray import upload_robot_to_xray

class xray_listener:
    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        # Can't setup here if we want to auto set up from yaml file.
        pass

    def setup(self, product, test_plan, output_file):
        global xray_product, xray_test_plan, xray_output_file
        xray_product = product
        xray_test_plan = test_plan
        xray_output_file = output_file

    def close(self):
        global xray_product, xray_test_plan, xray_output_file
        print("Uploading Robot Framework XML reports: "+xray_output_file+" to Xray Cloud: Product: "+xray_product+" Test Plan: "+xray_test_plan+"...")
        try:
            upload_robot_to_xray(xray_product, xray_test_plan, xray_output_file)
        except Exception as e:
            print(e)
        else:
            print("Uploaded Robot Framework XML reports to Xray Cloud: Product: "+xray_product+" Test Plan: "+xray_test_plan+" successfully!")
