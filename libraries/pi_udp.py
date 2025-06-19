import socket
import struct
import time

def get_local_addr() -> str:
    """Get the local IP address of the machine."""
    try:
        # Create a temporary UDP socket to determine the local IP address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
    except Exception as e:
        raise RuntimeError(f"Failed to get local IP address: {e}")
    return local_ip

def create_udp_socket(port: int) -> socket.socket:
    """Create a UDP socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, 'SO_REUSEPORT'): # For Linux/BSD
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(('', port))
    return sock

def send_udp_msg(sock: socket.socket, message: bytes, address: str, port: int) -> None:
    """Send a message over the UDP socket."""
    sock.sendto(message, (address, port))

def receive_udp_msg(sock: socket.socket, size: int = 1024, timeout: float = 1.0) -> bytes:
    """Receive a message from the UDP socket."""
    sock.settimeout(timeout)
    data, _ = sock.recvfrom(size)  # Buffer size is 1024 bytes
    return data

def fast_transmitter(address: str, port: int, num_packets: int = 1000, eot_delay: float = 2.0, num_eot: int = 5) -> None:
    """Send a stream of UDP packets to a specified address and port."""
    sock = create_udp_socket(port)
    try:
        # Send a series of UDP packets with a simple header
        pkt = bytearray(64)  # 64 bytes per packet
        for i in range(num_packets):
            struct.pack_into('>L', pkt, 0, i)  # Pack the packet number into the first 4 bytes
            send_udp_msg(sock, pkt, address, port)

        # Wait for a short period to ensure all packets are sent/received
        time.sleep(eot_delay)

        # Send several End of Transmission (EOT) packets
        struct.pack_into('>L', pkt, 0, 0xFFFF)  # End of transmission marker
        for i in range(num_eot):
            send_udp_msg(sock, pkt, address, port)
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        sock.close()

def fast_receiver(port: int):
    """ Receive a stream of UDP packets on a specified port."""
    sock = create_udp_socket(port)
    rx_count = 0
    try:
        while True:
            data = receive_udp_msg(sock, timeout=3.0)
            if not data:
                break  # No more data, exit the loop

            # Process the received packet (for demonstration, we just print the first 4 bytes)
            pkt_num = struct.unpack_from('>L', data, 0)[0]
            if pkt_num == 0xFFFF:  # Check for EOT marker
                print("End of Transmission received.")
                break
            elif pkt_num < rx_count:
                print("Out of order packet received:", pkt_num)
            else:
                rx_count += 1
    except Exception as e:
        print(f"Error receiving message: {e}")
    finally:
        sock.close()
        print(f"Total packets received: {rx_count}")
        return rx_count
