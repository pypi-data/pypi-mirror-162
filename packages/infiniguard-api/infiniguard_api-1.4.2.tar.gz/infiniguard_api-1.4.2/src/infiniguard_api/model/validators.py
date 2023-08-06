import re

from marshmallow import ValidationError


def validate_devname(devname):
    """Function to validate a device name.

    :param devname: Device name alphanumeric string
    :raise ValidationError: if the input is not a valid device name
    """
    valid_devname = r'^([a-z0-9]+)\Z'
    if re.match(valid_devname, devname) is None:
        raise ValidationError("Device name is not alphanumeric (you maybe passing an interface)")
    return devname


def validate_intfname(intfname, only_intf=False):
    """Function to validate a device name.

    :param intfname: Device name. The general format is <label>[.<vlanid>]:<vifno> where
        label:  alphanumeric string
        vlanid: VLAN ID is an optional field and can range from 2 to 4094.
        vifno:  virtual interface number, which is used to distinguish each set of
            network layer (L3) values, i.e. IP address and netmask values.
            It can range from 1 to possibly 99, depending on actual systems.
    :raise ValidationError: if the input is not a valid device name
    """
    if not intfname:
        raise ValidationError('no interface name or device name specified')

    if intfname.count(':') > 1:
        raise ValidationError("only one interface number can be provided")
    if intfname.count('.') > 1:
        raise ValidationError("only one vlanid can be provided")

    parts = intfname.split(':')
    devname_vlanid = parts[0]
    numparts = len(parts)
    if only_intf and numparts != 2:
        raise ValidationError("full interface name is required <devname>[.<vlandid>]:<intf_num>")

    intfnum = parts[1] if numparts == 2 else None
    if intfnum and not 1 <= int(intfnum) <= 99:
        raise ValidationError("interface number must be from 1 to 99, if provided, not {}".format(intfnum))

    parts = devname_vlanid.split('.')
    devname = parts[0]
    validate_devname(devname)

    vlanid = parts[1] if len(parts) == 2 else None
    if vlanid and not 2 <= int(vlanid) <= 4094:
        raise ValidationError("vlanid must be from 2 to 4094, if provided, not {}".format(vlanid))

    return intfname


def validate_slaves(slave_names):
    """

    :param slave_names: verify that there is a comma separated string of at least two slave devnames
    :return: slave_names
    """
    if len(slave_names) < 2:
        raise ValidationError('There must be 2 or more slaves specified')
    for s in slave_names:
        if re.match(r'[a-z0-9]+', s) is None:
            raise ValidationError('Slaves must be alphanumeric strings')
    return slave_names
