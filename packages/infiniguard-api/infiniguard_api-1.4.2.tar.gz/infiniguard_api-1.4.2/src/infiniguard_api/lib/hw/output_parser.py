import string
import re
import copy
import json

import six
import xmltodict
from collections import OrderedDict
from configobj import ConfigObj
from six.moves import StringIO, configparser
from infiniguard_api.lib.logging import iguard_logging

log = iguard_logging.get_logger(__name__)

def convert_to_nested_config(data):
    def remap(l):
        n = (len(l) - len(l.lstrip())) // 2
        l1 = (l.replace('[', '[' * n).replace(']', ']' * n) if n and '[' in l else copy.copy(l)).strip()
        return l1
    return [remap(line) for line in data.split('\n')]

def parse_config_obj(out):
    config = convert_to_config_obj(out)
    config.pop('total')
    return config

def normalize_config(input):
    newinput = list()
    for dictionary in input:
        newdict = dict()
        for k,v in dictionary.items():
            if str(v).lower() in ['disabled', 'false', 'off', 'no']:
                v = False
            elif str(v).lower() in ['enabled', 'true', 'on', 'yes']:
                v = True
            newdict[k] = v
        newinput.append(newdict)
    return newinput


def parse_config_style_raw(out):
    if isinstance(out, bytes):
        out = out.decode()
    config = configparser.ConfigParser(allow_no_value=True)
    out = '[total]\n' + '\n'.join([a.strip() for a in out.split('\n') if '=' in a])
    buf = StringIO(out)
    config.readfp(buf)
    res = [
        b for (a, b) in
        list({s: {k.lower().replace(' ', '_'): v for k, v in config.items(s)} for s in config.sections()}.items())
    ]
    result = normalize_config(res)
    log.debug('Command Output: {}'.format(result))
    return result


def parse_config_style(out):
    if isinstance(out, bytes):
        out = out.decode()
    config = configparser.ConfigParser(allow_no_value=True)
    out = '[total]\n' + '\n'.join([a.strip() for a in out.split('\n') if '=' in a])
    buf = StringIO(out)
    config.readfp(buf)
    config.remove_section('total')
    res = [
        b for (a, b) in
        list({s: {k.lower().replace(' ', '_'): v for k, v in config.items(s)} for s in config.sections()}.items())
    ]
    result = normalize_config(res)
    log.debug('Command Output: {}'.format(result))
    return result


def parse_list_user(out):
    return parse_config_style(out)


def parse_list_interface_xml(out):
    if isinstance(out, bytes):
        out = out.decode()
    try:
        result = xmltodict.parse(''.join(re.findall(r'^\s*<.*>\n?', out, flags=re.MULTILINE)),
                                 force_list=('DNS_Servers', 'CustomerInterface', 'Interface', 'L3Interface', 'Slave',
                                             'StaticRoute'))
        log.debug('Command Output: {}'.format(json.dumps(result)))
        return result
    except Exception as e:
        log.error(e.message)
        return []

def listify(d):
    """
    Convert a nested dict to an array of dicts that are at the sam level
    Args:
        d:

    Returns:

    """
    listd = OrderedDict()
    for k, v in d.items():
        if not ('=' in k and isinstance(v, dict)):
            listd[k] = v
        else:
            listv = listify(v)
            pre = k.split('=')[0].rstrip(' s') + 's'
            if listd.get(pre):
                listd[pre].append(listv)
            else:
                listd[pre] = [listv]
    return listd

def process_list_interface(data):
    data = data.pop('devices', [])
    rdata = []
    for d in data:
        # if not d.get('interfaces', []):
        #     rd = copy.deepcopy(d)
        #     rd.pop('interfaces', None)
        #     rdata.append(rd)
        #
        for i in d.get('interfaces', []):
            rd = copy.deepcopy(d)
            rd.pop('interfaces', None)
            rd.update(i)
            rdata.append(rd)
    log.debug('Command Result:{}'.format(json.dumps(data)))
    # print('Command Result:\n{}'.format(json.dumps(rdata)))
    return rdata

def process_list_hostmapping(data):
    data = data.pop('groups', [])
    rdata = []
    for d in data:
        devices = d.pop('devices', None)
        if devices:
            vmcs = 0
            vtds = 0
            for i in devices:
                dtype = i.get('type', None)
                if dtype == 'VMC':
                    vmcs += 1
                elif dtype == 'VTD':
                    vtds += 1
            d['devices'] = '{} VMC, {} VTD'.format(vmcs, vtds)
        rdata.append(d)
    log.debug('Command Result:{}'.format(json.dumps(data)))
    # print('Command Result:\n{}'.format(json.dumps(rdata)))
    return rdata

def parse_list_interface(out):
    return parse_list_nested_data(out, process_list_interface)

def parse_list_hostmapping(out):
    return parse_list_nested_data(out, process_list_hostmapping)

def parse_list_nested_data(out, processor):
    def pre(l):
        l1 = ('# ' + l) if '=' not in l or any(x in l for x in ['Total interface count', 'Total count', ]) else l
        return l1

    def post(conf):
        fn = lambda s, k: s.rename(k, k.lower().replace(' = ', '=').translate(str.maketrans(' -', '__')))
        conf.walk(fn, call_on_sections=True)
        result = listify(conf)
        return result
    if isinstance(out, bytes):
        out = out.decode()
    data = convert_to_nested_config(out)
    data = [pre(line) for line in data]
    # log.debug('Command Result:{}'.format(['{}: {}'.format(n+1, line) for n, line in enumerate(data)]))
    buf = StringIO('\n'.join(data))
    config = ConfigObj(buf, write_empty_values=True)
    data = post(config)
    return processor(data)

def parse_single_entry(out):
    if isinstance(out, bytes):
        out = out.decode()
    config = configparser.ConfigParser(allow_no_value=True)
    out = '[objects]\n' + '\n'.join([a.strip() for a in out.split('\n') if '=' in a])
    buf = StringIO(out)
    config.readfp(buf)
    result = [
        b for (a, b) in
        list({s: {k.lower().replace(' ', '_'): v for k, v in config.items(s)} for s in config.sections()}.items())
    ]
    log.debug('Command Output: {}'.format(result))
    return result[0]


def parse_accentstats(out):
    if isinstance(out, bytes):
        out = out.decode()
    config = configparser.ConfigParser(allow_no_value=True)
    out = '\n'.join([re.sub(r"(?i)^.*Accent Statistics:.*$",
                            "[accent_statistics]", a) for a in out.split('\n')])
    out = '\n'.join([re.sub(r"(?i)^.*Optimized Duplication Statistics:.*$",
                            "[optimized_duplication_tatistics]", a) for a in out.split('\n')])
    out = '[basic_statistics]\n' + '\n'.join(
        [a.strip() for a in out.split('\n') if (('=' in a or '[' in a) and 'Total count' not in a)])
    buf = StringIO(out)
    config.readfp(buf)
    result = [{s: {k.lower().replace(' ', '_'): v for k, v in config.items(s)} for s in config.sections()}]
    log.debug('Command Output: {}'.format(result))
    return result


def check_command_successful(out):
    if isinstance(out, bytes):
        out = out.decode()
    match = re.search(r'^.*Command completed successfully.*\n?', out, flags=re.MULTILINE)
    log.debug('Successful: {}, Result Message: {}'.format(match is not None, out))
    return match is not None, out.split('\n')

def parse_async(out):
    if isinstance(out, bytes):
        out = out.decode()
    return out
