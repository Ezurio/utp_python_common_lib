import json
import yaml

class JsonYamlInterpreter:
    def __init__(self, file_path):
        self.file_path = file_path

    # Reads data into a python dictionary format based upon the file type.
    # Dictionary format is the same regardless of the file format.
    def read_data(self):
        try:
            with open(self.file_path, 'r') as file:
                if self.file_path.endswith('.json'):
                    data = json.load(file)
                elif self.file_path.endswith('.yaml') or self.file_path.endswith('.yml'):
                    data = yaml.safe_load(file)
                else:
                    print("Unsupported file format.")
                    return None
            return data
        except FileNotFoundError:
            print("File not found.")
            return None




