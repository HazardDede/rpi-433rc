"""Provides some additional field validation and serialization for flask."""

from flask_restplus import fields


class Dict(fields.Raw):
    """Dictionary serializer."""
    def format(self, value):
        """Formats the given value according to the fields strategy."""
        if isinstance(value, dict):
            return value

        raise fields.MarshallingError("Can not marshal dictionary")


class OnOff(fields.Boolean):
    """On/Off serializer for boolean."""
    __schema_type__ = 'string'

    def format(self, value):
        """Formats the given value according to the fields strategy."""
        boolean = super().format(value)
        return "on" if boolean else "off"
