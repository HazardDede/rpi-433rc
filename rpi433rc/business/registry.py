import attr

from .devices import DeviceStore, UnknownDeviceError, Device
from .state import DeviceState
from .rc433 import RC433


@attr.s
class StatefulDevice(object):
    """
    Adds a state (on resp. off) to a device entity.

    Example:

        >>> device = Device('device1')
        >>> StatefulDevice(device, True)
        StatefulDevice(device=Device(device_name='device1'), state=True)
    """
    device = attr.ib(validator=attr.validators.instance_of(Device))
    state = attr.ib(validator=attr.validators.instance_of(bool))


@attr.s
class DeviceRegistry(DeviceStore, DeviceState):
    """
    The device registry associates a DeviceStore (where the actual devices are stored / configured) and
    a DeviceState (where the state of the devices are tracked).

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
        ...     [StatefulDevice(device=CodeDevice(device_name='device1', code_on=12345, code_off=23456), state=False),
        ...     StatefulDevice(device=SystemDevice(device_name='device2', system_code='00010', device_code=2)
        ...     , state=False)])
        True

        >>> ((dut.lookup('device1'), dut.switch('device1', True), dut.lookup('device1')) ==
        ...     (StatefulDevice(device=CodeDevice(device_name='device1', code_on=12345, code_off=23456), state=False),
        ...     True,
        ...     StatefulDevice(device=CodeDevice(device_name='device1', code_on=12345, code_off=23456), state=True)))
        True

    """
    device_store = attr.ib(validator=attr.validators.instance_of(DeviceStore))
    device_state = attr.ib(validator=attr.validators.instance_of(DeviceState))
    rc433 = attr.ib(validator=attr.validators.instance_of(RC433))

    def lookup(self, device):
        if not isinstance(device, Device):
            # Assuming a device name instead of a real device
            device = self.device_store.lookup(device)

        if device is None:
            raise UnknownDeviceError("The requested device '{}' is unknown".format(str(device)))

        return StatefulDevice(device=device, state=self.device_state.lookup(device.device_name))

    def list(self):
        return [self.lookup(device) for device in self.device_store.list()]

    def switch(self, device_or_name, on):
        device = self.lookup(device_or_name)
        res = self.rc433.switch_device(device, on)
        if res:
            self.device_state.switch(device_or_name, on)
        return res
