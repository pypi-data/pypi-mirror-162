import six
from marshmallow import fields
import ipaddress


# noinspection PyProtectedMember
class IpAddress(fields.String):
    """A string containing one or multiple comma separated ip address(es) in
    dotted decimal form.
    """
    default_error_messages = {
        'invalid': 'Not a valid IP address or comma separated list of IP addresses in dotted decimal notation.',
    }

    def _validate_ip(self, value, **kwargs):
        ips = value.split(',')
        if not len(ips):
            return self.fail('invalid')
        try:
            ipaddress.ip_address(str(ips[0])) if len(ips) == 1 else [ipaddress.ip_address(str(ip)) for ip in ips]
            return value
        except (ValueError, AttributeError):
            return self.fail('invalid')
        except Exception as e:
            raise e

    def _validated(self, value, **kwargs):
        """Format the value or raise a :exc:`ValidationError` if an error occurs."""
        if value is None or not isinstance(value, six.string_types):
            return self.fail('invalid')
        return self._validate_ip(value)

    def _serialize(self, value, attr, obj, **kwargs):
        validated = str(self._validated(value)) if value is not None else None
        return super(IpAddress, self)._serialize(validated, attr, obj)

    def _deserialize(self, value, attr, data, **kwargs):
        return self._validated(value)


# noinspection PyProtectedMember
class Netmask(IpAddress):
    """A netmask field."""
    default_error_messages = {
        'invalid': 'Not a valid network mask in dotted decimal notation.',
    }

    def _validate_ip(self, mask, **kwargs):
        try:
            ipaddress.IPv4Address._prefix_from_ip_string(str(mask))
            return mask
        except (ValueError, AttributeError):
            return self.fail('invalid')
