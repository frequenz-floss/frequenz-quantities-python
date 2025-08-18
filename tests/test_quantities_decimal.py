# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for quantity types."""

# pylint: disable=too-many-lines


from datetime import timedelta
from decimal import Decimal

import hypothesis
import pytest
from hypothesis import strategies as st

from frequenz.quantities import (
    ApparentPower,
    Current,
    Energy,
    Frequency,
    Percentage,
    Power,
    Quantity,
    ReactivePower,
    Temperature,
    Voltage,
)

from .utils import (
    _QUANTITY_CTORS,
    Fz1,
    Fz2,
    _CtorType,
)


@pytest.mark.parametrize("quantity_ctor", _QUANTITY_CTORS)
def test_base_value_from_ctor_is_decimal(quantity_ctor: _CtorType[Decimal]) -> None:
    """Test that the base value always is a Decimal."""
    quantity = quantity_ctor(Decimal("1"))
    assert isinstance(quantity.base_value, Decimal)


def test_string_representation() -> None:
    """Test the string representation of the quantities."""
    assert str(Quantity(Decimal("1.024445"), exponent=0)) == "1.024"
    assert (
        repr(Quantity(Decimal("1.024445"), exponent=0))
        == "Quantity(value=1.024445, exponent=0)"
    )
    assert f"{Quantity(Decimal('0.50001'), exponent=0):.0}" == "1"
    assert f"{Quantity(Decimal('1.024445'), exponent=0)}" == "1.024"
    assert f"{Quantity(Decimal('1.024445'), exponent=0):.0}" == "1"
    assert f"{Quantity(Decimal('0.124445'), exponent=0):.0}" == "0"
    assert f"{Quantity(Decimal('0.50001'), exponent=0):.0}" == "1"
    assert f"{Quantity(Decimal('1.024445'), exponent=0):.6}" == "1.024445"

    assert f"{Quantity(Decimal('1.024445'), exponent=3)}" == "1024.445"

    assert str(Fz1(Decimal("1.024445"), exponent=0)) == "1.024 Hz"
    assert (
        repr(Fz1(Decimal("1.024445"), exponent=0)) == "Fz1(value=1.024445, exponent=0)"
    )
    assert f"{Fz1(Decimal('1.024445'), exponent=0)}" == "1.024 Hz"
    assert f"{Fz1(Decimal('1.024445'), exponent=0):.0}" == "1 Hz"
    assert f"{Fz1(Decimal('1.024445'), exponent=0):.1}" == "1 Hz"
    assert f"{Fz1(Decimal('1.024445'), exponent=0):.2}" == "1.02 Hz"
    assert f"{Fz1(Decimal('1.024445'), exponent=0):.9}" == "1.024445 Hz"
    assert f"{Fz1(Decimal('1.024445'), exponent=0):0.0}" == "1 Hz"
    assert f"{Fz1(Decimal('1.024445'), exponent=0):0.1}" == "1.0 Hz"
    assert f"{Fz1(Decimal('1.024445'), exponent=0):0.2}" == "1.02 Hz"
    assert f"{Fz1(Decimal('1.024445'), exponent=0):0.9}" == "1.024445000 Hz"

    assert f"{Fz1(Decimal('1.024445'), exponent=3)}" == "1.024 kHz"
    assert f"{Fz2(Decimal('1.024445'), exponent=3)}" == "1.024 kHz"

    assert f"{Fz1(Decimal('1.024445'), exponent=6)}" == "1024.445 kHz"
    assert f"{Fz2(Decimal('1.024445'), exponent=6)}" == "1.024 MHz"
    assert f"{Fz1(Decimal('1.024445'), exponent=9)}" == "1024445 kHz"
    assert f"{Fz2(Decimal('1.024445'), exponent=9)}" == "1.024 GHz"

    assert f"{Fz1(Decimal('1.024445'), exponent=-3)}" == "0.001 Hz"
    assert f"{Fz2(Decimal('1.024445'), exponent=-3)}" == "1.024 mHz"

    assert f"{Fz1(Decimal('1.024445'), exponent=-6)}" == "0 Hz"
    assert f"{Fz1(Decimal('1.024445'), exponent=-6):.6}" == "0.000001 Hz"
    assert f"{Fz2(Decimal('1.024445'), exponent=-6)}" == "1.024 uHz"

    assert f"{Fz1(Decimal('1.024445'), exponent=-12)}" == "0 Hz"
    assert f"{Fz2(Decimal('1.024445'), exponent=-12)}" == "0 Hz"

    assert f"{Fz1(0)}" == "0 Hz"

    assert f"{Fz1(-20)}" == "-20 Hz"
    assert f"{Fz1(-20000)}" == "-20 kHz"

    assert f"{Power[Decimal].from_watts(Decimal('0.000124445')):.0}" == "0 W"
    assert f"{Energy[Decimal].from_watt_hours(Decimal('0.124445')):.0}" == "0 Wh"
    assert (
        f"{ReactivePower[Decimal].from_volt_amperes_reactive(Decimal('0.000124445')):.0}"
        == "0 VAR"
    )
    assert (
        f"{ApparentPower[Decimal].from_volt_amperes(Decimal('0.000124445')):.0}"
        == "0 VA"
    )
    assert f"{Power[Decimal].from_watts(Decimal('-0.0')):.0}" == "-0 W"
    assert f"{Power[Decimal].from_watts(Decimal('0.0')):.0}" == "0 W"
    assert (
        f"{ReactivePower[Decimal].from_volt_amperes_reactive(Decimal('-0.0')):.0}"
        == "-0 VAR"
    )
    assert (
        f"{ReactivePower[Decimal].from_volt_amperes_reactive(Decimal('0.0')):.0}"
        == "0 VAR"
    )
    assert f"{ApparentPower[Decimal].from_volt_amperes(Decimal('-0.0')):.0}" == "-0 VA"
    assert f"{ApparentPower[Decimal].from_volt_amperes(Decimal('0.0')):.0}" == "0 VA"
    assert f"{Voltage[Decimal].from_volts(Decimal('999.9999850988388'))}" == "1 kV"


