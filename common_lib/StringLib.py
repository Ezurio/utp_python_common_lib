import codecs
import secrets


def BuildHexString(input_length: int) -> str:
    """ Builds and returns a hexadecimal string of the requested input_length

    Args:
        input_length (int): is the length of the hexadecimal string to return.

    Returns:
        str: returns a hexadecimal string of the requested input_length

    Examples:
        | result =  | BuildHexString | 8 | # Result is D73A9E14F7C65B81 |
        | result =  | BuildHexString | 16 | # Result is A7B0E1F23C459D68EE7F102B09C7A1D3 |
    """
    # Calculate the number of bytes needed to generate the desired length of hex string
    num_bytes = (input_length + 1) // 2

    # Generate random bytes
    random_bytes = secrets.token_bytes(num_bytes)

    # Convert the bytes to a hexadecimal string
    hex_string = random_bytes.hex()
    hex_string = hex_string.upper()
    return (hex_string)


def ConvertStringToDecimal(in_string: str) -> str:
    """ Converts a string to an array containing the decimal codes for each character in the string.
    Args:
        in_string (str): is the string to return the decimal equivalents for.

    Returns:
        str: returns an array containing the decimal codes for each character in the string.

    Examples:
        | result =  | ConvertStringToDecimal | Hello, World! | # Result is [72, 101, 108, 108, 111, 44, 32, 87, 111, 114, 108, 100, 33] |
        | result =  | ConvertStringToDecimal | 12345 | # Result is [49, 50, 51, 52, 53] |
    """
    decimal_codes = []
    string_length = len(in_string)
    string_index = 0

    while (string_index < string_length):
        next_char = in_string[string_index]
        decimal_codes.append(ord(next_char))
        string_index = string_index + 1
    return (decimal_codes)


def ConvertStringToHexadecimal(in_string: str) -> str:
    """ Converts a string to an array containing the hexadecimal codes for each character in the string.
    Args:
        in_string (str): is the string to return the hexadecimal equivalents for

    Returns:
        str: returns an array containing the hexadecimal codes for each character in the string.

    Examples:
        | result =  | ConvertStringToHexadecimal | Hello, World! | # Result is ['48', '65', '6C', '6C', '6F', '2C', '20', '57', '6F', '72', '6C', '64', '21'] |
        | result =  | ConvertStringToHexadecimal | 12345 | # Result is ['31', '32', '33', '34', '35'] |
    """
    decimal_codes = []
    string_length = len(in_string)
    string_index = 0

    while (string_index < string_length):
        next_char = in_string[string_index]
        decimal_code = ord(next_char)
        decimal_codes.append("{:02X}".format(decimal_code))
        string_index = string_index + 1
    return (decimal_codes)


def ConvertASCIIToHexadecimal(in_string: str) -> str:
    """ Converts a string containing ASCII hexadecimal values to a string containing the ASCII characters.
    Args:
        in_string (str): is the string that contains the ASCII hex value.

    Returns:
        str: returns a string containing the ASCII characters.

    Examples:
        | result =  | ConvertASCIIToHexadecimal | b"\\x48\\x65\\x6C\\x6C\\x6F\\x2C\\x20\\x57\\x6F\\x72\\x6C\\x64\\x21" | # Result is 48656C6C6F2C20576F726C6421 |
        | result =  | ConvertASCIIToHexadecimal | b"\\x31\\x32\\x33\\x34\\x35" | # Result is 3132333435 |
    """
    # Use codecs to escape the escape sequences and decode the bytes
    escaped_data = codecs.escape_decode(in_string)[0]

    # Convert the escaped data to a hexadecimal string
    hex_string = escaped_data.hex()
    # Remove the b" and " characters
    hex_string = hex_string[4:-6]
    hex_string = hex_string.upper()

    return (hex_string)


def ConvertStringToHexadecimalString(in_string: str) -> str:
    """ Converts a string to a string containing the hexadecimal codes for each character in the string.

    Args:
        in_string (str): is the string to return the hexadecimal equivalents for.

    Returns:
        str: string containing the hexadecimal codes for each character in the string.

    Examples:
        | result =  | ConvertStringToHexadecimalString | Hello, World! | # Result is 48656C6C6F2C20576F726C6421 |
        | result =  | ConvertStringToHexadecimalString | 12345 | # Result is 3132333435 |
    """
    hexadecimal_codes = ""
    string_length = len(in_string)
    string_index = 0

    while (string_index < string_length):
        next_char = in_string[string_index]
        decimal_code = ord(next_char)
        hexadecimal_codes = hexadecimal_codes + ("{:02X}".format(decimal_code))
        string_index = string_index + 1
    return (hexadecimal_codes)


