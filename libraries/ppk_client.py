import socket
import json
import argparse
import time

class PPKClient:
    """
    TCP Client to interface with PPK2 Daemon

    :param host: Host to connect to
    :param port: Port to connect to
    :param verbose: Enable verbose output
    """
    def __init__(self, host, port, verbose=False):
        self.host = host
        self.port = port
        self.verbose = verbose
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(5)
        self.client.connect((self.host, self.port))

    def close(self):
        """
        Close the TCP connection.
        """
        self.client.close()

    def _get_response(self):
        try:
            response = self.client.recv(1024)
        except socket.timeout as e:
            if self.verbose:
                print(f"Socket timeout: {e}")
            return None
        except socket.error as e:
            if self.verbose:
                print(f"Socket error: {e}")
            return None

        if self.verbose:
            print(f"Received: {response.decode('utf-8')}")
        try:
            json_resp = json.loads(response.decode('utf-8'))
        except json.JSONDecodeError as e:
            if self.verbose:
                print(f"JSON decode error: {e}")
            return None
        if 'error' in json_resp:
            if self.verbose:
                print(f"Server error: {json_resp['error']}")
            return None

        return json_resp

    def send(self, request):
        """
        Send a request to the server and get the response.

        :param request: Dictionary representing the request
        :return: Response from the server as a dictionary
        """
        jr = json.dumps(request)
        if self.verbose:
            print(f"Sending: {jr}")
        self.client.send(jr.encode('utf-8'))
        return self._get_response()

    def set_output_voltage(self, voltage_mv: int):
        """
        Set the output voltage of the power profiler.
        
        :param voltage_mv: Voltage in millivolts
        :raises Exception: If setting the voltage fails
        """
        response = self.send({'command': 'set_output_voltage', 'value': voltage_mv})
        if response is not None and 'result' in response:
            if response['result'] == voltage_mv:
                return
        raise Exception("Failed to set output voltage")
        
    def set_output(self, state: bool):
        """
        Enable or disable the output of the power profiler.
        
        :param state: True to enable, False to disable
        :raises Exception: If setting the output fails
        """
        response = self.send({'command': 'set_output', 'value': state})
        if response is not None and 'result' in response:
            if response['result'] is True:
                return
        raise Exception("Failed to set output state")

    def start_measuring(self):
        """
        Start measuring current.

        :raises Exception: If starting measurement fails
        """
        response = self.send({'command': 'start'})
        if response is not None and 'result' in response:
            if response['result'] == 0:
                return
        raise Exception("Failed to start measuring")
        
    def stop_measuring(self):
        """
        Stop measuring current.

        :raises Exception: If stopping measurement fails
        """
        response = self.send({'command': 'stop'})
        if response is not None and 'result' in response:
            if response['result'] == 0:
                return
        raise Exception("Failed to stop measuring")
        
    def get_min_current(self):
        """
        Get the minimum current measured.

        :return: Minimum current in mA
        :raises Exception: If getting minimum current fails
        """
        response = self.send({'command': 'get_min_current'})
        if response is not None and 'result' in response:
            return response['result']
        raise Exception("Failed to get minimum current")

    def get_max_current(self):
        """
        Get the maximum current measured.

        :return: Maximum current in mA
        :raises Exception: If getting maximum current fails
        """
        response = self.send({'command': 'get_max_current'})
        if response is not None and 'result' in response:
            return response['result']
        raise Exception("Failed to get maximum current")

    def get_average_current(self):
        """
        Get the average current measured.
        
        :return: Average current in mA
        :raises Exception: If getting average current fails
        """
        response = self.send({'command': 'get_average_current'})
        if response is not None and 'result' in response:
            return response['result']
        raise Exception("Failed to get average current")

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='localhost', help='Host to connect to')
    parser.add_argument('--port', type=int, default=5678, help='Port to connect to')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    parser.add_argument('--voltage', type=int, help='Output voltage in mV')
    parser.add_argument('--measure', action='store_true', help='Start measuring')
    args = parser.parse_args()

    # Make sure that we have something to do
    if (args.voltage is None) and (not args.measure):
        print("No action specified. Use --voltage or --measure.")
        exit(1)
    
    # Init client
    try:
        client = PPKClient(args.host, args.port, args.verbose)
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        exit(1)

    # Send request
    try:
        if args.voltage is not None:
            if args.voltage <= 0:
                client.set_output(False)
            else:
                client.set_output_voltage(args.voltage)
                client.set_output(True)

        if args.measure:
            client.start_measuring()
            time.sleep(1)
            print(f"Min current: {client.get_min_current()} mA")
            print(f"Max current: {client.get_max_current()} mA")
            print(f"Average current: {client.get_average_current()} mA")
            client.stop_measuring()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