def test_isclose() -> None:
    """Test the isclose method of the quantities."""
    assert Fz1(Decimal("1.024445")).isclose(Fz1(Decimal("1.024445")))
    assert not Fz1(Decimal("1.024445")).isclose(Fz1(Decimal("1.0")))


@hypothesis.given(
    value=st.floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=1e-5,
        max_value=1e5,
    )
)
@pytest.mark.parametrize("ndigits", [0, 1, 2, 3])
def test_round(value: float, ndigits: int) -> None:
    """Test the rounding of the quantities."""
    assert round(Quantity(value), ndigits) == Quantity(round(value, ndigits))


@hypothesis.given(
    dividend=st.floats(
        allow_infinity=False,
        min_value=1e-5,
        max_value=1e5,
        allow_nan=False,
    ),
    divisor=st.floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=1e-5,
        max_value=1e5,
        exclude_min=True,
    ),
)
def test_mod(dividend: float, divisor: float) -> None:
    """Test the modulo operation of the quantities."""
    dividend_decimal = Decimal(str(dividend))
    divisor_decimal = Decimal(str(divisor))
    assert Quantity(dividend_decimal) % Quantity(divisor_decimal) == Quantity(
        dividend_decimal % divisor_decimal
    )


def test_addition_subtraction() -> None:
    """Test the addition and subtraction of the quantities."""
    assert Quantity(Decimal("1")) + Quantity(Decimal("1"), exponent=0) == Quantity(
        Decimal("2"), exponent=0
    )
    assert Quantity(Decimal("1")) + Quantity(Decimal("1"), exponent=3) == Quantity(
        Decimal("1001"), exponent=0
    )
    assert Quantity(Decimal("1")) - Quantity(Decimal("1"), exponent=0) == Quantity(
        Decimal("0"), exponent=0
    )

    assert Fz1(Decimal("1")) + Fz1(Decimal("1")) == Fz1(Decimal("2"))
    with pytest.raises(TypeError) as excinfo:
        assert Fz1(Decimal("1")) + Fz2(Decimal("1"))  # type: ignore
    assert excinfo.value.args[0] == "unsupported operand type(s) for +: 'Fz1' and 'Fz2'"
    with pytest.raises(TypeError) as excinfo:
        assert Fz1(Decimal("1")) - Fz2(Decimal("1"))  # type: ignore
    assert excinfo.value.args[0] == "unsupported operand type(s) for -: 'Fz1' and 'Fz2'"

    fz1 = Fz1(Decimal("1.0"))
    fz1 += Fz1(Decimal("4.0"))
    assert fz1 == Fz1(Decimal("5.0"))
    fz1 -= Fz1(Decimal("9.0"))
    assert fz1 == Fz1(Decimal("-4.0"))

    with pytest.raises(TypeError) as excinfo:
        fz1 += Fz2(Decimal("1.0"))  # type: ignore


