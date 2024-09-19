from probe import Probe
import logging
import operator
from pyocd.probe.pydapaccess import DAPAccessCMSISDAP
import serial.tools.list_ports as list_ports
import time
from lc_util import logger_setup

logger = logging.getLogger(__name__)

PROBE_VENDOR_STRING = 'Arm'
# Windows = 'CMSIS-DAP v1', RPi = 'DAPLink CMSIS-DAP'
PROBE_PRODUCT_STRING = 'CMSIS-DAP'

VERBOSE = False


class UsbSwdProbe(Probe):
    def __init__(self,
                 id,
                 description: str = "",
                 ports=dict(),
                 family: str = ""):

        super().__init__(id, description, ports, family)
        self.__probe_handle = None

    @staticmethod
    def get_connected_probes(with_comports: bool = True) -> list['UsbSwdProbe']:
        """Get a list of all connected probes.

        Args:
            with_comports (bool, optional): If True, only return probes with comports.
            Defaults to True.

        Returns:
            List: List of USB-SWD probes
        """
        probes = []
        for dap_probe in DAPAccessCMSISDAP.get_connected_devices():
            if VERBOSE:
                logger.debug(
                    f"{dap_probe.vendor_name=} {dap_probe.product_name=}")
            # Is this the probe we are looking for?
            if (dap_probe.vendor_name == PROBE_VENDOR_STRING and
                    PROBE_PRODUCT_STRING in dap_probe.product_name):

                id = dap_probe._unique_id
                logger.debug(f'Found probe {id}')

                if with_comports:
                    # Create list of comports that correspond to emulator
                    com_ports = list()
                    for comport in list_ports.comports():
                        if id == comport.serial_number:
                            logger.debug(
                                f'Found probe COM port {comport.device} [{comport.serial_number}]')
                            com_ports.append(comport)
                        else:
                            logger.debug(
                                f'COM port {comport.device} [{comport.serial_number}]')

                    # Sort the com ports so that the Zephyr port is first
                    com_ports.sort(key=operator.attrgetter(
                        'location', 'device'))

                    if len(com_ports) < 1:
                        logger.warning(
                            f'No COM ports found for probe {id}, skipping this probe')
                        continue

                    probes.append(
                        UsbSwdProbe(dap_probe._unique_id,
                                    PROBE_PRODUCT_STRING,
                                    {"python": com_ports[0].device}))

                else:
                    probes.append(
                        UsbSwdProbe(dap_probe._unique_id, PROBE_PRODUCT_STRING))

        return probes

    def open(self):
        if self.__probe_handle == None:
            self.__probe_handle = DAPAccessCMSISDAP(self.id)

        logger.debug(f"Opening USB-SWD Probe ID {self.id}")
        if not self.__probe_handle.is_open:
            self.__probe_handle.open()
            self.__probe_handle.connect()
        if not self.__probe_handle.is_open:
            raise Exception(f"Unable to open USB-SWD Probe at {self.id}")

    @ property
    def is_open(self):
        if self.__probe_handle is None:
            return False
        return self.__probe_handle.is_open

    @ property
    def firmware_version(self):
        return self.__probe_handle.firmware_version

    def close(self):
        if self.__probe_handle is not None:
            self.__probe_handle.close()

    def get_dap_info(self, id: int):
        result = self.__probe_handle.identify(DAPAccessCMSISDAP.ID(id))
        return result

    def get_dap_info1(self, id: DAPAccessCMSISDAP.ID):
        result = self.__probe_handle.identify(id)
        return result

    def get_dap_ids(self):
        return DAPAccessCMSISDAP.ID

    def reset_target(self):
        if not self.is_open:
            self.open()
        self.__probe_handle.assert_reset(True)
        assert self.__probe_handle.is_reset_asserted()
        time.sleep(0.1)
        self.__probe_handle.assert_reset(False)
        time.sleep(0.1)
        # let the target run
        self.__probe_handle.swo_control(True)

    def reboot(self) -> int:
        """Reboot the debug probe

        Returns:
            int: 0 on success
        """
        self.close()
        self.__probe_handle = None
        return 0


if __name__ == "__main__":
    logger = logger_setup(__file__, debug=True)
    probes = UsbSwdProbe.get_connected_probes()
    logger.info(f"Probes found: {len(probes)}")
    for p in probes:
        logger.info(p)
        for port in p.ports:
            port_info = UsbSwdProbe.get_com_port_info(p.ports[port])
            logger.info(
                f"\tProbe port {port_info.device} HWID: {port_info.hwid}")
