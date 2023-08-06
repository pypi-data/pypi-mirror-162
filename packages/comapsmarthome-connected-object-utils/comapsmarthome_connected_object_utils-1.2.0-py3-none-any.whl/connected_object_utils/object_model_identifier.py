from enum import Enum


class ObjectModel(Enum):
    GATEWAY = 1
    THERMOSTAT = 2
    PILOT_WIRE_HEATING_MODULE = 3
    DRY_CONTACT_HEATING_MODULE = 4
    RADIATOR_VALVE = 5
    V1_THERMOSTAT = 6
    V1_GATEWAY = 7
    OPENTHERM_HEATING_MODULE = 8


class UnrecognizedModelException(Exception):
    def __init__(self, serial_number: str):
        self.serial_number = serial_number


class InstructionTypeEnum(Enum):
    pilot_wire = "pilot_wire"
    temperature = "temperature"


def get_role(serial_number: str, zone=None):
    if (
        serial_number[:1] == "g"
        or serial_number[:1] == "e"
        or serial_number[:2] == "aa"
        or serial_number[:2] == "ca"
    ):
        return "master"
    elif serial_number[:2] == "ba":
        return "slave"
    elif serial_number[:2] == "bb":
        instruction_type = (
            zone.instruction_type.value
            if isinstance(zone.instruction_type, InstructionTypeEnum)
            else zone.instruction_type
        )
        if zone and instruction_type == "pilot_wire":
            return "master"
    return "slave"


def get_model(serial_number: str) -> int:
    if not serial_number:
        raise UnrecognizedModelException(None)

    if len(serial_number) == 16 and serial_number[11:].lower() == "24b00":
        return ObjectModel.V1_GATEWAY

    start = serial_number[:4].lower()
    if start == "1c87":
        return ObjectModel.GATEWAY

    start = serial_number[:2].lower()
    if start == "aa":
        return ObjectModel.THERMOSTAT
    if start == "bb":
        return ObjectModel.PILOT_WIRE_HEATING_MODULE
    if start == "ba":
        return ObjectModel.DRY_CONTACT_HEATING_MODULE
    if start == "ca":
        return ObjectModel.RADIATOR_VALVE
    if start == "bc":
        return ObjectModel.OPENTHERM_HEATING_MODULE

    start = serial_number[:1].lower()
    if start in ["g", "e"]:
        return ObjectModel.V1_THERMOSTAT

    raise UnrecognizedModelException(serial_number)


def is_gateway(serial_number: str) -> bool:
    try:
        return get_model(serial_number) == ObjectModel.GATEWAY
    except UnrecognizedModelException:
        return False


def is_thermostat(serial_number: str) -> bool:
    try:
        return get_model(serial_number) == ObjectModel.THERMOSTAT
    except UnrecognizedModelException:
        return False


def is_pilot_wire_heating_module(serial_number: str) -> bool:
    try:
        return get_model(serial_number) == ObjectModel.PILOT_WIRE_HEATING_MODULE
    except UnrecognizedModelException:
        return False


def is_dry_contact_heating_module(serial_number: str) -> bool:
    try:
        return get_model(serial_number) == ObjectModel.DRY_CONTACT_HEATING_MODULE
    except UnrecognizedModelException:
        return False


def is_heating_module(serial_number: str) -> bool:
    return (
        is_pilot_wire_heating_module(serial_number)
        or is_dry_contact_heating_module(serial_number)
        or is_opentherm_heating_module(serial_number)
    )


def is_radiator_valve(serial_number: str) -> bool:
    try:
        return get_model(serial_number) == ObjectModel.RADIATOR_VALVE
    except UnrecognizedModelException:
        return False


def is_v1_thermostat(serial_number: str) -> bool:
    try:
        return get_model(serial_number) == ObjectModel.V1_THERMOSTAT
    except UnrecognizedModelException:
        return False


def is_v1_gateway(serial_number: str) -> bool:
    try:
        return get_model(serial_number) == ObjectModel.V1_GATEWAY
    except UnrecognizedModelException:
        return False


def is_opentherm_heating_module(serial_number: str) -> bool:
    try:
        return get_model(serial_number) == ObjectModel.OPENTHERM_HEATING_MODULE
    except UnrecognizedModelException:
        return False
