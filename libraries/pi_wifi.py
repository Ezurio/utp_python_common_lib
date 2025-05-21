"""
This module provides functions to manage the WiFi settings on a Raspberry Pi.

It includes functions to start and stop the Access Point (AP) mode and the
Station (STA) mode. The configuration of the AP and STA modes are done
through configuration filenames passed as arguments to the functions.
"""
import subprocess

# Default IP address/mask for the AP mode
DEFAULT_AP_IP="192.168.16.1/24"

def stop_ap():
    """
    Stop the AP (Access Point) mode on the Raspberry Pi.
    """
    subprocess.run(["sudo", "systemctl", "stop", "hostapd"], check=True)
    subprocess.run(["sudo", "systemctl", "stop", "dnsmasq"], check=True)
    subprocess.run(["sudo", "systemctl", "disable", "hostapd"], check=True)
    subprocess.run(["sudo", "systemctl", "disable", "dnsmasq"], check=True)
    subprocess.run(["sudo", "ip", "link", "set", "wlan0", "down"], check=True)

def stop_sta():
    """
    Stop the STA (Station) mode on the Raspberry Pi.
    """
    subprocess.run(["sudo", "systemctl", "stop", "wpa_supplicant"], check=True)
    subprocess.run(["sudo", "systemctl", "disable", "wpa_supplicant"], check=True)
    subprocess.run(["sudo", "ip", "link", "set", "wlan0", "down"], check=True)

def stop():
    """
    Stop any WiFi activity on the Raspberry Pi. This includes both STA 
    (wpa_supplicant) and AP (hostapd) modes.
    """
    subprocess.run(["sudo", "nmcli", "radio", "wifi", "off"], check=True)
    stop_ap()
    stop_sta()

def start_ap(hostapd_config: str, dnsmasq_config: str):
    """
    Start the AP (Access Point) mode on the Raspberry Pi using the specified
    configuration file.
    
    :param hostapd_config: Path to the configuration file for hostapd.
    :param dnsmasq_config: Path to the configuration file for dnsmasq.
    """
    # Overwrite the hostapd configuration file
    subprocess.run(["sudo", "cp", hostapd_config, "/etc/hostapd/hostapd.conf"], check=True)
    subprocess.run(["sudo", "cp", dnsmasq_config, "/etc/dnsmasq.conf"], check=True)

    # Start the hostapd and dnsmasq services
    subprocess.run(["sudo", "rfkill", "unblock", "wifi"], check=True)
    subprocess.run(["sudo", "ip", "link", "set", "wlan0", "up"], check=True)
    subprocess.run(["sudo", "ip", "addr", "add", DEFAULT_AP_IP, "dev", "wlan0"], check=False)
    subprocess.run(["sudo", "systemctl", "start", "hostapd"], check=True)
    subprocess.run(["sudo", "systemctl", "start", "dnsmasq"], check=True)

def start_sta(config_file: str):
    """
    Start the STA (Station) mode on the Raspberry Pi using the specified
    configuration file.
    
    :param config_file: Path to the configuration file for wpa_supplicant.
    """
    # Overwrite the wpa_supplicant configuration file
    subprocess.run(["sudo", "cp", config_file, "/etc/wpa_supplicant/wpa_supplicant.conf"], check=True)
    subprocess.run(["sudo", "ip", "link", "set", "wlan0", "up"], check=True)
    subprocess.run(["sudo", "systemctl", "start", "wpa_supplicant"], check=True)