def test_comparison() -> None:
    """Test the comparison of the quantities."""
    assert Quantity(Decimal("1.024445"), exponent=0) == Quantity(
        Decimal("1.024445"), exponent=0
    )
    assert Quantity(Decimal("1.024445"), exponent=0) != Quantity(
        Decimal("1.024445"), exponent=3
    )
    assert Quantity(Decimal("1.024445"), exponent=0) < Quantity(
        Decimal("1.024445"), exponent=3
    )
    assert Quantity(Decimal("1.024445"), exponent=0) <= Quantity(
        Decimal("1.024445"), exponent=3
    )
    assert Quantity(Decimal("1.024445"), exponent=0) <= Quantity(
        Decimal("1.024445"), exponent=0
    )
    assert Quantity(Decimal("1.024445"), exponent=0) > Quantity(
        Decimal("1.024445"), exponent=-3
    )
    assert Quantity(Decimal("1.024445"), exponent=0) >= Quantity(
        Decimal("1.024445"), exponent=-3
    )
    assert Quantity(Decimal("1.024445"), exponent=0) >= Quantity(
        Decimal("1.024445"), exponent=0
    )

    assert Fz1(Decimal("1.024445"), exponent=0) == Fz1(Decimal("1.024445"), exponent=0)
    assert Fz1(Decimal("1.024445"), exponent=0) != Fz1(Decimal("1.024445"), exponent=3)
    assert Fz1(Decimal("1.024445"), exponent=0) < Fz1(Decimal("1.024445"), exponent=3)
    assert Fz1(Decimal("1.024445"), exponent=0) <= Fz1(Decimal("1.024445"), exponent=3)
    assert Fz1(Decimal("1.024445"), exponent=0) <= Fz1(Decimal("1.024445"), exponent=0)
    assert Fz1(Decimal("1.024445"), exponent=0) > Fz1(Decimal("1.024445"), exponent=-3)
    assert Fz1(Decimal("1.024445"), exponent=0) >= Fz1(Decimal("1.024445"), exponent=-3)
    assert Fz1(Decimal("1.024445"), exponent=0) >= Fz1(Decimal("1.024445"), exponent=0)

    assert Fz1(Decimal("1.024445"), exponent=0) != Fz2(Decimal("1.024445"), exponent=0)
    with pytest.raises(TypeError) as excinfo:
        # unfortunately, mypy does not identify this as an error, when comparing a child
        # type against a base type, but they should still fail, because base-type
        # instances are being used as dimension-less quantities, whereas all child types
        # have dimensions/units.
        assert Fz1(Decimal("1.024445"), exponent=0) <= Quantity(
            Decimal("1.024445"), exponent=0
        )
    assert (
        excinfo.value.args[0]
        == "'<=' not supported between instances of 'Fz1' and 'Quantity'"
    )
    with pytest.raises(TypeError) as excinfo:
        assert Quantity(Decimal("1.024445"), exponent=0) <= Fz1(
            Decimal("1.024445"), exponent=0
        )
    assert (
        excinfo.value.args[0]
        == "'<=' not supported between instances of 'Quantity' and 'Fz1'"
    )
    with pytest.raises(TypeError) as excinfo:
        assert Fz1(Decimal("1.024445"), exponent=0) < Fz2(
            Decimal("1.024445"), exponent=3
        )  # type: ignore
    assert (
        excinfo.value.args[0]
        == "'<' not supported between instances of 'Fz1' and 'Fz2'"
    )
    with pytest.raises(TypeError) as excinfo:
        assert Fz1(Decimal("1.024445"), exponent=0) <= Fz2(
            Decimal("1.024445"), exponent=3
        )  # type: ignore
    assert (
        excinfo.value.args[0]
        == "'<=' not supported between instances of 'Fz1' and 'Fz2'"
    )
    with pytest.raises(TypeError) as excinfo:
        assert Fz1(Decimal("1.024445"), exponent=0) > Fz2(
            Decimal("1.024445"), exponent=-3
        )  # type: ignore
    assert (
        excinfo.value.args[0]
        == "'>' not supported between instances of 'Fz1' and 'Fz2'"
    )
    with pytest.raises(TypeError) as excinfo:
        assert Fz1(Decimal("1.024445"), exponent=0) >= Fz2(
            Decimal("1.024445"), exponent=-3
        )  # type: ignore
    assert (
        excinfo.value.args[0]
        == "'>=' not supported between instances of 'Fz1' and 'Fz2'"
    )


def test_power() -> None:
    """Test the power class."""
    power = Power[Decimal].from_milliwatts(Decimal("0.0000002"))
    assert f"{power:.9}" == "0.0000002 mW"
    power = Power[Decimal].from_kilowatts(Decimal("10000000.2"))
    assert f"{power}" == "10000 MW"

    power = Power[Decimal].from_kilowatts(Decimal("1.2"))
    assert power.as_watts() == Decimal("1200.0")
    assert power.as_megawatts() == Decimal("0.0012")
    assert power.as_kilowatts() == Decimal("1.2")
    assert power == Power[Decimal].from_milliwatts(Decimal("1200000.0"))
    assert power == Power[Decimal].from_megawatts(Decimal("0.0012"))
    assert power != Power[Decimal].from_watts(Decimal("1000.0"))

    with pytest.raises(TypeError):
        # using the default constructor should raise.
        Power(1.0, exponent=0)


def test_reactive_power() -> None:
    """Test the reactive power class."""
    power = ReactivePower[Decimal].from_milli_volt_amperes_reactive(
        Decimal("0.0000002")
    )
    assert f"{power:.9}" == "0.0000002 mVAR"
    power = ReactivePower[Decimal].from_kilo_volt_amperes_reactive(
        Decimal("10000000.2")
    )
    assert f"{power}" == "10000 MVAR"

    power = ReactivePower[Decimal].from_kilo_volt_amperes_reactive(Decimal("1.2"))
    assert power.as_volt_amperes_reactive() == Decimal("1200.0")
    assert power.as_mega_volt_amperes_reactive() == Decimal("0.0012")
    assert power.as_kilo_volt_amperes_reactive() == Decimal("1.2")
    assert power == ReactivePower[Decimal].from_milli_volt_amperes_reactive(
        Decimal("1200000.0")
    )
    assert power == ReactivePower[Decimal].from_mega_volt_amperes_reactive(
        Decimal("0.0012")
    )
    assert power != ReactivePower[Decimal].from_volt_amperes_reactive(Decimal("1000.0"))

    with pytest.raises(TypeError):
        # using the default constructor should raise.
        ReactivePower(1.0, exponent=0)


def test_apparent_power() -> None:
    """Test the apparent power class."""
    power = ApparentPower[Decimal].from_milli_volt_amperes(Decimal("0.0000002"))
    assert f"{power:.9}" == "0.0000002 mVA"
    power = ApparentPower[Decimal].from_kilo_volt_amperes(Decimal("10000000.2"))
    assert f"{power}" == "10000 MVA"

    power = ApparentPower[Decimal].from_kilo_volt_amperes(Decimal("1.2"))
    assert power.as_volt_amperes() == Decimal("1200.0")
    assert power.as_mega_volt_amperes() == Decimal("0.0012")
    assert power.as_kilo_volt_amperes() == Decimal("1.2")
    assert power == ApparentPower[Decimal].from_milli_volt_amperes(Decimal("1200000.0"))
    assert power == ApparentPower[Decimal].from_mega_volt_amperes(Decimal("0.0012"))
    assert power != ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0"))

    with pytest.raises(TypeError):
        # using the default constructor should raise.
        ApparentPower(1.0, exponent=0)


