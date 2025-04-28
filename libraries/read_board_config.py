import yaml
import logging
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from board import BoardConfig, Properties
from typing import List, Dict, Any, Set, FrozenSet, Tuple

DEFAULT_CONFIG_FILE = "board_config.yml"


class InvalidPropertyError(Exception):
    pass


class ContinueOuterLoop(Exception):
    pass


class MatchNotFound(Exception):
    pass

def valid_property(property_str: str) -> bool:
    """
    Checks if a given property string is valid.
    (This is a placeholder implementation for demonstration).

    Args:
        property_str: The string to validate. Case-insensitive.

    Returns:
        True if the string is valid, False otherwise.
    """
    if not isinstance(property_str, str):
        return False
    return hasattr(Properties, property_str)

def valid_properties(properties: list) -> bool:
    """Check if a list of properties is valid.

    Args:
        properties (list): list of properties

    Returns:
        bool: True if valid
    """
    if not properties:
        return True

    try:
        for p in properties:
            if isinstance(p, str):
                if not valid_property(p):
                    raise InvalidPropertyError(f"Invalid property: {p}")
            elif isinstance(p, list):
                for x in p:
                    if not valid_property(x):
                        raise InvalidPropertyError(f"Invalid property: {x}")
            else:
                raise InvalidPropertyError(
                    f"Invalid property type {type(p)} for {p}")
        return True

    except InvalidPropertyError:
        return False

def validate_and_normalize_properties(desired_properties, property_validator=valid_property):
    """
    Validates that desired_properties is either a list of strings
    or a list containing exactly two lists of strings. It also validates
    each string using the provided property_validator function.

    If the input is a valid list of strings, it converts it into a
    list containing two identical lists of those strings.

    Args:
        desired_properties: The input parameter to validate.
        property_validator: A function that takes a string and returns True
                            if the string is a valid property, False otherwise.
                            Defaults to the placeholder valid_property function.

    Returns:
        list: The validated (and potentially normalized) list, always in the
              format of a list containing two lists of strings (e.g., [[...], [...]]).

    Raises:
        TypeError: If desired_properties is not a list, or if elements
                   within the list(s) are not strings, or if the structure
                   mixes strings and lists at the top level inappropriately.
        ValueError: If desired_properties is a list of lists, but does
                    not contain exactly two lists, OR if any property string
                    fails validation by the property_validator function.
    """

    # Rule 1: Must be a list
    if not isinstance(desired_properties, list):
        raise TypeError("Input 'desired_properties' must be a list.")

    # Handle empty list: Normalize to [[], []]
    if not desired_properties:
        return [[], []] # Normalized format for empty input

    # Determine expected structure based on the first element
    first_element = desired_properties[0]

    # Case 1: Input is potentially a list of strings -> Validate and Normalize
    if isinstance(first_element, str):
        validated_strings = []
        # Check if ALL elements are strings AND pass validation
        for i, item in enumerate(desired_properties):
            # Type check
            if not isinstance(item, str):
                raise TypeError(
                    f"Expected a list of strings, but found element "
                    f"of type {type(item).__name__} at index {i}."
                )
            # Property validation
            user_property = item.upper()
            if not property_validator(user_property):
                raise ValueError(
                    f"Invalid property string found: '{item}' at index {i}."
                )
            validated_strings.append(user_property) # Collect validated strings

        # If loop completes, it's a valid list of valid strings. Now normalize.
        return [list(validated_strings), list(validated_strings)]

    # Case 2: Input is potentially a list of two lists of strings -> Validate Only
    elif isinstance(first_element, list):
        # Rule 2a: Must contain exactly two elements
        if len(desired_properties) != 2:
            raise ValueError(
                "If 'desired_properties' contains lists, it must contain "
                f"exactly two lists, but found {len(desired_properties)}."
            )

        # Rule 2b: Both elements must be lists, and their contents must be valid strings
        validated_list_of_lists = []
        for i, inner_list in enumerate(desired_properties):
            # Check if the outer element is actually a list
            if not isinstance(inner_list, list):
                raise TypeError(
                    f"Expected a list of lists, but found element "
                    f"of type {type(inner_list).__name__} at outer index {i}."
                )

            validated_inner_list = []
            # Check if all elements within the inner list are strings AND pass validation
            for j, item in enumerate(inner_list):
                # Type check
                if not isinstance(item, str):
                    raise TypeError(
                        f"Expected inner lists to contain only strings, but "
                        f"found element of type {type(item).__name__} at "
                        f"index [{i}][{j}]."
                    )
                # Value check
                user_property = item.upper()
                if not property_validator(user_property):
                     raise ValueError(
                        f"Invalid property string found: '{item}' at index [{i}][{j}]."
                     )
                validated_inner_list.append(user_property)
            validated_list_of_lists.append(validated_inner_list)

        # If loops complete without error, it's valid and already normalized.
        return validated_list_of_lists

    # Case 3: First element is neither a string nor a list
    else:
        raise TypeError(
            f"Elements of 'desired_properties' must be strings or lists, "
            f"but found element of type {type(first_element).__name__} "
            f"at index 0."
        )
        
