import os.path
import tempfile
from upload_robot_xray import upload_robot_to_xray

xray_machine = None
xray_version = None
xray_output_file = None

class xray_listener:
    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        # Can't setup here if we want to auto set up from yaml file.
        pass

    def setup(self, machine, version, output_file):
        # Save the parameters
        global xray_machine, xray_version, xray_output_file
        xray_machine = machine
        xray_version = version
        xray_output_file = output_file

    def close(self):
        global xray_machine, xray_version, xray_output_file
        if xray_machine and xray_version and xray_output_file:           
            try:
                upload_robot_to_xray(xray_machine, xray_version, xray_output_file)
            except Exception as e:
                print(e)
        else:
            print("No machine, version or output file specified. Skipping upload to Xray.")
