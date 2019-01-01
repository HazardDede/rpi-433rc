import json
from abc import abstractmethod
from collections import defaultdict

import attr

from schema import Schema, Or, Use, Optional

from .util import LogMixin


class UnknownDeviceError(Exception):
    pass


@attr.s
class Device(object):
    """
    Base class for different 433mhz devices.

    Example:

        >>> d1 = Device(device_name='device1')
        >>> print(repr(d1))
        Device(device_name='device1')

        >>> Device.props() == {'device_name': (str, None)}
        True
    """
    device_name = attr.ib(converter=str)

    @property
    def configuration(self):
        return {name: getattr(self, name, None) for name, _ in self.props().items() if name != 'device_name'}

    @classmethod
    def props(cls):
        return {a.name: (a.converter, None if a.default is attr.NOTHING else a.default) for a in cls.__attrs_attrs__}

    @classmethod
    def from_props(cls, device_name, props):
        return cls(device_name=device_name, **props)


@attr.s
class CodeDevice(Device):
    """
    Specialized 433mhz device that can be controlled by specifying different codes for on and off.

    Example:

        >>> d2 = CodeDevice(device_name='device2', code_on="12345", code_off=23456, resend=1)
        >>> print(repr(d2))
        CodeDevice(device_name='device2', code_on=12345, code_off=23456, resend=1)

        >>> CodeDevice.props() == {'device_name': (str, None), 'code_on': (int, None),
        ...                        'code_off': (int, None), 'resend': (int, 3)}
        True
    """
    code_on = attr.ib(converter=int)
    code_off = attr.ib(converter=int)
    resend = attr.ib(converter=int, validator=lambda i, a, v: v > 0, default=3)


@attr.s
class SystemDevice(Device):
    """
    Specialized 433mhz device that can be controlled by specifying a system code and a unit code.

    Example:

        >>> d3 = SystemDevice(device_name='device3', system_code="00111", device_code="4")
        >>> print(repr(d3))
        SystemDevice(device_name='device3', system_code='00111', device_code=4, resend=3)

        >>> SystemDevice.props() == {'device_name': (str, None), 'system_code': (str, None),
        ...                          'device_code': (int, None), 'resend': (int, 3)}
        True
    """
    system_code = attr.ib(converter=str)
    device_code = attr.ib(converter=int)
    resend = attr.ib(converter=int, validator=lambda i, a, v: v > 0, default=3)


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


__ALL_DEVICES__ = [CodeDevice, SystemDevice]


@attr.s
class DeviceStore(LogMixin):
    """
    Abstract base classes for storing / fetching configured devices.
    """

    @abstractmethod
    def list(self):
        """
        Lists all configured devices.

        Returns:
            Returns a list of all configured devices.
        """
        pass

    @abstractmethod
    def lookup(self, device_name):
        """
        Lookup a given device by its name.

        Args:
            device_name (str): Device name to lookup.

        Returns:
            Returns the actual device if found; otherwise a `UnknownDeviceError` is raised.
        """
        pass


@attr.s
class DeviceDict(DeviceStore):
    """
    Parses the devices information from the specified python dictionary.

    Example:

        >>> device_dict = {
        ...     'device1': {"code_on": 12345, 'code_off': "23456"},
        ...     'device2': {"system_code": "00010", "device_code": "2"}
        ... }
        >>> dut = DeviceDict(device_dict)
        >>> (sorted(dut.list(), key=lambda e: e.device_name) ==
        ...     [CodeDevice(device_name='device1', code_on=12345, code_off=23456),
        ...     SystemDevice(device_name='device2', system_code='00010', device_code=2)])
        True

        >>> dut.lookup('device1')
        CodeDevice(device_name='device1', code_on=12345, code_off=23456, resend=3)

        >>> dut.lookup('unknown')
        Traceback (most recent call last):
        ...
        rpi433rc.business.devices.UnknownDeviceError: The requested device 'unknown' is unknown

        >>> import tempfile
        >>> fn = tempfile.NamedTemporaryFile().name
        >>> with open(fn, 'w') as fp:
        ...     json.dump(device_dict, fp)
        >>> dut = DeviceDict.from_json(fn)
        >>> (sorted(dut.list(), key=lambda e: e.device_name) ==
        ...     [CodeDevice(device_name='device1', code_on=12345, code_off=23456),
        ...     SystemDevice(device_name='device2', system_code='00010', device_code=2)])
        True
    """
    device_dict = attr.ib(validator=attr.validators.instance_of(dict))
    devices = attr.ib(default=None, repr=False, cmp=False, hash=False, init=False)

    @property
    def validation_schema(self):
        device_schemas = list()
        for dev in __ALL_DEVICES__:
            props = dev.props()
            device_schemas.append({
                k if default is None else Optional(k, default=default): Use(conv)
                for k, (conv, default) in props.items() if k != 'device_name'
            })

        return Schema({
            str: Or(*device_schemas)
        })

    @classmethod
    def from_json(cls, file_name):
        """
        Instead from dictionary loads the devices from a json file.

        Args:
            file_name (str): Path of the file to load the devices from.

        Returns:
            Returns a `DeviceDict` that is initialized from the given json file.
        """
        with open(file_name, 'r') as fp:
            jsonf = json.load(fp)

        return DeviceDict(jsonf)

    def _init_devices(self):
        def _init_device(device_name, props):
            for dev in __ALL_DEVICES__:
                try:
                    return dev.from_props(device_name, props)
                except (TypeError, ValueError):
                    # import traceback
                    # traceback.print_exc()
                    pass

            raise ValueError("Misconfigured device '{}'".format(device_name))

        self.devices = {
            device_name: _init_device(device_name, props)
            for device_name, props in self.validation_schema.validate(self.device_dict).items()
        }

    def list(self):
        """
        Lists all configured devices.

        Returns:
            Returns a list of all configured devices.
        """
        if self.devices is None:
            self._init_devices()

        return [device for _, device in self.devices.items()]

    def lookup(self, device_name):
        """
        Lookup a given device by its name.

        Args:
            device_name (str): Device name to lookup.

        Returns:
            Returns the actual device if found; otherwise a `UnknownDeviceError` is raised.
        """
        if self.devices is None:
            self._init_devices()

        res = self.devices.get(device_name, None)
        if res is None:
            raise UnknownDeviceError("The requested device '{}' is unknown".format(device_name))
        return res