def read_board_config(board_config_file=DEFAULT_CONFIG_FILE, desired_properties: list = None):
    """Read a board configuration file and return a list of BoardConfig objects.

    Args:
        board_config_file (str, optional): A board config file that
        list board hardware configurations. Defaults to "board_config.yml".

        desired_properties (list, optional): A list of properties 
        that boards must have to be included in output. Defaults to None. 
        Properties are case insensitive.
        Can be a list of lists when a board must have all properties in a sublist.
        If desired properties is a lists of lists, then the order of the output list
        will match the order of the input list.
    Returns:
        list[BoardConfig]: list of boards
    """

    boards = list[BoardConfig]()

    # If Robot framework passes and empty string, then use the default file name
    if not board_config_file:
        board_config_file = DEFAULT_CONFIG_FILE

    # Single board tests provide a list.
    # Multi-board tests provovide a lists of lists.
    # Convert all properties to upper case. Output is a list of lists.
    if desired_properties:
        new_list = list()
        if all(isinstance(i, list) for i in desired_properties):
            for sublist in desired_properties:
                if isinstance(sublist, list):
                    sublist = [item.upper() for item in sublist]
                    new_list.append(sublist)
        elif not all(isinstance(i, list) for i in desired_properties):
            sub = list()
            for p in desired_properties:
                sub.append(p.upper())
            new_list.append(sub)
        else:
            raise RuntimeError("Invalid desired properties format")

        desired_properties = new_list
        valid_properties(desired_properties)
        logging.debug(f"Desired properties: {desired_properties}")

    try:
        with open(board_config_file, 'r') as stream:
            dictionary = yaml.load(stream, Loader)
            board_configurations = dictionary['boards']
            if not desired_properties:
                return [BoardConfig(b) for b in board_configurations]

            # Find a board with all desired properties, the order of the input list matters.
            for sublist in desired_properties:
                for b in board_configurations[:]:
                    properties = b['properties']
                    if properties:
                        properties = [item.upper() for item in properties]
                        valid_properties(properties)
                        logging.debug(f"actual properties: {properties}")
                        if all(x in properties for x in sublist):
                            logging.info(
                                f"Board {b['name']} has all desired properties")
                            boards.append(BoardConfig(b))
                            board_configurations.remove(b)
                            break

    except FileNotFoundError as e:
        if desired_properties:
            logging.error(f"No {board_config_file} file found")
            raise e
        else:
            logging.info(f"No {board_config_file} file found")

    except Exception as e:
        print(e)
        raise e

    if desired_properties and len(boards) == 0:
        raise ValueError("No boards found with desired properties")

    return boards

def get_firmware_images_set(device_dict: Dict[str, Any]) -> Set[str]:
    """
    Safely retrieves the set of all firmware images from a device's probes list.

    Args:
      device_dict: The dictionary representing the device.

    Returns:
      A set containing all unique firmware image names found in the probes list.
      Returns an empty set if 'probes' is missing, empty, or contains no images.
    """
    images_set: Set[str] = set()
    try:
        probes_list = device_dict.get('probes')
        if probes_list and isinstance(probes_list, list):
            for probe in probes_list:
                if isinstance(probe, dict):
                    image = probe.get('image')
                    if image and isinstance(image, str):
                        images_set.add(image)
    except (AttributeError, TypeError):
        # Ignore errors for now. May just end up with an empty set.
        pass
    return images_set

