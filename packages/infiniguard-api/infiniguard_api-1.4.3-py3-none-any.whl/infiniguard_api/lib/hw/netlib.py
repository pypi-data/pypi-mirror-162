from icmplib.ip import IPSocket
from icmplib.ping import (ICMPv4Socket,
                          ICMPv6Socket,
                          ICMPRequest,
                          ICMPError,
                          ICMPLibError,
                          TimeExceeded,
                          TimeoutExceeded
                          )
from icmplib.utils import is_ipv6_address
import wrapt
from time import sleep
from socket import IPPROTO_IP, getfqdn, gethostbyname
from random import randint
from types import SimpleNamespace
import dns
import dns.reversename
import dns.resolver
import sys
import socket
import fcntl
import struct
import array
from enum import Enum

STDOUT = 1
STDERR = 2

'''
# uapi/ linux/ethtool.h
struct ethtool_cmd {
    __u32   cmd; 4
    __u32   supported; 8
    __u32   advertising; 12
    __u16   speed; 14
    __u8    duplex; 15
    __u8    port; 16
    __u8    phy_address; 17
    __u8    transceiver; 18
    __u8    autoneg; 19
    __u8    mdio_support; 20
    __u32   maxtxpkt; 24
    __u32   maxrxpkt; 28
    __u16   speed_hi; 30
    __u8    eth_tp_mdix; 31
    __u8    eth_tp_mdix_ctrl; 32
    __u32   lp_advertising; 36
    __u32   reserved[2]; 38
};
'''
# linux/sockios.h
SIOCETHTOOL = 0x8946

# uapi/linux/ethtool.h
ETHTOOL_GSET = 0x00000001  # Get settings


class MyEnum(Enum):
    def __str__(self):
        return '%s' % " ".join(self.name.split("_")[1:])

    def __int__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other

    def __rand__(self, other):
        return self.value & other

    @classmethod
    def find_one(cls, candidate):
        members = cls._member_names_
        for member in members:
            if candidate == cls[member]:
                return str(cls[member])

    @classmethod
    def find_all(cls, candidate):
        res = list()
        members = cls._member_names_
        for member in members:
            if candidate & cls[member]:
                res.append(str(cls[member]))
        return res


class NetworkPort(MyEnum):
    PORT_TP = 0x00
    PORT_AUI = 0x01
    PORT_MII = 0x02
    PORT_FIBRE = 0x03
    PORT_BNC = 0x04
    PORT_DA = 0x05
    PORT_NONE = 0xef
    PORT_OTHER = 0xff


class NetworkDuplex(MyEnum):
    DUPLEX_Half = 0x00
    DUPLEX_Full = 0x01


class NetworkAutonegotiation(MyEnum):
    AUTONEG_off = 0x00
    AUTONEG_on = 0x01


class NetworkSpeed(MyEnum):
    SPEED_10baseT_Half = (1 << 0)
    SPEED_10baseT_Full = (1 << 1)
    SPEED_100baseT_Half = (1 << 2)
    SPEED_100baseT_Full = (1 << 3)
    SPEED_1000baseT_Half = (1 << 4)
    SPEED_1000baseT_Full = (1 << 5)
    SPEED_10000baseT_Full = (1 << 12)
    SPEED_2500baseX_Full = (1 << 15)
    SPEED_1000baseKX_Full = (1 << 17)
    SPEED_10000baseKX4_Full = (1 << 18)
    SPEED_10000baseKR_Full = (1 << 19)
    SPEED_10000baseR_FEC = (1 << 20)
    SPEED_20000baseMLD2_Full = (1 << 21)
    SPEED_20000baseKR2_Full = (1 << 22)
    SPEED_40000baseKR4_Full = (1 << 23)
    SPEED_40000baseCR4_Full = (1 << 24)
    SPEED_40000baseSR4_Full = (1 << 25)
    SPEED_40000baseLR4_Full = (1 << 26)
    SPEED_56000baseKR4_Full = (1 << 27)
    SPEED_56000baseCR4_Full = (1 << 28)
    SPEED_56000baseSR4_Full = (1 << 29)
    SPEED_56000baseLR4_Full = (1 << 30)


