import pytest


class RFDeviceDummy(object):
    def __init__(self, *args, **kwargs):
        pass

    def enable_tx(self):
        pass

    def cleanup(self):
        pass

    def tx_code(self, code, **kwargs):
        return True


def test_send_code():
    from rpi433rc.business.rc433 import RC433
    dut = RC433(gpio_out=17)
    dut.rf_device = RFDeviceDummy()

    assert dut.send_code(12345)
    with pytest.raises(TypeError):
        dut.send_code("abc")


def test_switch_device():
    from rpi433rc.business.devices import CodeDevice, SystemDevice
    from rpi433rc.business.rc433 import RC433, UnsupportedDeviceError

    dut = RC433(gpio_out=17)
    dut.rf_device = RFDeviceDummy()

    cd = CodeDevice(device_name='device1', code_on=12345, code_off=12345)
    assert dut.switch_device(cd, True)

    with pytest.raises(UnsupportedDeviceError):
        dut.switch_device(SystemDevice('device2', system_code="01010", device_code=4), True)