def read_board_config_pairs(board_config_file=DEFAULT_CONFIG_FILE, desired_properties: list = None):
    """
    Read a board configuration file and return a list of pairs of BoardConfig
    objects.

    For example, if there are four boards in the configuration file (A, B, C,
    and D), all with properties including "BLE", then the output will be a
    list of all possible permutations of boards with "BLE" in their properties:

    [ [A, B], [B, A], [A, C], [C, A], [B, C], [C, B], [A, D], [D, A], [B, D],
    [D, B], [C, D], [D, C] ]

    One exception is made for boards that have the same firmware image. In this
    case, there's no need to run, for example, [A, B] and [B, A], so
    [A, B] is returned and [B, A] is not.

    :param board_config_file: A board config file that lists board hardware
      configurations.
    :param desired_properties: This parameter is a list of properties that boards
      must have to be included in output. This can be a single list, which means
      that each board must have all properties in the list. This can also be a
      list of two lists, which means that the pairs of boards will have the
      first board have all of the properties in the first list and the second
      board in the pair will have all of the properties in the second list. This
      is useful for testing two boards that have different properties (e.g.,
      GATT Client and GATT Server). The properties are case insensitive. If no
      desired properties are provided, return all boards.

    :returns: A tuple containing:
        - A list of BoardConfig objects that match the desired properties.
        - A list of tuples representing pairs of indices of the boards that
            have the desired properties.
    """
    # If Robot framework passes and empty string, then use the default file name
    if not board_config_file:
        board_config_file = DEFAULT_CONFIG_FILE

    # Validate and normalize the desired properties
    desired_properties = validate_and_normalize_properties(desired_properties)
    logging.debug(f"Desired properties: {desired_properties}")

    # Get the list of boards from the configuration file
    config_boards = []
    try:
        with open(board_config_file, 'r') as stream:
            dictionary = yaml.load(stream, Loader)
            config_boards = dictionary['boards']
    except FileNotFoundError as e:
        logging.error(f"read_board_config_pairs: File not found: {board_config_file}")
        raise e
    except Exception as e:
        print(e)
        raise e

    # Filter to the list of boards that have the desired "A" and "B" properties
    boards = []
    boards_a = []
    boards_b = []
    for b in config_boards:
        # Get the board's properties
        properties = b.get('properties', [])

        # Convert properties to uppercase for case-insensitive comparison
        properties = [i.upper() for i in properties]
        if not valid_properties(properties):
            raise ValueError(f"Board {b['name']} has invalid properties: {properties}")
        logging.debug(f"Board {b['name']} properties: {properties}")

        # Check if the board matches the desired properties
        match_a_props = all(x in properties for x in desired_properties[0])
        match_b_props = all(x in properties for x in desired_properties[1])

        if match_a_props or match_b_props:
            boards.append(BoardConfig(b))
        if match_a_props:
            boards_a.append(len(boards) - 1)
            logging.info(f"Board {b['name']} matches for list A")
        if match_b_props:
            boards_b.append(len(boards) - 1)
            logging.info(f"Board {b['name']} matches for list B")

    # Permute the boards
    board_pairs = []
    if len(boards_a) == 0 or len(boards_b) == 0:
        raise ValueError("Not enough boards to form pairs")
    for i in boards_a:
        for j in boards_b:
            if i != j:
                board_pairs.append((i, j))

    # Filter out boards that have the same firmware image.
    # Use the image name from the board's probes arrays to determine
    # if the firmware image is the same.
    filtered_list: List[Tuple[int]] = []

    # Keep track of pairs with the same firmware set we've already added.
    processed_same_firmware_pairs: Set[FrozenSet[str]] = set()

    for pair in board_pairs:
        device1 = boards[pair[0]]
        device2 = boards[pair[1]]
        
        # Get the set of firmware images for each device
        device1_firmware_set = get_firmware_images_set(device1)
        device2_firmware_set = get_firmware_images_set(device2)
        
        # Check if the firmware sets are the same and non-empty
        if device1_firmware_set and device1_firmware_set == device2_firmware_set:
            # If we haven't processed this pair yet, add it to the filtered list
            firmware_pair = frozenset(pair)
            if firmware_pair not in processed_same_firmware_pairs:
                filtered_list.append(pair)
                processed_same_firmware_pairs.add(firmware_pair)
            # Else, skip adding this pair to avoid duplicates
        else:
            # If the firmware is different, add the pair to the filtered list
            filtered_list.append(pair)

    # Return the list of boards and the filtered pairs
    return (boards, filtered_list)