from werkzeug.routing import BaseConverter


class OnOffConverter(BaseConverter):

    def to_python(self, value):
        return value.lower() == 'on'

    def to_url(self, value):
        return BaseConverter.to_url('on' if value else 'off')
