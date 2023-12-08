import json
import yaml

# Reads data into a python dictionary format based upon the file type.
# Dictionary format is the same regardless of the file format.
def read_data(file_path):
    try:
        with open(file_path, 'r') as file:
            if file_path.endswith('.json'):
                data = json.load(file)
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                data = yaml.safe_load(file)
            else:
                print("Unsupported file format.")
                return None
        return data
    except FileNotFoundError:
        print("File not found.")
        return None




