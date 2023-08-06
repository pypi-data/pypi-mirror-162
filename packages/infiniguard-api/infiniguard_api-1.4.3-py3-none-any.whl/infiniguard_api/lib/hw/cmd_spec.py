# pragma: no cover
from schematics.exceptions import DataError
allowed_concurrentopdup_options = 'disabled,enabled'
allowed_traffic_options = 'REP,MGMT,DATA,ALL'
bond_mode_options = 'RR,AB,LACP'
allowed_encryption_types = '128,256'
yn_options = 'YES,NO'

resource_cmd_spec_dict = {
    'user':
    {
        'syscli_resource': 'backupuser',
        'get':
        {
            'description': 'Get a backup application user',
            'syscli_command': '--list',
            'syscli_options':
                [
                ],
            'post_processing': True,
            'post_processor': 'get_single_item',
            'post_options':
                [
                    dict(name='--name', type=str, required=True, help='backup user name'),
                ]
        },
        'put':
        {
            'description': 'Edit a backup application user',
            'syscli_command':'--edit',
            'syscli_options':
                [
                    dict(name='--name', type=str, required=True),
                    dict(name='--password', type=str, required=True),
                    dict(name='--description', replace_with='--desc', type=str),
                ]
        },
        'delete':
        {
            'description': 'Delete a Backup Application User',
            'syscli_command':'--del',
            'syscli_options':
                [
                    dict(name='--name', type=str, required=True)
                ]
         },
    },
    'users':
    {
        'syscli_resource':'backupuser',
        'post':
        {
            'description': 'Add a backup application user',
            'syscli_command': '--add',
            'syscli_options':
                [
                    dict(name='--name', type=str, required=True),
                    dict(name='--password', type=str, required=True),
                    dict(name='--description', replace_with='--desc', type=str),
                ]
        },
        'get':
        {
            'description': 'List all backup application users defined in the system',
            'syscli_command': '--list',
            'syscli_options':
                [
                ]
        }
    },
    'ost/storageserver':
    {
        'syscli_resource':'storageserver',
        'put':
        {
            'description': 'Edit one or more attributes of an existing storage server',
            'syscli_command':'--edit',
            'syscli_options':
                [
                    dict(name='--name', type=str, required=True),
                    dict(name='--maxconnect', type=int),
                    dict(name='--target', type=str),
                    dict(name='--concurrentopdup', type=str, choices=allowed_concurrentopdup_options.split(',')),
                    dict(name='--description', replace_with='--desc', type=str),
                ]
        },
        'delete':
        {
            'description': 'Delete the specified OST storage server',
            'syscli_command':'--del',
            'syscli_options':
                [
                    dict(name='--name', type=str, required=True)
                ]
         },
        'get':
        {
            'description': 'Get an OST storage server and its associated attributes',
            'syscli_command': '--list',
            'syscli_options':
                [
                    dict(name='--name', type=str),
                ]
        }
    },
    'ost/storageservers':
    {
        'syscli_resource':'storageserver',
        'post':
        {
            'description': 'Add an OST storage server',
            'syscli_command': '--add',
            'syscli_options':
                [
                    dict(name='--name', type=str, required=True),
                    dict(name='--maxconnect', type=int, required=True),
                    dict(name='--target', type=str),
                    dict(name='--concurrentopdup', type=str, choices=allowed_concurrentopdup_options.split(',')),
                    dict(name='--description', replace_with='--desc', type=str),
                ]
        },
        'get':
        {
            'description': 'List existing OST storage servers and their associated attributes',
            'syscli_command': '--list',
            'syscli_options':
                [
                    dict(name='--name', type=str),
                    dict(name='--namematch', type=str),
                ]
        }
    },
    'ost/lsu':
    {
        'syscli_resource':'lsu',
        'put':
        {
            'description': 'Edit an LSU of the specified storage server',
            'syscli_command':'--edit',
            'syscli_options':
                [
                    dict(name='--name', type=str, required=True),
                    dict(name='--storageserver', type=str, required=True),
                    dict(name='--description', replace_with='--desc', type=str),
                    dict(name='--capacity', type=int, help='the capacity of the LSU in GB'),
                ]
        },
        'delete':
        {
            'description': 'Delete an LSU from a specified storage server',
            'syscli_command':'--del',
            'syscli_options':
                [
                    dict(name='--name', type=str, required=True),
                    dict(name='--storageserver', type=str, required=True),
                    dict(name='--force', action='store_true', default=False, help='If specified, the LSU is deleted even if it contains files or backup images')
                ]
         },
    },
    'ost/lsus':
    {
        'syscli_resource':'lsu',
        'post':
        {
            'description': 'Add an LSU to a specified storage server',
            'syscli_command': '--add',
            'syscli_options':
                [
                    dict(name='--name', type=str, required=True),
                    dict(name='--maxconnect', type=int, required=True),
                    dict(name='--target', type=str),
                    dict(name='--concurrentopdup', type=str, choices=allowed_concurrentopdup_options.split(',')),
                    dict(name='--description', replace_with='--desc', type=str),
                ]
        },
        'get':
        {
            'description': 'List LSUs attached to a storage server',
            'syscli_command': '--list',
            'syscli_options':
                [
                    dict(name='--storageserver', type=str, required=True),
                    dict(name='--name', type=str),
                ]
        }
    },
    'ost/certificate':
    {
        'syscli_resource':'tlscertificate',
        'post':
        {
            'description': 'Install user-provided TLS certificate files',
            'syscli_command': '--install',
            'syscli_options':
                [
                    dict(name='--certificate', type=str),
                    dict(name='--privatekey', type=str),
                    dict(name='--certificateauthority', type=str),
                    dict(name='--rejectionlist', type=str),
                ]
        },
        'delete':
        {
            'description': 'Restore the TLS certificates to factory default certificates',
            'syscli_command':'--restore',
            'syscli_options':
                [
                ]
        },
        'get':
        {
            'description': 'Access the current status of your system TLS certificate files',
            'syscli_command': '--getstatus',
            'syscli_options':
                [
                ]
        }
    },
    'ost/airuser':
    {
        'syscli_resource': 'airuser',
        'get':
        {
            'description': 'Get a backup application user',
            'syscli_command': '--get',
            'syscli_options':
                [
                    dict(name='--username', type=str, required=True),
                ],
            'post_processing': True,
            'post_processor': 'get_single_user',
        },
        'put':
        {
            'description': 'Edit a user on the AIR server',
            'syscli_command':'--edit',
            'syscli_options':
                [
                    dict(name='--username', type=str, required=True),
                    dict(name='--password', type=str, required=True),
                    dict(name='--description', replace_with='--desc', type=str),
                ]
        },
        'delete':
        {
            'description': 'Delete the specified user from the AIR server',
            'syscli_command':'--del',
            'syscli_options':
                [
                    dict(name='--username', type=str, required=True)
                ]
         },
    },
    'ost/airusers':
    {
        'syscli_resource':'airuser',
        'post':
        {
            'description': 'Add a user who can manage replication tasks on the AIR server',
            'syscli_command': '--add',
            'syscli_options':
                [
                    dict(name='--username', type=str, required=True),
                    dict(name='--password', type=str, required=True),
                    dict(name='--description', replace_with='--desc', type=str),
                ]
        },
        'get':
        {
            'description': 'List all users defined for the AIR server',
            'syscli_command': '--list',
            'syscli_options':
                [
                ]
        }
    },
    'ost/ostair':
    {
        'syscli_resource': 'ostair',
        'post':
        {
            'description': 'Set up the initial relationship that directs a storage server logical storage unit (LSU) to replicate to a target storage servers LSU for AIR',
            'syscli_command': '--add',
            'syscli_options':
                [
                    dict(name='--sourcess', type=str, required=True),
                    dict(name='--airuser', type=str, required=True),
                    dict(name='--sourcelsu', type=str),
                    dict(name='--targetss', type=str),
                    dict(name='--target', type=str),
                    dict(name='--targetlsu', type=str),
                ]
        },
        'put':
        {
            'description': 'Edit the relationship that directs a storage servers LSU to replicate to a target storage servers LSU for AIR',
            'syscli_command':'--edit',
            'syscli_options':
                [
                    dict(name='--sourcess', type=str, required=True),
                    dict(name='--airuser', type=str),
                    dict(name='--sourcelsu', type=str),
                    dict(name='--targetss', type=str),
                    dict(name='--target', type=str),
                    dict(name='--targetlsu', type=str),
                ]
        },
        'delete':
        {
            'description': 'Delete a target AIR storage server from a specified source storage server and LSU',
            'syscli_command':'--del',
            'syscli_options':
                [
                    dict(name='--sourcess', type=str, required=True),
                    dict(name='--sourcelsu', type=str),
                ]
         },
    },
    'replication/source':
    {
        'syscli_resource':'sourcerep',
        'delete':
        {
            'description': 'Delete a source from which the system is allowed to receive replicated data',
            'syscli_command':'--del',
            'syscli_options':
                [
                    dict(name='--hostid', type=str, required=True, help='source ip address or hostname'),
                ]
         },
        'get':
        {
            'description': 'List of all allowed replication source IP for this system as a target',
            'syscli_command': '--list',
            'syscli_options':
                [
                ],
            'post_processing': True,
            'post_processor': 'get_single_item',
            'post_options':
                [
                    dict(name='--hostid', type=str, required=True, help='source ip address or hostname'),
                ]
        }
    },
    'replication/sources':
    {
        'syscli_resource':'sourcerep',
        'post':
        {
            'description': 'Add a source from which the system can receive replicated data',
            'syscli_command': '--add',
            'syscli_options':
                [
                    dict(name='--hostid', type=str, required=True, help='source ip address or hostname'),
                ]
        },
        'get':
        {
            'description': 'List of all allowed replication source IP for this system as a target',
            'syscli_command': '--list',
            'syscli_options':
                [
                ],
        }
    },
    'replication/target':
    {
        'syscli_resource':'targetrep',
        'delete':
        {
            'description': 'Delete a target to which the system can send replicated data',
            'syscli_command':'--del',
            'syscli_options':
                [
                    dict(name='--hostid', type=str, required=True, help='target ip address or hostname'),
                ]
         },
        'get':
        {
            'description': 'List of all allowed replication source IP for this system as a target',
            'syscli_command': '--list',
            'syscli_options':
                [
                ],
            'post_processing': True,
            'post_processor': 'get_single_item',
            'post_options':
                [
                    dict(name='--hostid', type=str, required=True, help='target ip address or hostname'),
                ]
        }
    },
    'replication/targets':
    {
        'syscli_resource':'targetrep',
        'post':
        {
            'description': 'Add a target to which the system can send replicated data',
            'syscli_command': '--add',
            'syscli_options':
                [
                    dict(name='--hostid', type=str, required=True, help='target ip address or hostname'),
                    dict(name='--encrypt', type=str, help='Specify to encrypt data before replicating it and sending it to the target'),
                    dict(name='--encrypttype', type=str, choices=allowed_encryption_types.split(',')),
                ]
        },
        'get':
        {
            'description': 'List target IP addresses or hostnames to which the system can send replicated data',
            'syscli_command': '--list',
            'syscli_options':
                [
                ]
        }
    },
    'netcfg':
    {
        'syscli_resource': 'netcfg',
        'post':
        {
            'description': 'Add a target to which the system can send replicated data.',
            'syscli_command': '--add',
            'syscli_options':
                [
                    dict(name='--devname', type=str, required=True,
                         help='Name of device. Format: <label(alpha)><devno(0-99)>[.<vlanid(2-4094)>]:<vifno(0-99)>.'),
                    dict(name='--dhcp', action='store_true', default=False, required=False,
                         help='Use DHCP for network device configuration of Ipaddr, netmask, and gateway.'),
                    dict(name='--ipaddr', type=str, required=False, help='IP address in decimal dotted notation, if no dhcp.'),
                    dict(name='--netmask', type=str, required=False, help='Netmask in decimal dotted notation, if no dhcp.'),
                    dict(name='--gateway', type=str, required=False, help='IP address of gateway, if no dhcp.'),
                    dict(name='--slaves', type=str, required=False,
                         help='Specify two or more slave device names separated by commas.'),
                    dict(name='--mode', type=str, required=False, choices=bond_mode_options.split(','),
                         help='Mode must be specified when creating a bond (Round Robin(0),Active Backup(1),LACP(4)).'),
                    dict(name='--mtu', type=str, required=False, default=1500,
                         help='MTU size in bytes. Range: 68 - 9192, inclusive.'),
                    dict(name='--defaultgw', type=str, required=False, default='NO', choices=yn_options.split(','),
                         help='Set the default gateway.'),
                    dict(name='--segments', type=str, required=False, default="ALL",
                         choices=allowed_traffic_options.split(','),
                         help='Only allow the specified traffic types on this interface.'),
                    dict(name='--nat', type=str, required=False,
                         help='Specified on the target if the source needs to use this NAT IP address for replication.'),
                    dict(name='--hosts', type=str, required=False,
                         help='Only allow communication with these hosts via the specified gateway.'),
                    dict(name='--extHostIp', type=str, required=False, default='NO', choices=yn_options.split(','),
                         help='Uses the entered external host ip value above as the default external host ip.'),
                    dict(name='--sure', action='store_true', default=False, required=False,
                         help='If specified, the command will execute without asking for confirmation.'),
                ]
        },
        'get':
        {
            'description': 'Shows the IP address and routing information configuration for all or specified device.',
            'syscli_command': '--show',
            'syscli_options':
                [
                    dict(name='--devname', type=str, required=False, help='Name of device'),
                ]
        }
    },
}

def create_syscli_command(resource, operation, request_object):
    res_spec = resource_cmd_spec_dict.get(resource, None)
    if res_spec == None:
        raise DataError('resource_cmd_spec invalid resource {}'.format(resource))
    syscli_resource = res_spec.get('syscli_resource', None)
    if syscli_resource == None:
        raise DataError('resource_cmd_spec resource {} missing syscli_resource'.format(resource))
    cmd_spec = res_spec.get(operation, None)
    if cmd_spec == None:
        raise DataError('resource_cmd_spec invalid operation {}'.format(operation))
    syscli_command = cmd_spec.get('syscli_command', None)
    if syscli_command == None:
        raise DataError('resource_cmd_spec resource {} operation {} missing syscli_command'.format(resource, operation))
    components = ['/opt/DXi/syscli']
    components.extend([syscli_command, syscli_resource])
    syscli_options = cmd_spec.get('syscli_options', None)
    for option in syscli_options:
        attr_name = option['name'][2:]
        if hasattr(request_object, attr_name):
            option_key = option['replace_with'] if option.get('replace_with', None) != None else option['name']
            components.extend([option_key, request_object.get(attr_name)])
    return components
