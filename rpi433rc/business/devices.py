"""Device related business classes."""
import functools
import json
from abc import abstractmethod

import attr
from schema import Schema, Or, Use, Optional

from ..util import LogMixin


class UnknownDeviceError(Exception):
    """Error to signal a unknown device to the caller."""
    pass  # pylint: disable=unnecessary-pass


@attr.s
class Device:
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
        """Returns the configuration of the device."""
        return {
            name: getattr(self, name, None)
            for name, _ in self.props().items()
            if name != 'device_name'
        }

    @classmethod
    def props(cls):
        """Returns the valid properties of the device."""
        return {
            a.name: (a.converter, None if a.default is attr.NOTHING else a.default)
            for a in cls.__attrs_attrs__
        }

    @classmethod
    def from_props(cls, device_name, props):
        """Creates a device from a property dictionary."""
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


__ALL_DEVICES__ = [CodeDevice, SystemDevice]


def device_validator(fun):
    """
    Adds device specific validation to the decorated function.

    Examples:
        >>> @device_validator
        ... def do(device=None, device_name=None):
        ...    return device, device_name

        >>> from rpi433rc.business.devices import CodeDevice
        >>> do(device=CodeDevice(code_on=1, code_off=2, resend=2, device_name='d1'))
        (CodeDevice(device_name='d1', code_on=1, code_off=2, resend=2), 'd1')

        >>> do(device_name='d1')
        (None, 'd1')

        >>> do(device='d1')  # Bad one: string is no device!
        Traceback (most recent call last):
        ...
        TypeError: Argument 'device' is expected to be an actual `Device`, but it is not.

        >>> do()
        Traceback (most recent call last):
        ...
        TypeError: It is expected either to pass the argument 'device' or ...
    """
    @functools.wraps(fun)
    def _wrap(*args, device=None, device_name=None, **kwargs):
        if not device and not device_name:
            raise TypeError("It is expected either to pass the argument 'device' or"
                            " the argument 'device_name' or both, but not none.")
        if device and not isinstance(device, Device):
            raise TypeError("Argument 'device' is expected to be an actual `Device`,"
                            " but it is not.")
        device_name = device_name or device.device_name
        return fun(*args, device=device, device_name=device_name, **kwargs)

    return _wrap


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
        raise NotImplementedError()

    @abstractmethod
    def lookup(self, device=None, device_name=None):
        """
        Lookup a given device by its name.

        Args:
            device: An actual `business.devices.Device` instance.
            device_name (str): Device name to lookup.

        Returns:
            Returns the actual device if found; otherwise a `UnknownDeviceError` is raised.
        """
        raise NotImplementedError()


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

        >>> dut.lookup(device_name='device1')
        CodeDevice(device_name='device1', code_on=12345, code_off=23456, resend=3)

        >>> dut.lookup(device_name='unknown')
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
        """Dynamically creates a validation schema for the device."""
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
        with open(file_name, 'r') as fpointer:
            jsonf = json.load(fpointer)

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

    @device_validator
    def lookup(self, device=None, device_name=None):
        if self.devices is None:
            self._init_devices()

        res = self.devices.get(device_name, None)
        if res is None:
            raise UnknownDeviceError("The requested device '{}' is unknown".format(device_name))
        return res