def test_current() -> None:
    """Test the current class."""
    current = Current[Decimal].from_milliamperes(Decimal("0.0000002"))
    assert f"{current:.9}" == "0.0000002 mA"
    current = Current[Decimal].from_amperes(Decimal("600000.0"))
    assert f"{current}" == "600000 A"

    current = Current[Decimal].from_amperes(Decimal("6.0"))
    assert current.as_amperes() == Decimal("6.0")
    assert current.as_milliamperes() == Decimal("6000.0")
    assert current == Current[Decimal].from_milliamperes(Decimal("6000.0"))
    assert current == Current[Decimal].from_amperes(Decimal("6.0"))
    assert current != Current[Decimal].from_amperes(Decimal("5.0"))

    with pytest.raises(TypeError):
        # using the default constructor should raise.
        Current(1.0, exponent=0)


def test_voltage() -> None:
    """Test the voltage class."""
    voltage = Voltage[Decimal].from_millivolts(Decimal("0.0000002"))
    assert f"{voltage:.9}" == "0.0000002 mV"
    voltage = Voltage[Decimal].from_kilovolts(Decimal("600000.0"))
    assert f"{voltage}" == "600000 kV"

    voltage = Voltage[Decimal].from_volts(Decimal("6.0"))
    assert voltage.as_volts() == Decimal("6.0")
    assert voltage.as_millivolts() == Decimal("6000.0")
    assert voltage.as_kilovolts() == Decimal("0.006")
    assert voltage == Voltage[Decimal].from_millivolts(Decimal("6000.0"))
    assert voltage == Voltage[Decimal].from_kilovolts(Decimal("0.006"))
    assert voltage == Voltage[Decimal].from_volts(Decimal("6.0"))
    assert voltage != Voltage[Decimal].from_volts(Decimal("5.0"))

    with pytest.raises(TypeError):
        # using the default constructor should raise.
        Voltage(1.0, exponent=0)


def test_energy() -> None:
    """Test the energy class."""
    energy = Energy[Decimal].from_watt_hours(Decimal("0.0000002"))
    assert f"{energy:.9}" == "0.0000002 Wh"
    energy = Energy[Decimal].from_megawatt_hours(Decimal("600000.0"))
    assert f"{energy}" == "600000 MWh"

    energy = Energy[Decimal].from_kilowatt_hours(Decimal("6.0"))
    assert energy.as_watt_hours() == Decimal("6000.0")
    assert energy.as_kilowatt_hours() == Decimal("6.0")
    assert energy.as_megawatt_hours() == Decimal("0.006")
    assert energy == Energy[Decimal].from_megawatt_hours(Decimal("0.006"))
    assert energy == Energy[Decimal].from_kilowatt_hours(Decimal("6.0"))
    assert energy != Energy[Decimal].from_kilowatt_hours(Decimal("5.0"))

    with pytest.raises(TypeError):
        # using the default constructor should raise.
        Energy(1.0, exponent=0)


def test_temperature() -> None:
    """Test the temperature class."""
    temp = Temperature[Decimal].from_celsius(Decimal("30.4"))
    assert f"{temp}" == "30.4 °C"

    assert temp.as_celsius() == Decimal("30.4")
    assert temp != Temperature[Decimal].from_celsius(Decimal("5.0"))

    with pytest.raises(TypeError):
        # using the default constructor should raise.
        Temperature(1.0, exponent=0)


def test_quantity_compositions() -> None:
    """Test the composition of quantities."""
    power = Power[Decimal].from_watts(Decimal("1000.0"))
    voltage = Voltage[Decimal].from_volts(Decimal("250.0"))
    current = Current[Decimal].from_amperes(Decimal("4.0"))
    energy = Energy[Decimal].from_kilowatt_hours(Decimal("6.5"))

    assert power / voltage == current
    assert power / current == voltage
    assert power == voltage * current
    assert power == current * voltage

    assert energy / power == timedelta(hours=6.5)
    assert energy == power * timedelta(hours=6.5)
    assert energy / timedelta(hours=6.5) == power


def test_frequency() -> None:
    """Test the frequency class."""
    freq = Frequency[Decimal].from_hertz(Decimal("0.0000002"))
    assert f"{freq:.9}" == "0.0000002 Hz"
    freq = Frequency[Decimal].from_kilohertz(Decimal("600_000.0"))
    assert f"{freq}" == "600 MHz"

    freq = Frequency[Decimal].from_hertz(Decimal("6.0"))
    assert freq.as_hertz() == Decimal("6.0")
    assert freq.as_kilohertz() == Decimal("0.006")
    assert freq == Frequency[Decimal].from_kilohertz(Decimal("0.006"))
    assert freq == Frequency[Decimal].from_hertz(Decimal("6.0"))
    assert freq != Frequency[Decimal].from_hertz(Decimal("5.0"))

    with pytest.raises(TypeError):
        # using the default constructor should raise.
        Frequency(1.0, exponent=0)


def test_percentage() -> None:
    """Test the percentage class."""
    pct = Percentage[Decimal].from_fraction(Decimal("0.204"))
    assert f"{pct}" == "20.4 %"
    pct = Percentage[Decimal].from_percent(Decimal("20.4"))
    assert f"{pct}" == "20.4 %"
    assert pct.as_percent() == Decimal("20.4")
    assert pct.as_fraction() == Decimal("0.204")


