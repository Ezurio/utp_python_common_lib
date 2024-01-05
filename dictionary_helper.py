
def get_array_from_dict(data, key_path):
    """
    Returns the list at a given key path

        Args:
            data (int): is the length of the hexadecimal string to return.
            key_path (str): is the path to the key that contains the list to return.

        Returns:
            returns the list that is located at the key path specified in the input parameter.
            Or "None" if the key path is invalid or doesn't point to a list.

        Examples:
            For the following example dictionary:

                    nested_dict =
                    {
                        "person": {
                            "name": "Alice",
                            "age": 30,
                            "city": "New York",
                            "emails": ["alice@example.com", "alice.work@example.com"]
                        },
                        "preferences": {
                            "languages": ["Python", "JavaScript", "Java"],
                            "interests": ["Reading", "Traveling", "Music"]
                        }
                    }

            The Key path to the list of languages is "preferences.languages"
    """
    try:
        keys = key_path.split('.')
        current_level = data
        for key in keys:
            current_level = current_level[key]
        if isinstance(current_level, list):
            return current_level
        else:
            print(f"The key '{key_path}' does not point to a valid array.")
            return None
    except (KeyError, TypeError):
        print(f"Invalid key path: '{key_path}'")
        return None


def get_array_length_from_dict(data, key_path):
    """ Returns the length of the list at a given key path

    Args:
        data (int): is the length of the hexadecimal string to return.
        key_path (str): is the path to the key that contains the list to return.

    Returns:
        returns the length of the list that is located at the key path specified in the input parameter.
        Or None if the key path is invalid or doesnt point to a list.

    Examples:
        For the following example dictionary:

                nested_dict =
                {
                    "person": {
                        "name": "Alice",
                        "age": 30,
                        "city": "New York",
                        "emails": ["alice@example.com", "alice.work@example.com"]
                    },
                    "preferences": {
                        "languages": ["Python", "JavaScript", "Java"],
                        "interests": ["Reading", "Traveling", "Music"]
                    }
                }

        The Key path to the list of languages is "preferences.languages" and the value returned is 3.
    """
    try:
        keys = key_path.split('.')
        current_level = data
        for key in keys:
            current_level = current_level[key]
        if isinstance(current_level, list):
            return len(current_level)
        else:
            print(f"The key '{key_path}' does not point to a valid array.")
            return None
    except (KeyError, TypeError):
        print(f"Invalid key path: '{key_path}'")
        return None