import sys
import argparse
import time
import threading
import json
import port_helpers
import read_board_config
import socketserver
from ppk2_api.ppk2_api import PPK2_MP as PPK2_API

class PowerProfiler:
    """
    Power Profiler class to interface with PPK2 device

    Primarily designed to supply power to a DUT and measure current consumption
    over relatively short periods of time (seconds to minutes).

    :param serial_port: Serial port of the PPK2 device with which to connect
    """
    def __init__(self, serial_port: str, is_source_mode: bool = False):
        self.measuring = False
        self.measurement_thread = None
        self.ppk2 = None

        # Establish a link to the PPK2 device
        self.ppk2 = PPK2_API(serial_port)
        try:
            self.ppk2.get_modifiers()
        except Exception as e:
            print(f"Error initializing power profiler: {e}")
            raise e

        self.stop = False
        self.current_measurements = []
        self.measurement_thread = threading.Thread(target=self._measurement_loop)
        self.measurement_thread.start()

        # Set up for source metering mode
        if is_source_mode:
            self.source_mode = True
            self.ppk2.use_source_meter()
            self.set_output(False)
            self.set_output_voltage(0)

        # Set up for ampere measurement mode
        else:
            self.source_mode = False
            self.ppk2.use_ampere_meter()

    def close(self):
        # Stop measurement thread
        self.measuring = False
        self.stop = True
        if self.measurement_thread:
            self.measurement_thread.join()
            self.measurement_thread = None

        # Clean up the PPK2 state
        if self.ppk2:
            self.set_output_voltage(0)
            self.set_output(False)
            del self.ppk2

    def set_output_voltage(self, voltage_mv: int):
        """
        Set the output voltage of the power profiler.
        
        :param voltage_mv: Voltage in millivolts (0-5000)
        :raises ValueError: If voltage is out of range
        :return: The set voltage in millivolts
        """
        if not self.source_mode:
            raise Exception("Power Profiler not in source mode")
        if voltage_mv < 0 or voltage_mv > self.ppk2.vdd_high:
            raise ValueError(f"Voltage must be between 0 and {self.ppk2.vdd_high} mV")
        self.ppk2.set_source_voltage(voltage_mv)
        return voltage_mv

    def set_output(self, state: bool):
        """
        Enable or disable the output of the power profiler.

        :param state: True to enable output, False to disable
        :return: True if successful, False otherwise
        """
        if not self.source_mode:
            raise Exception("Power Profiler not in source mode")
        if self.ppk2:
            if state:
                state = "ON"
            else:
                state = "OFF"
            self.ppk2.toggle_DUT_power(state)
            return True
        return False

    def _measurement_loop(self):
        while not self.stop:
            read_data = self.ppk2.get_data()
            if read_data != b'':
                samples, _ = self.ppk2.get_samples(read_data)
                if self.measuring:
                    self.current_measurements += samples
            time.sleep(0.010)

    def start_measuring(self):
        """
        Start measuring current.

        Will reset the array of current measurements.
        """
        if not self.measuring:
            self.current_measurements = []
            self.measuring = True
            self.ppk2.start_measuring()

    def stop_measuring(self):
        """
        Stop measuring current.
        """
        if self.measuring:
            self.measuring = False
            self.ppk2.stop_measuring()

    def get_min_current_mA(self):
        """
        Get the minimum current measured in milliamperes.
        :return: Minimum current in mA
        """
        if len(self.current_measurements) == 0:
            return 0

        return min(self.current_measurements) / 1000

    def get_max_current_mA(self):
        """
        Get the maximum current measured in milliamperes.
        :return: Maximum current in mA
        """
        if len(self.current_measurements) == 0:
            return 0

        return max(self.current_measurements) / 1000

    def get_average_current_mA(self):
        """
        Get the average current measured in milliamperes.
        :return: Average current in mA
        """
        if len(self.current_measurements) == 0:
            return 0

        average_current_mA = (sum(self.current_measurements) / len(self.current_measurements)) / 1000 # measurements are in microamperes, divide by 1000
        return average_current_mA

class PowerProfilerTCPServer(socketserver.TCPServer):
    """
    TCP Server to handle power profiler commands. Since this
    class inherits from socketserver.TCPServer, it will handle
    connections serially. It will block and not accept new
    connections until the current connection is closed.
    """
    def __init__(self, server_address, RequestHandlerClass, profiler):
        self.profiler = profiler
        super().__init__(server_address, RequestHandlerClass)