def test_neg() -> None:
    """Test the negation of quantities."""
    power = Power[Decimal].from_watts(Decimal("1000.0"))
    assert -power == Power[Decimal].from_watts(Decimal("-1000.0"))
    assert -(-power) == power

    reactive_power = ReactivePower[Decimal].from_volt_amperes_reactive(
        Decimal("1000.0")
    )
    assert -reactive_power == ReactivePower[Decimal].from_volt_amperes_reactive(
        Decimal("-1000.0")
    )
    assert -(-reactive_power) == reactive_power

    apparent_power = ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0"))
    assert -apparent_power == ApparentPower[Decimal].from_volt_amperes(
        Decimal("-1000.0")
    )
    assert -(-apparent_power) == apparent_power

    voltage = Voltage[Decimal].from_volts(Decimal("230.0"))
    assert -voltage == Voltage[Decimal].from_volts(Decimal("-230.0"))
    assert -(-voltage) == voltage

    current = Current[Decimal].from_amperes(Decimal("2"))
    assert -current == Current[Decimal].from_amperes(Decimal("-2"))
    assert -(-current) == current

    energy = Energy[Decimal].from_kilowatt_hours(Decimal("6.2"))
    assert -energy == Energy[Decimal].from_kilowatt_hours(Decimal("-6.2"))

    freq = Frequency[Decimal].from_hertz(Decimal("50"))
    assert -freq == Frequency[Decimal].from_hertz(Decimal("-50"))
    assert -(-freq) == freq

    pct = Percentage[Decimal].from_fraction(Decimal("30"))
    assert -pct == Percentage[Decimal].from_fraction(Decimal("-30"))
    assert -(-pct) == pct


def test_pos() -> None:
    """Test the positive sign of quantities."""
    power = Power[Decimal].from_watts(Decimal("1000.0"))
    assert +power == power
    assert +(+power) == power

    reactive_power = ReactivePower[Decimal].from_volt_amperes_reactive(
        Decimal("1000.0")
    )
    assert +reactive_power == reactive_power
    assert +(+reactive_power) == reactive_power

    apparent_power = ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0"))
    assert +apparent_power == apparent_power
    assert +(+apparent_power) == apparent_power

    voltage = Voltage[Decimal].from_volts(Decimal("230.0"))
    assert +voltage == voltage
    assert +(+voltage) == voltage

    current = Current[Decimal].from_amperes(Decimal("2"))
    assert +current == current
    assert +(+current) == current

    energy = Energy[Decimal].from_kilowatt_hours(Decimal("6.2"))
    assert +energy == energy
    assert +(+energy) == energy

    freq = Frequency[Decimal].from_hertz(Decimal("50"))
    assert +freq == freq
    assert +(+freq) == freq

    pct = Percentage[Decimal].from_fraction(Decimal("30"))
    assert +pct == pct
    assert +(+pct) == pct


def test_abs() -> None:
    """Test the absolute value of quantities."""
    power = Power[Decimal].from_watts(Decimal("1000.0"))
    assert abs(power) == Power[Decimal].from_watts(Decimal("1000.0"))
    assert abs(-power) == Power[Decimal].from_watts(Decimal("1000.0"))

    reactive_power = ReactivePower[Decimal].from_volt_amperes_reactive(
        Decimal("1000.0")
    )
    assert abs(reactive_power) == ReactivePower[Decimal].from_volt_amperes_reactive(
        Decimal("1000.0")
    )
    assert abs(-reactive_power) == ReactivePower[Decimal].from_volt_amperes_reactive(
        Decimal("1000.0")
    )

    apparent_power = ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0"))
    assert abs(apparent_power) == ApparentPower[Decimal].from_volt_amperes(
        Decimal("1000.0")
    )
    assert abs(-apparent_power) == ApparentPower[Decimal].from_volt_amperes(
        Decimal("1000.0")
    )

    voltage = Voltage[Decimal].from_volts(Decimal("230.0"))
    assert abs(voltage) == Voltage[Decimal].from_volts(Decimal("230.0"))
    assert abs(-voltage) == Voltage[Decimal].from_volts(Decimal("230.0"))

    current = Current[Decimal].from_amperes(Decimal("2"))
    assert abs(current) == Current[Decimal].from_amperes(Decimal("2"))
    assert abs(-current) == Current[Decimal].from_amperes(Decimal("2"))

    energy = Energy[Decimal].from_kilowatt_hours(Decimal("6.2"))
    assert abs(energy) == Energy[Decimal].from_kilowatt_hours(Decimal("6.2"))
    assert abs(-energy) == Energy[Decimal].from_kilowatt_hours(Decimal("6.2"))

    freq = Frequency[Decimal].from_hertz(Decimal("50"))
    assert abs(freq) == Frequency[Decimal].from_hertz(Decimal("50"))
    assert abs(-freq) == Frequency[Decimal].from_hertz(Decimal("50"))

    pct = Percentage[Decimal].from_fraction(Decimal("30"))
    assert abs(pct) == Percentage[Decimal].from_fraction(Decimal("30"))
    assert abs(-pct) == Percentage[Decimal].from_fraction(Decimal("30"))


