from distutils.version import StrictVersion

from getmac import get_mac_address

from prusa.connect.printer.const import PrinterType

from ... import errors
from ..const import NO_IP, SUPPORTED_FIRMWARE
from ..model import Model
from ..input_output.serial.serial_queue import SerialQueue
from ..input_output.serial.helpers import enqueue_matchable, \
    wait_for_instruction, enqueue_instruction
from ..structures.model_classes import NetworkInfo
from ..structures.regular_expressions import \
    PRINTER_TYPE_REGEX, FW_REGEX, NOZZLE_REGEX

PRINTER_TYPES = {
    300: PrinterType.I3MK3,
    20300: PrinterType.I3MK3,
    302: PrinterType.I3MK3S,
    20302: PrinterType.I3MK3S,
}

MINIMAL_FIRMWARE = StrictVersion(SUPPORTED_FIRMWARE)  # TODO: Firmware release


def get_printer_type(serial_queue: SerialQueue, should_wait=lambda: True):
    instruction = enqueue_matchable(serial_queue,
                                    "M862.2 Q",
                                    PRINTER_TYPE_REGEX,
                                    to_front=True)
    wait_for_instruction(instruction, should_wait)
    match = instruction.match()
    if match is None:
        errors.ID.ok = False
        raise RuntimeError("Printer responded with something unexpected")

    code = int(match.groups()[0])

    try:
        errors.ID.ok = True
        return PRINTER_TYPES[code]
    except KeyError:
        errors.ID.ok = False
        enqueue_instruction(serial_queue,
                            "M117 Unsupported printer",
                            to_front=True)
        raise RuntimeError(f"Unsupported printer model '{code}'")


def get_firmware_version(serial_queue: SerialQueue, should_wait=lambda: True):
    """Try to get firmware version from printer."""
    instruction = enqueue_matchable(serial_queue,
                                    "M115",
                                    FW_REGEX,
                                    to_front=True)
    wait_for_instruction(instruction, should_wait)
    match = instruction.match()
    if match is None:
        raise RuntimeError("Printer responded with something unexpected")
    firmware_version = match.groups()[0]
    errors.FW.ok = StrictVersion(firmware_version) >= MINIMAL_FIRMWARE

    return firmware_version


def get_nozzle_diameter(serial_queue: SerialQueue, should_wait=lambda: True):
    instruction = enqueue_matchable(serial_queue,
                                    "M862.1 Q",
                                    NOZZLE_REGEX,
                                    to_front=True)
    wait_for_instruction(instruction, should_wait)
    match = instruction.match()
    if match is None:
        raise RuntimeError("Printer responded with something unexpected")

    return float(match.groups()[0])


def get_network_info(model: Model):
    network_info = NetworkInfo()

    if model.ip_updater.local_ip != NO_IP:
        network_info.wifi_ipv4 = model.ip_updater.local_ip

    network_info.wifi_mac = get_mac_address()

    return network_info
