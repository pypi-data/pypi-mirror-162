import pytest

from connected_object_utils.object_model_identifier import (
    ObjectModel,
    UnrecognizedModelException,
    get_model,
    is_gateway,
    is_thermostat,
    is_pilot_wire_heating_module,
    is_dry_contact_heating_module,
    is_heating_module,
    is_radiator_valve,
    is_v1_thermostat,
    is_v1_gateway,
    is_opentherm_heating_module,
)


@pytest.mark.parametrize(
    "serial_number, expected_model",
    [
        ("aa0c2504f896", ObjectModel.THERMOSTAT),
        ("ca0f4ff7d9ea", ObjectModel.RADIATOR_VALVE),
        ("ba05f17e10c6", ObjectModel.DRY_CONTACT_HEATING_MODULE),
        ("bb05f17e10c6", ObjectModel.PILOT_WIRE_HEATING_MODULE),
        ("1c8776d02994", ObjectModel.GATEWAY),
        ("g8776d0299", ObjectModel.V1_THERMOSTAT),
        ("05aa25b400124b00", ObjectModel.V1_GATEWAY),
    ],
)
def test_get_model_should_return_correct_model_from_serial_number(
    serial_number, expected_model
):
    assert get_model(serial_number) == expected_model


def test_get_model_should_raise_exception_because_model_unknown():
    with pytest.raises(UnrecognizedModelException) as e:
        get_model("xx1234567890")
        assert e.value.serial_number == "xx1234567890"


@pytest.mark.parametrize(
    "serial_number, should_be",
    [
        ("1c8776d02994", True),
        ("1c8776d02995", True),
        ("1c87_length_doesnt_matter", True),
        ("1c8676d02994", False),
        (None, False),
    ],
)
def test_is_gateway_should_return_true_when_serial_number_starts_with_1c87(
    serial_number, should_be
):
    assert is_gateway(serial_number) == should_be


@pytest.mark.parametrize(
    "serial_number, should_be",
    [
        ("aa0c2504f896", True),
        ("aa1c2504f896", True),
        ("aa_length_doesnt_matter", True),
        ("ab0c2504f896", False),
        ("1c8776d02994", False),
        (None, False),
    ],
)
def test_is_thermostat_should_return_true_when_serial_number_starts_with_aa(
    serial_number, should_be
):
    assert is_thermostat(serial_number) == should_be


@pytest.mark.parametrize(
    "serial_number, should_be",
    [
        ("bb05f17e10c6", True),
        ("bb15f17e10c6", True),
        ("bb_length_doesnt_matter", True),
        ("bc05f17e10c6", False),
        ("1c8776d02994", False),
        (None, False),
    ],
)
def test_is_pilot_wire_hm_should_return_true_when_serial_number_starts_with_bb(
    serial_number, should_be
):
    assert is_pilot_wire_heating_module(serial_number) == should_be


@pytest.mark.parametrize(
    "serial_number, should_be",
    [
        ("ba05f17e10c6", True),
        ("ba15f17e10c6", True),
        ("ba_length_doesnt_matter", True),
        ("bb05f17e10c6", False),
        ("1c8776d02994", False),
        (None, False),
    ],
)
def test_is_dry_contact_hm_should_return_true_when_serial_number_starts_with_ba(
    serial_number, should_be
):
    assert is_dry_contact_heating_module(serial_number) == should_be


@pytest.mark.parametrize(
    "serial_number, should_be",
    [
        ("ba05f17e10c6", True),
        ("bb15f17e10c6", True),
        ("ba_length_doesnt_matter", True),
        ("bc05f17e10c6", True),
        ("bd05f17e10c6", False),
        ("aa8776d02994", False),
        (None, False),
    ],
)
def test_is_hm_should_return_true_when_hm_is_either_pilot_wire_or_dry_contact(
    serial_number, should_be
):
    assert is_heating_module(serial_number) == should_be


@pytest.mark.parametrize(
    "serial_number, should_be",
    [
        ("ca05f17e10c6", True),
        ("ca15f17e10c6", True),
        ("ca_length_doesnt_matter", True),
        ("cc05f17e10c6", False),
        ("aa8776d02994", False),
        (None, False),
    ],
)
def test_is_radiator_valve_should_return_true_when_serial_number_starts_with_ca(
    serial_number, should_be
):
    assert is_radiator_valve(serial_number) == should_be


@pytest.mark.parametrize(
    "serial_number, should_be",
    [
        ("g144500608", True),
        ("E144300884", True),
        ("g_length_doesnt_matter", True),
        ("h1152002810", False),
        ("aa8776d02994", False),
        (None, False),
    ],
)
def test_is_v1_thermostat_should_return_true_when_serial_number_starts_with_g_or_e(
    serial_number, should_be
):
    assert is_v1_thermostat(serial_number) == should_be


@pytest.mark.parametrize(
    "serial_number, should_be",
    [
        ("05aa25b400124b00", True),
        ("0433c55400124b00", True),
        ("043c4e6100124b00", True),
        ("h1152002810", False),
        ("aa8776d02994", False),
        (None, False),
    ],
)
def test_is_v1_gateway_should_return_true_when_serial_number_ends_with_124b00(
    serial_number, should_be
):
    assert is_v1_gateway(serial_number) == should_be


@pytest.mark.parametrize(
    "serial_number, should_be",
    [
        ("bc05f17e10c6", True),
        ("bc15f17e10c6", True),
        ("bc_length_doesnt_matter", True),
        ("bb05f17e10c6", False),
        ("ba05f17e10c6", False),
        ("1c8776d02994", False),
        (None, False),
    ],
)
def test_is_opentherm_heating_module_should_return_true_when_serial_number_starts_with_bc(
    serial_number, should_be
):
    assert is_opentherm_heating_module(serial_number) == should_be