def get_interface_ethtool(name):

    cmd = array.array('B', struct.pack('I38s', ETHTOOL_GSET, b'\x00'*38))
    ifreq = struct.pack('16sP', name.encode(), cmd.buffer_info()[0])
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sockfd = sock.fileno()
            fcntl.ioctl(sockfd, SIOCETHTOOL, ifreq)
        res = cmd.tobytes()
        supported, advertising, speed, duplex_bit, port_bit, auto = struct.unpack(
            '4xIIHBB2xB23x', res)
    except IOError:
        raise

    port = NetworkPort.find_one(port_bit)
    duplex = NetworkDuplex.find_one(duplex_bit)
    supported_modes = NetworkSpeed.find_all(supported)
    autoneg = NetworkAutonegotiation.find_one(auto)
    if speed == 65535:
        speed = 0

    return speed, duplex, autoneg, port, supported_modes


class MyAnswer(dns.resolver.Answer):
    def __init__(self, qname, rdtype, rdclass, response,
                 raise_on_no_answer=True, nameserver=None, port=None):
        super().__init__(qname, rdtype, rdclass, response,
                         raise_on_no_answer)
        self.nameserver = nameserver
        self.port = port


class MyResolver(dns.resolver.Resolver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = None
        self._nameserver = None

    def resolve(self, qname, rdtype=dns.rdatatype.A, rdclass=dns.rdataclass.IN,
                tcp=False, source=None, raise_on_no_answer=True, source_port=0,
                lifetime=None):
        def tracer(frame, event, arg):
            if event == 'return':
                if frame.f_locals.get('nameserver', None):
                    self._nameserver = frame.f_locals['nameserver']
                if frame.f_locals.get('port', None):
                    self._port = frame.f_locals['port']

        sys.setprofile(tracer)
        res = self.query(qname, rdtype, rdclass,
                         tcp, source, raise_on_no_answer, source_port,
                         lifetime)
        sys.setprofile(None)

        res.nameserver = self._nameserver
        res.port = self._port
        return res


dns.resolver.Answer = MyAnswer
dns.resolver.Resolver = MyResolver


class MyICMPv4Socket(ICMPv4Socket):
    def set_dnf(self):
        pass

    def bind(self, args, kwargs):
        pass


ICMPv4Socket = MyICMPv4Socket


@wrapt.patch_function_wrapper(IPSocket, 'receive')
def _receive(wrapped, instance, args, kwargs):
    result = instance._socket.recvfrom(65536)

    packet = result[0]
    address = result[1][0]
    port = result[1][1]

    return packet, address, port


@wrapt.patch_function_wrapper(ICMPv4Socket, 'bind')
def _bind(wrapped, instance, args, kwargs):
    socket = instance._socket._socket
    socket.bind((args[0], 0))


@wrapt.patch_function_wrapper(ICMPv4Socket, 'set_dnf')
def _set_dnf(wrapped, instance, args, kwargs):
    IP_MTU_DISCOVER = 10
    IP_PMTUDISC_DONT = 0  # Never send DF frames.
    IP_PMTUDISC_WANT = 1  # Use per route hints.
    IP_PMTUDISC_DO = 2  # Always DF.
    IP_PMTUDISC_PROBE = 3  # Ignore dst pmtu.
    socket = instance._socket._socket
    socket.setsockopt(IPPROTO_IP, IP_MTU_DISCOVER, IP_PMTUDISC_DO)


def do_resolv():
    resolver = MyResolver(configure=True)
    search_domain = [a.to_text() for a in resolver.search]
    nameservers = resolver.nameservers
    return nameservers, search_domain


def do_dig(*args):
    lookup = {
        'question': ';; QUESTION SECTION:',
        'answer': ';; ANSWER SECTION:',
        'authority': ';; AUTHORITY SECTION:',
        'additional': ';; ADDITIONAL SECTION:',
        'server': ';; SERVER: {ns}#{port}({ns})'
    }
    defaults = {
        'dst': None,
        'time': 3,
    }
    parms = dict()
    for key in defaults.keys():
        parms[key] = args[0].get(key, defaults[key])
    parms = SimpleNamespace(**parms)
    try:
        resolver = MyResolver(configure=True)
        # Move to next nameserver after 1 seconds if no response
        resolver.timeout = 1
        # Fail after <time> seconds if no nameservers answer
        resolver.lifetime = parms.time
        try:
            addr = dns.reversename.from_address(parms.dst)
            q = 'PTR'
        except Exception as e:
            addr = parms.dst
            q = 'A'

        answer = resolver.resolve(addr, q)

        yield(lookup['question'], STDOUT)
        yield(f';{answer.response.question[0].to_text()}', STDOUT)
        yield('', STDOUT)

        for a in ['answer', 'authority', 'additional']:
            items = getattr(answer.response, a)
            yield(lookup[a], STDOUT)
            for item in items:
                yield(item.to_text(), STDOUT)
            yield('', STDOUT)
        yield(lookup['server'].format(ns=answer.nameserver, port=answer.port), STDOUT)
    except Exception as e:
        yield(str(e), STDERR)


def do_ping(*args):
    defaults = {
        'dst': None,
        'time': 5,
        'interval': 1,
        'timeout': 1,
        'payload_size': 56,
        'do_not_fragment': False,
        'src': None
    }
    parms = dict()
    for key in defaults.keys():
        parms[key] = args[0].get(key, defaults[key])
    parms = SimpleNamespace(**parms)
    # Payload should always be multiple of 2
    parms.payload_size = parms.payload_size // 2 * 2

    source_addr = f'from {parms.src}' if parms.src else ''
    yield(f'PING {parms.dst} {source_addr}: {parms.payload_size}({parms.payload_size + 28}) data bytes', STDOUT)

    # Automatic detection of the socket to use
    try:
        if is_ipv6_address(parms.dst):
            socket = ICMPv6Socket()

        else:
            socket = ICMPv4Socket()

        if parms.do_not_fragment:
            socket.set_dnf()

        if parms.src:
            socket.bind(parms.src)

        ping_id = randint(1024, 65535)
    except Exception as e:
        yield(str(e), STDERR)
        return
    for sequence in range(1, parms.time + 1):
        request = ICMPRequest(
            destination=parms.dst,
            id=ping_id,
            sequence=sequence,
            timeout=1,
            payload_size=parms.payload_size)
        try:
            socket.send(request)
            reply = socket.receive()
            line = (f'{reply.received_bytes} bytes from {reply.source}: ')
            reply.raise_for_status()
            round_trip_time = (reply.time - request.time) * 1000
            yield(f'{line} icmp_seq={sequence} '
                  f'time={round(round_trip_time, 2):.2f} ms', STDOUT)

            if sequence < parms.time - 1:
                sleep(1)

        except TimeoutExceeded:
            yield(f'From {request.destination} icmp_seq={sequence} Request timeout', STDOUT)

        except ICMPError as err:
            strerr = str(err)
            yield(f'From {request.destination} icmp_seq={sequence} {strerr}', STDOUT)

        except ICMPLibError as e:
            strerr = str(e.message)
            yield(f'From {request.destination} icmp_seq={sequence} {strerr}', STDERR)
            break


def do_traceroute(*args):
    defaults = {
        'dst': None,
        'src': None,
        'max_hops': 30,
        'count': 3,
        'interval': 0.05,
        'timeout': 2,
        'no_resolve': False
    }
    parms = dict()
    for key in defaults.keys():
        parms[key] = args[0].get(key, defaults[key])
    parms = SimpleNamespace(**parms)
    try:
        yield(f'Traceroute to {parms.dst} ({gethostbyname(parms.dst)}): '
              f'56 data bytes, {parms.max_hops} hops max', STDOUT)
    except Exception as e:
        yield(f'Error: {e}', STDERR)
        return
    # Automatic detection of the socket to use
    try:
        if is_ipv6_address(parms.dst):
            socket = ICMPv6Socket()

        else:
            socket = ICMPv4Socket()

        if parms.src:
            socket.bind(parms.src)

        ping_id = randint(1024, 65535)
    except Exception as e:
        yield(str(e), STDERR)
        return
    ttl = 1
    host_reached = False
    line = 'Timeout'

    while not host_reached and ttl <= parms.max_hops:
        for sequence in range(parms.count):
            # We create an ICMP request
            request = ICMPRequest(
                destination=parms.dst,
                id=ping_id,
                sequence=sequence,
                timeout=parms.timeout,
                ttl=ttl)

            try:
                # We send the request
                socket.send(request)

                # We are awaiting receipt of an ICMP reply
                reply = socket.receive()

                # We received a reply
                # We display some information
                if parms.no_resolve:
                    source_name = reply.source
                else:
                    source_name = getfqdn(reply.source)

                line = (f'{ttl:3}    {reply.source:15}    {source_name:40}    ')
                # We throw an exception if it is an ICMP error message
                reply.raise_for_status()

                # We reached the destination host
                # We calculate the round-trip time and we display it
                round_trip_time = round(
                    (reply.time - request.time) * 1000, STDERR)
                yield(f'{line} {round_trip_time} ms', STDOUT)

                # We can stop the search
                host_reached = True
                break

            except TimeExceeded as err:
                # An ICMP Time Exceeded message has been received
                # The message was probably generated by an intermediate
                # gateway
                reply = err.reply

                # We calculate the round-trip time and we display it
                round_trip_time = round(
                    (reply.time - request.time) * 1000, STDERR)
                yield(f'{line} {round_trip_time} ms', STDOUT)

                sleep(parms.interval)
                break

            except TimeoutExceeded:
                # The timeout has been reached and no host or gateway
                # has responded after multiple attemps
                if sequence >= parms.count - 1:
                    yield(f'{ttl:3}    * * *', STDOUT)

            except ICMPLibError as e:
                if sequence == parms.count - 1:
                    strerr = str(e)
                    yield(f'{ttl:3} {strerr}', STDERR)
                    return

        ttl += 1


def do_mtu(*args):
    defaults = {
        'dst': None,
        'src': None
    }
    parms = dict()
    for key in defaults.keys():
        parms[key] = args[0].get(key, defaults[key])
    parms = SimpleNamespace(**parms)

    # Automatic detection of the socket to use
    try:
        if is_ipv6_address(parms.dst):
            socket = ICMPv6Socket()

        else:
            socket = ICMPv4Socket()

        socket.set_dnf()

        if parms.src:
            socket.bind(parms.src)

        ping_id = randint(1024, 65535)
    except Exception as e:
        yield(str(e), STDERR)
        return

    try:
        request = ICMPRequest(
            destination=parms.dst,
            id=ping_id,
            sequence=1,
            timeout=1,
            payload_size=56)

        socket.send(request)
        reply = socket.receive()
        reply.raise_for_status()

    except TimeoutExceeded:
        yield(f'Host {parms.dst} is unreachable!', STDERR)
        return

    except ICMPError as err:
        strerr = str(err)
        yield(f'ICMPError: {strerr}', STDERR)
        return

    except ICMPLibError as e:
        yield(f'ICMPLibError {e}', STDERR)
        return

    min_size = 0
    max_size = 9000
    now_size = (min_size + max_size) // 4 * 2
    while max_size - min_size > 2:
        # Payload should always be even
        now_size = (min_size + max_size) // 4 * 2
        try:
            request = ICMPRequest(
                destination=parms.dst,
                id=ping_id,
                sequence=1,
                timeout=1,
                payload_size=now_size)

            socket.send(request)
            reply = socket.receive()
            reply.raise_for_status()
            min_size = now_size

        except ICMPLibError as e:
            max_size = now_size

    # Add header overhead
    yield min_size + 28, 1