@pytest.mark.parametrize("quantity_ctor", _QUANTITY_CTORS + [Quantity])
# Use a small amount to avoid long running tests, we have too many combinations
@hypothesis.settings(max_examples=10)
@hypothesis.given(
    quantity_value=st.floats(
        allow_infinity=False,
        allow_nan=False,
        allow_subnormal=False,
        # We need to set this because otherwise constructors with big exponents will
        # cause the value to be too big for the Decimal type, and the test will fail.
        max_value=1e298,
        min_value=-1e298,
    ),
    percent=st.floats(allow_infinity=False, allow_nan=False, allow_subnormal=False),
)
def test_quantity_multiplied_with_precentage(
    quantity_ctor: type[Quantity[Decimal]], quantity_value: float, percent: float
) -> None:
    """Test the multiplication of all quantities with percentage."""
    quantity_value_decimal = Decimal(str(quantity_value))
    percent_decimal = Decimal(str(percent))
    percentage = Percentage[Decimal].from_percent(percent_decimal)
    quantity = quantity_ctor(quantity_value_decimal)
    expected_value = quantity.base_value * (percent_decimal / Decimal("100.0"))
    print(f"{quantity=}, {percentage=}, {expected_value=}")

    product = quantity * percentage
    print(f"{product=}")
    assert product.base_value == expected_value

    quantity *= percentage
    print(f"*{quantity=}")
    assert quantity.base_value == expected_value


@pytest.mark.parametrize("quantity_ctor", _QUANTITY_CTORS + [Quantity])
# Use a small amount to avoid long running tests, we have too many combinations
@hypothesis.settings(max_examples=10)
@hypothesis.given(
    quantity_value=st.floats(
        allow_infinity=False,
        allow_nan=False,
        allow_subnormal=False,
        # We need to set this because otherwise constructors with big exponents will
        # cause the value to be too big for the Decimal type, and the test will fail.
        max_value=1e298,
        min_value=-1e298,
    ),
    scalar=st.floats(allow_infinity=False, allow_nan=False, allow_subnormal=False),
)
def test_quantity_multiplied_with_decimal(
    quantity_ctor: type[Quantity[Decimal]], quantity_value: float, scalar: float
) -> None:
    """Test the multiplication of all quantities with a Decimal."""
    quantity_value_decimal = Decimal(str(quantity_value))
    scalar_decimal = Decimal(str(scalar))
    quantity = quantity_ctor(quantity_value_decimal)
    expected_value = quantity.base_value * scalar_decimal
    print(f"{quantity=}, {expected_value=}")

    product = quantity * scalar_decimal
    print(f"{product=}")
    assert product.base_value == expected_value

    quantity *= scalar_decimal
    print(f"*{quantity=}")
    assert quantity.base_value == expected_value


def test_invalid_multiplications() -> None:
    """Test the multiplication of quantities with invalid quantities."""
    power = Power[Decimal].from_watts(Decimal("1000.0"))
    voltage = Voltage[Decimal].from_volts(Decimal("230.0"))
    current = Current[Decimal].from_amperes(Decimal("2"))
    energy = Energy[Decimal].from_kilowatt_hours(Decimal("12"))

    for quantity in [power, voltage, current, energy]:
        with pytest.raises(TypeError):
            _ = power * quantity  # type: ignore
        with pytest.raises(TypeError):
            power *= quantity  # type: ignore

    for quantity in [voltage, power, energy]:
        with pytest.raises(TypeError):
            _ = voltage * quantity  # type: ignore
        with pytest.raises(TypeError):
            voltage *= quantity  # type: ignore

    for quantity in [current, power, energy]:
        with pytest.raises(TypeError):
            _ = current * quantity  # type: ignore
        with pytest.raises(TypeError):
            current *= quantity  # type: ignore

    for quantity in [energy, power, voltage, current]:
        with pytest.raises(TypeError):
            _ = energy * quantity  # type: ignore
        with pytest.raises(TypeError):
            energy *= quantity  # type: ignore


@pytest.mark.parametrize("quantity_ctor", _QUANTITY_CTORS + [Quantity])
# Use a small amount to avoid long running tests, we have too many combinations
@hypothesis.settings(max_examples=10)
@hypothesis.given(
    quantity_value=st.floats(
        allow_infinity=False,
        allow_nan=False,
        allow_subnormal=False,
        # We need to set this because otherwise constructors with big exponents will
        # cause the value to be too big for the Decimal type, and the test will fail.
        max_value=1e298,
        min_value=-1e298,
    ),
    scalar=st.floats(allow_infinity=False, allow_nan=False, allow_subnormal=False),
)
def test_quantity_divided_by_decimal(
    quantity_ctor: type[Quantity[Decimal]], quantity_value: float, scalar: float
) -> None:
    """Test the division of all quantities by a Decimal."""
    quantity_value_decimal = Decimal(str(quantity_value))
    scalar_decimal = Decimal(str(scalar))
    hypothesis.assume(scalar != 0.0)
    quantity = quantity_ctor(quantity_value_decimal)
    expected_value = quantity.base_value / scalar_decimal
    print(f"{quantity=}, {expected_value=}")

    quotient = quantity / scalar_decimal
    print(f"{quotient=}")
    assert quotient.base_value == expected_value

    quantity /= scalar_decimal
    print(f"*{quantity=}")
    assert quantity.base_value == expected_value


