import serial.tools.list_ports as list_ports


def print_ports():
    for port in list_ports.comports():
        print(f"Port: {port.device} Serial Number: {port.serial_number}")


def get_ports():
    """
    Return a list of serial ports that have a serial number.
    """

    detected_ports = list_ports.comports()
    for port in detected_ports[:]:
        if not port.serial_number:
            detected_ports.remove(port)

    return detected_ports


def get_ports_with_serial_number(serial_number: str):
    """
    Return a list of serial ports that control the specified serial number.
    """
    detected_ports = get_ports()

    for port in detected_ports[:]:
        if str(serial_number) not in port.serial_number:
            detected_ports.remove(port)

    return detected_ports
