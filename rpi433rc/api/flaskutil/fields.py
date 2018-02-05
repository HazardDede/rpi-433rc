from flask_restplus import fields


class Dict(fields.Raw):
    def format(self, value):
        if isinstance(value, dict):
            return value

        raise fields.MarshallingError("Can not marshal dictionary")


class OnOff(fields.Boolean):
    __schema_type__ = 'string'

    def format(self, value):
        b = super().format(value)
        return "on" if b else "off"