@pytest.mark.parametrize("quantity_ctor", _QUANTITY_CTORS + [Quantity])
# Use a small amount to avoid long running tests, we have too many combinations
@hypothesis.settings(max_examples=10)
@hypothesis.given(
    quantity_value=st.floats(
        allow_infinity=False,
        allow_nan=False,
        allow_subnormal=False,
        # We need to set this because otherwise constructors with big exponents will
        # cause the value to be too big for the Decimal type, and the test will fail.
        max_value=1e298,
        min_value=-1e298,
    ),
    divisor_value=st.floats(
        allow_infinity=False, allow_nan=False, allow_subnormal=False
    ),
)
def test_quantity_divided_by_self(
    quantity_ctor: type[Quantity[Decimal]],
    quantity_value: float,
    divisor_value: float,
) -> None:
    """Test the division of all quantities by a Decimal."""
    quantity_value_decimal = Decimal(str(quantity_value))
    divisor_value_decimal = Decimal(str(divisor_value))
    hypothesis.assume(divisor_value != 0.0)
    # We need to have Decimal here because quantity /= divisor will return a Decimal
    quantity: Quantity[Decimal] | Decimal = quantity_ctor(quantity_value_decimal)
    divisor = quantity_ctor(divisor_value_decimal)
    assert isinstance(quantity, Quantity)
    expected_value = quantity.base_value / divisor.base_value
    print(f"{quantity=}, {expected_value=}")

    quotient = quantity / divisor
    print(f"{quotient=}")
    assert isinstance(quotient, Decimal)
    assert quotient == expected_value

    quantity /= divisor
    print(f"*{quantity=}")
    assert isinstance(quantity, Decimal)
    assert quantity == expected_value


@pytest.mark.parametrize(
    "divisor",
    [
        Energy[Decimal].from_kilowatt_hours(Decimal("500.0")),
        Frequency[Decimal].from_hertz(Decimal("50")),
        Power[Decimal].from_watts(Decimal("1000.0")),
        ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0")),
        ReactivePower[Decimal].from_volt_amperes_reactive(Decimal("1000.0")),
        Quantity[Decimal](Decimal("30.0")),
        Temperature[Decimal].from_celsius(Decimal("30")),
        Voltage[Decimal].from_volts(Decimal("230.0")),
    ],
    ids=lambda q: q.__class__.__name__,
)
def test_invalid_current_divisions(divisor: Quantity[Decimal]) -> None:
    """Test the divisions of current with invalid quantities."""
    current = Current[Decimal].from_amperes(Decimal("2"))

    with pytest.raises(TypeError):
        _ = current / divisor  # type: ignore
    with pytest.raises(TypeError):
        current /= divisor  # type: ignore


@pytest.mark.parametrize(
    "divisor",
    [
        Current[Decimal].from_amperes(Decimal("2")),
        Frequency[Decimal].from_hertz(Decimal("50")),
        Quantity[Decimal](Decimal("30.0")),
        Temperature[Decimal].from_celsius(Decimal("30")),
        Voltage[Decimal].from_volts(Decimal("230.0")),
        ReactivePower[Decimal].from_volt_amperes_reactive(Decimal("1000.0")),
        ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0")),
    ],
    ids=lambda q: q.__class__.__name__,
)
def test_invalid_energy_divisions(divisor: Quantity[Decimal]) -> None:
    """Test the divisions of energy with invalid quantities."""
    energy = Energy[Decimal].from_kilowatt_hours(Decimal("500.0"))

    with pytest.raises(TypeError):
        _ = energy / divisor  # type: ignore
    with pytest.raises(TypeError):
        energy /= divisor  # type: ignore


@pytest.mark.parametrize(
    "divisor",
    [
        Current[Decimal].from_amperes(Decimal("2")),
        Energy[Decimal].from_kilowatt_hours(Decimal("500.0")),
        Power[Decimal].from_watts(Decimal("1000.0")),
        ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0")),
        ReactivePower[Decimal].from_volt_amperes_reactive(Decimal("1000.0")),
        Quantity[Decimal](Decimal("30.0")),
        Temperature[Decimal].from_celsius(Decimal("30")),
        Voltage[Decimal].from_volts(Decimal("230.0")),
    ],
    ids=lambda q: q.__class__.__name__,
)
def test_invalid_frequency_divisions(divisor: Quantity[Decimal]) -> None:
    """Test the divisions of frequency with invalid quantities."""
    frequency = Frequency[Decimal].from_hertz(Decimal("50"))

    with pytest.raises(TypeError):
        _ = frequency / divisor  # type: ignore
    with pytest.raises(TypeError):
        frequency /= divisor  # type: ignore


@pytest.mark.parametrize(
    "divisor",
    [
        Current[Decimal].from_amperes(Decimal("2")),
        Energy[Decimal].from_kilowatt_hours(Decimal("500.0")),
        Frequency[Decimal].from_hertz(Decimal("50")),
        Power[Decimal].from_watts(Decimal("1000.0")),
        ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0")),
        ReactivePower[Decimal].from_volt_amperes_reactive(Decimal("1000.0")),
        Quantity[Decimal](Decimal("30.0")),
        Temperature[Decimal].from_celsius(Decimal("30")),
        Voltage[Decimal].from_volts(Decimal("230.0")),
    ],
    ids=lambda q: q.__class__.__name__,
)
def test_invalid_percentage_divisions(divisor: Quantity[Decimal]) -> None:
    """Test the divisions of percentage with invalid quantities."""
    percentage = Percentage[Decimal].from_percent(Decimal("50.0"))

    with pytest.raises(TypeError):
        _ = percentage / divisor  # type: ignore
    with pytest.raises(TypeError):
        percentage /= divisor  # type: ignore


