"""The registry puts everything together. The store is the list of registered devices. The state
is the state handler to handle actual states for the devices and the rc433 is the actual
interface to control the hardware to send 433mhz commands to the power sockets.
"""

import attr

from .devices import DeviceStore, UnknownDeviceError, Device, device_validator
from .rc433 import RC433
from .state import DeviceState


@attr.s
class StatefulDevice:  # pylint: disable=too-few-public-methods
    """
    Adds a state (on resp. off) to a device entity.

    Example:

        >>> device = Device('device1')
        >>> StatefulDevice(device.device_name, device, True)
        StatefulDevice(device_name='device1', device=Device(device_name='device1'), state=True)
    """
    device_name = attr.ib(converter=str)
    device = attr.ib(validator=attr.validators.instance_of(Device))
    state = attr.ib(validator=attr.validators.instance_of(bool))


@attr.s
class DeviceRegistry(DeviceStore, DeviceState):
    """
    The device registry associates a DeviceStore (where the actual devices are stored
    / configured) and a DeviceState (where the state of the devices are tracked).

    Example:

        >>> from rpi433rc.business.devices import DeviceDict, SystemDevice, CodeDevice
        >>> from rpi433rc.business.state import MemoryState
        >>> from rpi433rc.business.rc433 import RFDeviceMock, RC433
        >>> device_dict = {
        ...     'device1': {"code_on": 12345, 'code_off': "23456"},
        ...     'device2': {"system_code": "00010", "device_code": "2"}
        ... }
        >>> dstore = DeviceDict(device_dict)  # Instantiate the device store
        >>> dstate = MemoryState()  # Instantiate the device state
        >>> rc433 = RC433()
        >>> rc433.rf_device = RFDeviceMock()
        >>> dut = DeviceRegistry(dstore, dstate, rc433)

        >>> (sorted(dut.list(), key=lambda e: e.device.device_name) ==
        ...     [StatefulDevice(device_name='device1', device=CodeDevice(device_name='device1',
        ...         code_on=12345, code_off=23456), state=False),
        ...     StatefulDevice(device_name='device2', device=SystemDevice(device_name='device2',
        ...         system_code='00010', device_code=2), state=False)])
        True

        >>> (dut.lookup(device_name='device1') ==
        ...     StatefulDevice(device_name='device1', device=CodeDevice(device_name='device1',
        ...         code_on=12345, code_off=23456), state=False))
        True

        >>> dut.switch(True, device_name='device1')
        True

        >>> (dut.lookup(device_name='device1') ==
        ...     StatefulDevice(device_name='device1', device=CodeDevice(device_name='device1',
        ...         code_on=12345, code_off=23456), state=True))
        True

    """

    device_store = attr.ib(validator=attr.validators.instance_of(DeviceStore))
    device_state = attr.ib(validator=attr.validators.instance_of(DeviceState))
    rc433 = attr.ib(validator=attr.validators.instance_of(RC433))

    def __attrs_post_init__(self):
        self._init_all_devices()

    def _init_all_devices(self):
        for dev in self.device_store.list():
            try:
                self.init_device(dev)
            except Exception:  # pylint: disable=broad-except
                import traceback
                self.logger.error(traceback.format_exc())
        self.init_done()

    def init_device(self, device):
        self.device_state.init_device(device)

    def init_done(self):
        self.device_state.init_done()

    @device_validator
    def lookup(self, device=None, device_name=None):
        if not device:
            device = self.device_store.lookup(device=device, device_name=device_name)

        if device is None:
            raise UnknownDeviceError("The requested device '{}' is unknown".format(str(device)))

        return StatefulDevice(
            device_name=device.device_name,
            device=device,
            state=self.device_state.lookup(device=device, device_name=device_name)
        )

    def list(self):
        self.logger.debug("[list] using %s (%s)", self.device_state, hex(id(self.device_state)))
        return [self.lookup(device=device) for device in self.device_store.list()]

    @device_validator
    def switch(self, on_off, device=None, device_name=None):
        state_device = self.lookup(device=device, device_name=device_name)
        self.logger.info("Switching %s from %s to %s",
                         state_device.device_name, state_device.state, on_off)
        # rc433 and state component do not know about StatefulDevices
        res = self.rc433.switch_device(on_off, state_device.device)
        if res:
            self.device_state.switch(on_off, device=state_device.device, device_name=device_name)
        return res