class PowerProfilerCommandHandler(socketserver.BaseRequestHandler):
    """
    Request handler for power profiler commands.
    """
    def handle(self):
        # Access our dedicated Power Profiler instance via self.server.profiler
        profiler = self.server.profiler
        
        while True:
            # Receive a request
            request = self.request.recv(1024)
            if not request:
                # Stop measuring on disconnect
                profiler.stop_measuring()
                break

            # Parse the request
            try:
                json_request = json.loads(request.decode('utf-8'))
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                error_response = json.dumps({'error': 'Malformed JSON'})
                self.request.send(error_response.encode('utf-8'))
                continue

            response = 0
            if 'command' not in json_request:
                response = -1
            elif json_request['command'] == 'start':
                profiler.start_measuring()
                response = 0
            elif json_request['command'] == 'stop':
                profiler.stop_measuring()
                response = 0
            elif json_request['command'] == 'get_min_current':
                response = profiler.get_min_current_mA()
            elif json_request['command'] == 'get_max_current':
                response = profiler.get_max_current_mA()
            elif json_request['command'] == 'get_average_current':
                response = profiler.get_average_current_mA()
            elif json_request['command'] == 'set_output':
                if 'value' not in json_request:
                    response = False
                else:
                    try:
                        response = profiler.set_output(bool(json_request['value']))
                    except Exception as e:
                        print(f"Error setting output: {e}")
                        response = False
            elif json_request['command'] == 'set_output_voltage':
                if 'value' not in json_request:
                    response = -1
                else:
                    try:
                        response = profiler.set_output_voltage(json_request['value'])
                    except Exception as e:
                        print(f"Error setting output voltage: {e}")
                        response = -1
            else:
                response = -1

            # Send a response
            r = json.dumps({'result': response})
            self.request.send(r.encode('utf-8'))

def start_server(config):
    """
    Start a Power Profiler TCP server based on the provided configuration.

    :param config: Dictionary containing 'port' and 'serial_number' keys

    :return: Tuple of (server instance, PowerProfiler instance) or (None, None)
    """
    port = config.get('tcp_port', 5678)
    serial_number = config.get('sn', None)
    voltage = config.get('voltage_mv', None)

    try:
        # Handle serial number
        ports = port_helpers.get_ports_with_serial_number(serial_number)
        if len(ports) == 0:
            raise Exception(f"No PPK2 device found with serial number {serial_number}")

        if len(ports) > 1:
            raise Exception(f"Multiple PPK2 devices found with serial number {serial_number}")
        serial_port = ports[0].device

        # If voltage is specified, initialize in source mode with that voltage
        if voltage:
            print(f"{serial_number}: Initializing in source mode with {voltage} mV")
            pp = PowerProfiler(serial_port, True)
            pp.set_output_voltage(voltage)
            pp.set_output(True)
        
        # Else, initialize in ampere measurement mode
        else:
            print(f"{serial_number}: Initializing in ampere measurement mode")
            pp = PowerProfiler(serial_port, False)

        # Run the TCP server
        server = PowerProfilerTCPServer(('localhost', port), PowerProfilerCommandHandler, pp)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"{serial_number}: Starting PPK server on localhost:{port}")

        return server, pp
    except Exception as e:
        print(f"Error starting server for {serial_number}: {e}")
        return None, None

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default=None, help='Path to board configuration file')
    args = parser.parse_args()

    # Need the board config to continue
    if not args.config:
        print("Board configuration file is required. Use --config to specify the path.")
        exit(1)

    # Read board configuration
    board_config = read_board_config.read_board_config(args.config)

    # Start servers for each power profiler in the configuration
    servers = []
    profilers = []
    for board in board_config:
        if 'ppk' in board:
            for ppk in board['ppk']:
                server, pp = start_server(ppk)
                if server is None:
                    print(f"Failed to start server for board {board.get('name', 'unknown')}")
                else:
                    servers.append(server)
                    profilers.append(pp)

    # If we didn't start anything, just exit
    if len(servers) == 0:
        print("No power profiler servers started. Exiting.")
        exit(1)

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down servers...")
        for server in servers:
            server.shutdown()
            server.server_close()

        for pp in profilers:
            pp.close()

        sys.exit(0)