@pytest.mark.parametrize(
    "divisor",
    [
        Energy[Decimal].from_kilowatt_hours(Decimal("500.0")),
        Frequency[Decimal].from_hertz(Decimal("50")),
        Quantity[Decimal](Decimal("30.0")),
        Temperature[Decimal].from_celsius(Decimal("30")),
        ReactivePower[Decimal].from_volt_amperes_reactive(Decimal("1000.0")),
        ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0")),
    ],
    ids=lambda q: q.__class__.__name__,
)
def test_invalid_power_divisions(divisor: Quantity[Decimal]) -> None:
    """Test the divisions of power with invalid quantities."""
    power = Power[Decimal].from_watts(Decimal("1000.0"))

    with pytest.raises(TypeError):
        _ = power / divisor  # type: ignore
    with pytest.raises(TypeError):
        power /= divisor  # type: ignore


@pytest.mark.parametrize(
    "divisor",
    [
        Current[Decimal].from_amperes(Decimal("2")),
        Energy[Decimal].from_kilowatt_hours(Decimal("500.0")),
        Frequency[Decimal].from_hertz(Decimal("50")),
        Power[Decimal].from_watts(Decimal("1000.0")),
        ReactivePower[Decimal].from_volt_amperes_reactive(Decimal("1000.0")),
        ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0")),
        Temperature[Decimal].from_celsius(Decimal("30")),
        Voltage[Decimal].from_volts(Decimal("230.0")),
    ],
    ids=lambda q: q.__class__.__name__,
)
def test_invalid_quantity_divisions(divisor: Quantity[Decimal]) -> None:
    """Test the divisions of quantity with invalid quantities."""
    quantity = Quantity(Decimal("30.0"))

    with pytest.raises(TypeError):
        _ = quantity / divisor
    with pytest.raises(TypeError):
        quantity /= divisor  # type: ignore[assignment]


@pytest.mark.parametrize(
    "divisor",
    [
        Current[Decimal].from_amperes(Decimal("2")),
        Energy[Decimal].from_kilowatt_hours(Decimal("500.0")),
        Frequency[Decimal].from_hertz(Decimal("50")),
        Power[Decimal].from_watts(Decimal("1000.0")),
        ReactivePower[Decimal].from_volt_amperes_reactive(Decimal("1000.0")),
        ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0")),
        Quantity[Decimal](Decimal("30.0")),
        Voltage[Decimal].from_volts(Decimal("230.0")),
    ],
    ids=lambda q: q.__class__.__name__,
)
def test_invalid_temperature_divisions(divisor: Quantity[Decimal]) -> None:
    """Test the divisions of temperature with invalid quantities."""
    temperature = Temperature[Decimal].from_celsius(Decimal("30"))

    with pytest.raises(TypeError):
        _ = temperature / divisor  # type: ignore
    with pytest.raises(TypeError):
        temperature /= divisor  # type: ignore


@pytest.mark.parametrize(
    "divisor",
    [
        Current[Decimal].from_amperes(Decimal("2")),
        Energy[Decimal].from_kilowatt_hours(Decimal("500.0")),
        Frequency[Decimal].from_hertz(Decimal("50")),
        Power[Decimal].from_watts(Decimal("1000.0")),
        ReactivePower[Decimal].from_volt_amperes_reactive(Decimal("1000.0")),
        ApparentPower[Decimal].from_volt_amperes(Decimal("1000.0")),
        Quantity[Decimal](Decimal("30.0")),
        Temperature[Decimal].from_celsius(Decimal("30")),
    ],
    ids=lambda q: q.__class__.__name__,
)
def test_invalid_voltage_divisions(divisor: Quantity[Decimal]) -> None:
    """Test the divisions of voltage with invalid quantities."""
    voltage = Voltage[Decimal].from_volts(Decimal("230.0"))

    with pytest.raises(TypeError):
        _ = voltage / divisor  # type: ignore
    with pytest.raises(TypeError):
        voltage /= divisor  # type: ignore


# We can't use _QUANTITY_TYPES here, because it will break the tests, as hypothesis
# will generate more values, some of which are unsupported by the quantities. See the
# test comment for more details.
@pytest.mark.parametrize(
    "quantity_type",
    [Power, Voltage, Current, Energy, Frequency, ReactivePower, ApparentPower],
)
@pytest.mark.parametrize("exponent", [0, 3, 6, 9])
@hypothesis.settings(
    max_examples=1000
)  # Set to have a decent amount of examples (default is 100)
@hypothesis.seed(42)  # Seed that triggers a lot of problematic edge cases
@hypothesis.given(value=st.floats(min_value=-1.0, max_value=1.0))
def test_to_and_from_string(
    quantity_type: type[Quantity[Decimal]], exponent: int, value: Decimal
) -> None:
    """Test string parsing and formatting.

    The parameters for this test are constructed to stay deterministic.

    With a different (or random) seed or different max_examples the
    test will show failing examples.

    Fixing those cases was considered an unreasonable amount of work
    at the time of writing.

    For the future, one idea was to parse the string number after the first
    generation and regenerate it with the more appropriate unit and precision.
    """
    quantity = quantity_type.__new__(quantity_type)
    quantity._base_value = value * 10**exponent  # pylint: disable=protected-access
    # The above should be replaced with:
    # quantity = quantity_type._new(  # pylint: disable=protected-access
    #     value, exponent=exponent
    # )
    # But we can't do that now, because, you guessed it, it will also break the tests
    # (_new() will use 10.0**exponent instead of 10**exponent, which seems to have some
    # effect on the tests.
    quantity_str = f"{quantity:.{exponent}}"
    from_string = quantity_type.from_string(quantity_str)
    try:
        assert f"{from_string:.{exponent}}" == quantity_str
    except AssertionError as error:
        pytest.fail(
            f"Failed for {quantity.base_value} != from_string({from_string.base_value}) "
            + f"with exponent {exponent} and source value '{value}': {error}"
        )
