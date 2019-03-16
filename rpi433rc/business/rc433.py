"""RC433 related components. The heart to control 433mhz power sockets."""

import attr

from rpi433rc.util import LogMixin
from .devices import CodeDevice


class RFDeviceMock:
    """Mocking the class inside package rpi_rf if it is not available."""
    def __init__(self, *args, **kwargs):
        pass

    def enable_tx(self):  # pylint: disable=missing-docstring
        pass

    def cleanup(self):  # pylint: disable=missing-docstring
        pass

    def tx_code(self, code, **kwargs):  # pylint: disable=missing-docstring,unused-argument,no-self-use
        return True


try:
    import rpi_rf
    RFDevice = rpi_rf.RFDevice  # pylint: disable=invalid-name
except ImportError:
    # Mock it on non-rpi machines
    RFDevice = RFDeviceMock


class UnsupportedDeviceError(Exception):
    """Raised when a device is unsupported."""
    pass  # pylint: disable=unnecessary-pass


@attr.s
class RC433(LogMixin):
    """
    Remote control 433mhz devices.
    """
    gpio_out = attr.ib(default=17, converter=int, validator=attr.validators.instance_of(int))
    rf_device = attr.ib(default=None, init=False)

    def _initialize(self):
        """Sets the RFDevice to transmit state if necessary"""
        if self.rf_device is None:
            self.rf_device = RFDevice(self.gpio_out)
            self.rf_device.enable_tx()

    def __del__(self):
        """Stops transmitting."""
        if self.rf_device is not None:
            self.rf_device.cleanup()
            self.rf_device = None

    def send_code(self, code, times=3):
        """
        Sends a decimal code via 433mhz. This implementation will actually send
        the code multiple times to make sure that any disturbance in the force has less impact.

        Args:
            code (int): Code to send
            times (int):

        Returns:
            Returns True if the underlying RFDevice acknowledged; otherwise False.
        """
        if not isinstance(code, int):
            raise TypeError("Argument code is expected to be an int, but given is '{}'"
                            .format(type(code)))
        if not isinstance(times, int):
            raise TypeError("Argument times is expected to be an int, but is '{}'"
                            .format(type(times)))

        if times <= 0:
            times = 1

        self._initialize()
        self.logger.debug("Sending code '%s' for %s times", code, str(times))
        return any([self.rf_device.tx_code(code) for _ in range(times)])

    def switch_device(self, on_off, device):
        """
        Switches the specified device to on resp. off.

        Remark: Unfortunately any device besides the CodeDevice is not supported so far.

        Args:
            device (rpi433rc.business.devices.Device): The device to turn on resp. off
            on_off (bool): If True the device will be set on; otherwise off.

        Returns:
            Returns True if the underlying RFDevice acknowledged; otherwise False.
        """
        self.logger.debug("Device switch for '%s' to '%s' requested", str(device), str(on_off))
        if isinstance(device, CodeDevice):
            return self.send_code(
                device.code_on if on_off else device.code_off,
                times=device.resend
            )

        raise UnsupportedDeviceError("The device type '{}' is not supported".format(type(device)))
