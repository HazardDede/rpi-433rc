from werkzeug.routing import BaseConverter


class OnOffConverter(BaseConverter):
    """
    Converts on/off in routing to True/False (e.g. <on_off:switch>.
    Has to be registered by calling `app.url_map.converters['on_off'] = OnOffConverter`

    Example:

        >>> from collections import namedtuple
        >>> m = namedtuple("m", ['charset'])
        >>> cs = m(charset='utf-8')
        >>> dut = OnOffConverter(cs)
        >>> dut.to_python('on'), dut.to_python('off'), dut.to_python('blub')
        (True, False, False)
        >>> dut.to_url(value=True), dut.to_url(value=False)
        ('on', 'off')
    """

    def to_python(self, value):
        return value.lower() == 'on'

    def to_url(self, value):
        return BaseConverter.to_url(self, value='on' if value else 'off')