def ConvertStringToASCIIDecimalString(in_string: str) -> str:
    """ Converts a string to a string containing the ASCII decimal codes for each character in the string.
    Args:
        in_string (str): is the string to return the ASCII decimal equivalents for.

    Returns:
        str: string containing the ASCII decimal codes for each character in the string.

    Examples:
        | result =  | ConvertStringToASCIIDecimalString | Hello, World! | # Result is 7210111110112164112112164101 |
        | result =  | ConvertStringToASCIIDecimalString | 12345 | # Result is 4950515253 |
    """
    asciidecimal_codes = ""
    string_length = len(in_string)
    string_index = 0

    while (string_index < string_length):
        next_char = in_string[string_index]
        decimal_code = str(ord(next_char))
        asciidecimal_codes = asciidecimal_codes + decimal_code
        string_index = string_index + 1
    return (asciidecimal_codes)


def Right(in_string: str, in_count: int) -> str:
    """ Count number of characters starting from the right side of a string.

    Args:
        in_string (str): is the string to read the characters from.
        in_count (int): is the number of characters to read.

    Returns:
        str: string containing the characters read from the string.

    Examples:
        | result =  | Right | Hello, World! | 6 | # Result is World! |
        | result =  | Right | 12345 | 3 | # Result is 345 |
    """
    out_characters = ""
    if (in_count < len(in_string)):
        out_characters = in_string[-in_count:]
    return (out_characters)


def Mid(in_string: str, in_start: int, in_count: int) -> str:
    """ Count number of characters starting from in_start from the left side of a string

    Args:
        in_string (str): is the string to read the characters from.
        in_start (int): is the start index from where to read the characters from.
        in_count (int): is the number of characters to read.

    Returns:
        str: string containing the characters read from the string.

    Examples:
        | result =  | Mid | Hello, World! | 7 | 5 | # Result is World |
        | result =  | Mid | 12345 | 1 | 3 | # Result is 234 |
    """
    out_characters = ""
    if (in_count < len(in_string)):
        out_characters = in_string[in_start:in_start+in_count]
    return (out_characters)


def ConvertIntToHexadecimalString(in_int: int) -> str:
    """ Converts integer to hexadecimal string.

    Args:
        in_int (int): is the int to return the hexadecimal equivalent for.

    Returns:
        str: string containing the hexadecimal code for the passed int.

    Examples:
        | result =  | ConvertIntToHexadecimalString | 255 | # Result is FF |
        | result =  | ConvertIntToHexadecimalString | 16 |# Result is 10 |
    """
    hexadecimal_code = ""
    hexadecimal_code = ("{:02X}".format(in_int))
    return (hexadecimal_code)


def ConvertHexadecimalStringtoByteArray(in_string: str) -> str:
    """ Converts a hexadecimal string to a string with escape sequences.

    Args:
        in_string (str): is the hex string to read the characters from.

    Returns:
        str: string containing the byte array format ex:\x00\x00 code for the hex string passed in.

    Examples:
        | result =  | ConvertHexadecimalStringtoByteArray | 48656C6C6F2C20576F726C6421 | # Result is \x48\x65\x6C\x6C\x6F\x2C\x20\x57\x6F\x72\x6C\x64\x21 |
        | result =  | ConvertHexadecimalStringtoByteArray | 1A2B3C4D5E |# Result is \x1A\x2B\x3C\x4D\x5E |
    """
    # Check if the input string is a valid hexadecimal string
    if all(char in "0123456789ABCDEF" for char in in_string):
        # Split the input string into pairs of two characters and convert to integers
        bytes_list = [int(in_string[i:i+2], 16)
                      for i in range(0, len(in_string), 2)]
        # Create a string with escape sequences
        result_str = ''.join([f'\\x{byte:02X}' for byte in bytes_list])
        return result_str
    else:
        return "None"  # Return None for invalid input