class DeviceState(object):
    """
    Abstract base class for a device state tracker.
    """
    def _device_name(self, device_or_name):
        if isinstance(device_or_name, Device):
            return device_or_name.device_name

        return device_or_name

    @abstractmethod
    def lookup(self, device_or_name):
        """
        Lookup the state of a single device by the specified name or entity.

        Args:
            device_or_name: A real device entity (Device) or it's name

        Returns:
            Returns True if the device is currently on; otherwise False.
        """
        pass

    @abstractmethod
    def switch(self, device_or_name, on):
        """
        Switch on / off the specified device.

        Args:
            device_or_name: A real device entity (Device) or it's name
            on: If True the device will be marked as on; otherwise off.

        Returns:
            None
        """
        pass


class MemoryState(DeviceState):
    """
    In-memory implementation of a device state mapping.

    Example:

        >>> dut = MemoryState()
        >>> dut.lookup(Device('device1'))
        False

        >>> dut.switch(Device('device2'), True)
        >>> dut.lookup(Device('device1')), dut.lookup(Device('device2'))
        (False, True)
    """
    def __init__(self):
        self.states = defaultdict(bool)

    def lookup(self, device_or_name):
        """
        Lookup the state of a single device by the specified name or entity.

        Args:
            device_or_name: A real device entity (Device) or it's name

        Returns:
            Returns True if the device is currently on; otherwise False.
        """
        return self.states.get(self._device_name(device_or_name), False)

    def switch(self, device_or_name, on):
        """
        Switch on / off the specified device.

        Args:
            device_or_name: A real device entity (Device) or it's name
            on: If True the device will be marked as on; otherwise off.

        Returns:
            None
        """
        self.states[self._device_name(device_or_name)] = on


@attr.s
class DeviceRegistry(DeviceStore, DeviceState):
    """
    The device registry associates a DeviceStore (where the actual devices are stored / configured) and
    a DeviceState (where the state of the devices are tracked).

    Example:

        >>> device_dict = {
        ...     'device1': {"code_on": 12345, 'code_off': "23456"},
        ...     'device2': {"system_code": "00010", "device_code": "2"}
        ... }
        >>> dstore = DeviceDict(device_dict)  # Instantiate the device store
        >>> dstate = MemoryState()  # Instantiate the device state
        >>> dut = DeviceRegistry(dstore, dstate)

        >>> (sorted(dut.list(), key=lambda e: e.device.device_name) ==
        ...     [StatefulDevice(device=CodeDevice(device_name='device1', code_on=12345, code_off=23456), state=False),
        ...     StatefulDevice(device=SystemDevice(device_name='device2', system_code='00010', device_code=2)
        ...     , state=False)])
        True

        >>> ((dut.lookup('device1'), dut.switch('device1', True), dut.lookup('device1')) ==
        ...     (StatefulDevice(device=CodeDevice(device_name='device1', code_on=12345, code_off=23456), state=False),
        ...     None,
        ...     StatefulDevice(device=CodeDevice(device_name='device1', code_on=12345, code_off=23456), state=True)))
        True

    """
    device_store = attr.ib(validator=attr.validators.instance_of(DeviceStore))
    state = attr.ib(validator=attr.validators.instance_of(DeviceState))

    def lookup(self, device):
        if not isinstance(device, Device):
            # Assuming a device name instead of a real device
            device = self.device_store.lookup(device)

        if device is None:
            raise UnknownDeviceError("The requested device '{}' is unknown".format(str(device)))

        return StatefulDevice(device=device, state=self.state.lookup(device.device_name))

    def list(self):
        return [self.lookup(device) for device in self.device_store.list()]

    def switch(self, device_or_name, on):
        self.state.switch(device_or_name, on)
