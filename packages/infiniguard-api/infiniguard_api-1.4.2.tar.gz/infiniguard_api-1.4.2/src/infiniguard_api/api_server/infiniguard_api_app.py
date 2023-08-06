import os
import re
import apispec
from flask import Flask
from apispec.ext.marshmallow import MarshmallowPlugin, BasePlugin
from apispec.ext.marshmallow.common import resolve_schema_cls

from iba_install.core.ibox import get_ibox

from infiniguard_api.api_server.config import DevelopmentConfig
from flask_apispec import FlaskApiSpec

from infiniguard_api.view.node_api import node_api, RebootResource
from infiniguard_api.common import messages
from infiniguard_api.lib.rest.common import handle_error, handle_error_malformed,\
    build_error_model, build_error_message, build_paginated_response
from infiniguard_api.lib.hw.threads import start_worker
from infiniguard_api.lib.hw.tasks import vacuum, get_session, delete_running_tasks


from infiniguard_api.view.network.common import network_api
from infiniguard_api.view.network.device_api import DeviceResource, DevicesResource
from infiniguard_api.view.network.host_api import HostResource
from infiniguard_api.view.network.interface_api import InterfaceResource, InterfacesResource
from infiniguard_api.view.network.bond_api import BondsResource, BondResource
from infiniguard_api.view.network.netcfg_api import (NetcfgResource)
from infiniguard_api.view.network.static_routes_api import (StaticRouteResource,
                                                            StaticRoutesResource,
                                                            StaticRouteResourceDevname,
                                                            StaticRoutesResourceDevname
                                                            )
from infiniguard_api.view.network.network_misc_api import NetworkBackupResource, NetworkRestoreResource
from infiniguard_api.view.network.tools_api import (PingResource,
                                                    MtuResource,
                                                    DigResource,
                                                    ResolvResource,
                                                    TracerouteResource,
                                                    IperfResource,
                                                    InterfacesDetailsResource,
                                                    network_tools_api
                                                    )
from infiniguard_api.view.ost import ost_api
from infiniguard_api.view.ost.accentstats_api import (OstaccentstatsResource)
from infiniguard_api.view.ost.lsu_api import (LsuResource, LsusResource)
from infiniguard_api.view.ost.ostair_api import (OstairResource)
from infiniguard_api.view.ost.ostsetting_api import (OstsettingResource)
from infiniguard_api.view.ost.storageserver_api import (
    StorageserverResource, StorageserversResource)
from infiniguard_api.view.ost.tlscertificate_api import (
    TlscertificateResource)
from infiniguard_api.view.replication.ostmapping_api import (
    OstMappingResource, OstMappingsResource)
from infiniguard_api.view.replication.sourcerep_api import (
    SourcerepResource, SourcerepsResource, replication_api)
from infiniguard_api.view.replication.targetrep_api import (
    TargetrepResource, TargetrepsResource)

from infiniguard_api.view.nas import nas_api
from infiniguard_api.view.nas.share_api import (ShareResource, SharesResource)
from infiniguard_api.view.nas.nfs_share_api import (
    NfsShareResource, NfsSharesResource)
from infiniguard_api.view.nas.sharehost_api import (
    NfsShareHostResource, NfsShareHostsResource)
from infiniguard_api.view.nas.nfssetting_api import (NfsNfssettingResource)
from infiniguard_api.view.nas.cifs_share_api import (
    CifsShareResource, CifsSharesResource)
from infiniguard_api.view.nas.shareuser_api import (
    CifsShareUserResource, CifsShareUsersResource)
from infiniguard_api.view.nas.app_specific_share_api import (
    AppSpecificShareResource, AppSpecificSharesResource, AppSpecificShareFilesResource)
from infiniguard_api.view.nas.workgroup_api import (CifsWorkgroupsResource)
from infiniguard_api.view.nas.adsdomain_api import (CifsAdsDomainsResource)
from infiniguard_api.view.nas.shareadmin_api import (
    CifsShareAdminResource, CifsShareAdminsResource)
from infiniguard_api.view.nas.smbsetting_api import (CifsSmbsettingResource)

from infiniguard_api.view.vtl import vtl_api
from infiniguard_api.view.vtl.partition_api import (PartitionResource, PartitionsResource, PartitionsOnlineResource, PartitionsOfflineResource,
                                                    PartitionOnlineResource, PartitionOfflineResource, PartitionDevicesResource,
                                                    PartitionSourceStorageLocationsResource, PartitionDestStorageLocationsResource)
from infiniguard_api.view.vtl.media_api import (MediaResource, MediaImportResource, MediaExportResource, MediaWriteProtectEnableResource,
                                                MediaWriteProtectDisableResource, MediaRecycleResource, MediaUnloadResource)
from infiniguard_api.view.vtl.media_api import (MediasResource, MediasImportResource, MediasExportResource, MediasWriteProtectEnableResource,
                                                MediasWriteProtectDisableResource, MediasRecycleResource, MediasMoveResource)
from infiniguard_api.view.vtl.host_api import (
    VtlHostResource, VtlHostsResource)
from infiniguard_api.view.vtl.host_mapping_api import (
    VtlHostmappingResource, VtlHostmappingsResource)
from infiniguard_api.view.vtl.library_api import (VtlLibrariesResource)
from infiniguard_api.view.vtl.target_api import (VtlTargetsResource)
from infiniguard_api.view.vtl.drive_api import (
    VtlDrivesResource, VtlMediatypesResource)

from infiniguard_api.view.user_api import (
    UserResource, UsersResource, user_api)
from infiniguard_api.view.asynctask_api import (
    AsynctaskResource,
    AsynctasksResource,
    AsynctaskFilesResource,
    AsynctaskProgressResource,
    asynctask_api)
from infiniguard_api.view.infinibox_api import (infinibox_api, InfiniboxCustomEvent,
                                                InfiniboxExternalEvent, InfiniboxDrive,
                                                InfiniboxDrives, InfiniboxDriveHW,
                                                InfiniboxEnclosure, DdePatchPanels,
                                                DdeNodeStatus, DdeNodesStatus,
                                                InfinidatUsersResource,
                                                InfinidatUserResource,
                                                InfinidatUserByUsernameResource,
                                                InfinidatUserEnableResource,
                                                InfinidatUserDisableResource,
                                                InfinidatUserLoginResource,
                                                InfinidatUserLogoutResource,
                                                InfiniboxSystemHealthState,
                                                InfiniboxSystemName,
                                                InfinidatLdapResource,
                                                InfinidatLdapsResource)
from infiniguard_api.__version__ import __version__
from distutils.version import LooseVersion
import json
from pathlib import Path
from infi.caching import cached_function
from http import HTTPStatus

SCHEMAS = list()


def enable_remote_debug_server(ipaddr, port):
    try:
        import sys
        sys.path.append("pydevd-pycharm.egg")
        import pydevd_pycharm
        pydevd_pycharm.settrace(
            ipaddr, port=port, stdoutToServer=True, stderrToServer=True)
    except Exception as e:
        raise e


def define_openapi_schemas(app):
    from infiniguard_api.model.ost_schemas import schema_classes as ostschemas
    from infiniguard_api.model.base_schema import schema_classes as baseschemas
    from infiniguard_api.model.user_schemas import schema_classes as userschemas
    from infiniguard_api.model.network import schema_classes as networkschemas
    from infiniguard_api.model.vtl_schemas import schema_classes as vtlschemas
    from infiniguard_api.model.nas_schemas import schema_classes as nasschemas
    from infiniguard_api.model.replication_schemas import schema_classes as replicationschemas
    from itertools import chain
    spec = app.config['APISPEC_SPEC']

    for cls in chain(baseschemas, ostschemas, userschemas, networkschemas, vtlschemas, nasschemas, replicationschemas):
        spec.components.schema(cls.__name__, schema=cls)


def schema_name_resolver(schema):
    global SCHEMAS
    schema_cls = resolve_schema_cls(schema)
    name = schema_cls.__name__
    while name in SCHEMAS:
        index = 0
        suffix = re.sub("[^0-9]", "", name)
        if suffix:
            index = int(suffix)
            name = re.sub("[0-9]", "", name)
        name = name + str(index + 1)
    SCHEMAS.append(name)
    return name


def get_local_version() -> LooseVersion:
    fname = '/etc/infiniguard-release.json'
    release = json.loads(Path(fname).read_text())
    return LooseVersion(release['infiniguard'])


@cached_function
def assure_running_version_uptodate():
    lst = get_ibox().api.get('/api/rest/integrations/infiniguard/dde_nodes?fields=dde_instance_version').get_result()
    max_iguard_ver = max(LooseVersion(elt['dde_instance_version']) for elt in lst)
    myver = get_local_version()
    if myver < max_iguard_ver:
        error = build_error_model(
            error_message=build_error_message(
                {'DDE Version Check': f'API is disabled because this DDE is running outdated '
                 f'version {myver} while {max_iguard_ver} is expected.'}),
            error_code='DDE_VERSION_OUTDATED')
        return build_paginated_response(error=error).to_primitive(), HTTPStatus.CONFLICT


def create_app(*args, **kwargs):
    # Only enable in case of PDF generation
    if os.environ.get('PDF_GEN'):
        dde_prefix = '/api/dde/{ddeId}/api'
        info = {} if 'OPENAPI_GEN' in os.environ else {
            'description': messages.API_DESCRIPTION}
    else:
        dde_prefix = ''
        info = {}

    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    app.config.update({
        'APISPEC_SPEC': apispec.APISpec(
            title='InfiniGuard API Reference',
            info=info,
            tags=messages.TAGS,
            version=__version__,
            openapi_version='2.0',
            plugins=[
                MarshmallowPlugin(schema_name_resolver=schema_name_resolver),
            ]),
        'APISPEC_SWAGGER_URL': '/swagger/',
    })
    app.url_map.strict_slashes = False

    app.register_error_handler(422, handle_error)
    app.register_error_handler(400, handle_error_malformed)

    app.register_blueprint(
        asynctask_api, url_prefix=dde_prefix + '/asynctasks')
    app.register_blueprint(user_api, url_prefix=dde_prefix + '/user')
    app.register_blueprint(network_api, url_prefix=dde_prefix + '/network/')
    app.register_blueprint(
        network_tools_api, url_prefix=dde_prefix + '/network/tools/')
    app.register_blueprint(ost_api, url_prefix=dde_prefix + '/ost/')
    app.register_blueprint(
        replication_api, url_prefix=dde_prefix + '/replication/')
    app.register_blueprint(node_api, url_prefix=dde_prefix + '/node/')
    app.register_blueprint(nas_api, url_prefix=dde_prefix + '/nas/')
    # app.register_blueprint(vtl_api, url_prefix=dde_prefix+'/vtl/')

    app.before_request(assure_running_version_uptodate)

    if os.environ.get('PDF_GEN'):
        app.register_blueprint(infinibox_api, url_prefix='/api/rest/')
    docs = FlaskApiSpec(app)
    if os.environ.get('PDF_GEN'):
        docs.register(InfiniboxCustomEvent, endpoint='custom',
                      blueprint='infinibox_api')
        docs.register(InfiniboxExternalEvent, endpoint='external',
                      blueprint='infinibox_api')
        docs.register(InfiniboxDrive, endpoint='drive',
                      blueprint='infinibox_api')
        docs.register(InfiniboxDrives, endpoint='drives',
                      blueprint='infinibox_api')
        docs.register(InfiniboxDriveHW, endpoint='hw',
                      blueprint='infinibox_api')
        docs.register(InfiniboxEnclosure, endpoint='enclosure',
                      blueprint='infinibox_api')
        docs.register(DdePatchPanels, endpoint='patchpanel',
                      blueprint='infinibox_api')
        docs.register(DdeNodeStatus, endpoint='status',
                      blueprint='infinibox_api')
        docs.register(DdeNodesStatus, endpoint='statuses',
                      blueprint='infinibox_api')
        docs.register(InfinidatUsersResource,
                      endpoint='iboxusers', blueprint='infinibox_api')
        docs.register(InfinidatUserResource, endpoint='iboxuser',
                      blueprint='infinibox_api')
        docs.register(InfinidatUserByUsernameResource,
                      endpoint='iboxuser_by_username', blueprint='infinibox_api')
        docs.register(InfinidatUserDisableResource,
                      endpoint='iboxuser_disable', blueprint='infinibox_api')
        docs.register(InfinidatUserEnableResource,
                      endpoint='iboxuser_enable', blueprint='infinibox_api')
        docs.register(InfinidatUserLoginResource,
                      endpoint='iboxuser_login', blueprint='infinibox_api')
        docs.register(InfinidatUserLogoutResource,
                      endpoint='iboxuser_logout', blueprint='infinibox_api')
        docs.register(InfiniboxSystemHealthState,
                      endpoint='healthstate', blueprint='infinibox_api')
        docs.register(InfiniboxSystemName, endpoint='systemname',
                      blueprint='infinibox_api')
        docs.register(InfinidatLdapResource, endpoint='ldap',
                      blueprint='infinibox_api')
        docs.register(InfinidatLdapsResource, endpoint='ldaps',
                      blueprint='infinibox_api')

    docs.register(UserResource, endpoint='user', blueprint='user_api')
    docs.register(UsersResource, endpoint='users', blueprint='user_api')
    docs.register(RebootResource, endpoint='reboot', blueprint='node_api')

    docs.register(AsynctaskResource, endpoint='asynctask',
                  blueprint='asynctask_api')
    docs.register(AsynctasksResource, endpoint='asynctasks',
                  blueprint='asynctask_api')
    docs.register(AsynctaskFilesResource,
                  endpoint='asynctask_files', blueprint='asynctask_api')
    docs.register(AsynctaskProgressResource,
                  endpoint='asynctask_progress', blueprint='asynctask_api')

    docs.register(StorageserverResource,
                  endpoint='storageserver', blueprint='ost_api')
    docs.register(StorageserversResource,
                  endpoint='storageservers', blueprint='ost_api')
    docs.register(LsuResource, endpoint='lsu', blueprint='ost_api')
    docs.register(LsusResource, endpoint='lsus', blueprint='ost_api')
    # docs.register(TlscertificateResource, endpoint='tlscertificate', blueprint='ost_api')
    docs.register(OstairResource, endpoint='ostair', blueprint='ost_api')
    docs.register(OstsettingResource, endpoint='ostsetting',
                  blueprint='ost_api')
    # docs.register(OstaccentstatsResource, endpoint='accentstats', blueprint='ost_api')

    docs.register(HostResource, endpoint='host', blueprint='network_api')
    docs.register(DevicesResource, endpoint='devices', blueprint='network_api')
    docs.register(DeviceResource, endpoint='device', blueprint='network_api')
    docs.register(StaticRoutesResource, endpoint='static_routes',
                  blueprint='network_api')
    docs.register(StaticRoutesResourceDevname,
                  endpoint='static_routes_devname', blueprint='network_api')
    docs.register(StaticRouteResource, endpoint='static_route',
                  blueprint='network_api')
    docs.register(StaticRouteResourceDevname,
                  endpoint='static_route_devname', blueprint='network_api')

    docs.register(InterfacesResource, endpoint='interfaces',
                  blueprint='network_api')
    docs.register(InterfaceResource, endpoint='interface',
                  blueprint='network_api')
    docs.register(BondsResource, endpoint='bonds', blueprint='network_api')
    docs.register(BondResource, endpoint='bond', blueprint='network_api')
    # docs.register(NetworkBackupResource, endpoint='backup', blueprint='network_api')
    # docs.register(NetworkRestoreResource, endpoint='restore', blueprint='network_api')
    docs.register(PingResource, endpoint='ping', blueprint='network_tools_api')
    docs.register(MtuResource, endpoint='mtu', blueprint='network_tools_api')
    docs.register(DigResource, endpoint='dig',
                  blueprint='network_tools_api')
    docs.register(ResolvResource, endpoint='resolv',
                  blueprint='network_tools_api')
    docs.register(TracerouteResource, endpoint='traceroute',
                  blueprint='network_tools_api')
    docs.register(IperfResource, endpoint='iperf',
                  blueprint='network_tools_api')
    docs.register(InterfacesDetailsResource, endpoint='interface_details',
                  blueprint='network_tools_api')

    docs.register(SourcerepResource, endpoint='sourcerep',
                  blueprint='replication_api')
    docs.register(SourcerepsResource, endpoint='sourcereps',
                  blueprint='replication_api')
    docs.register(TargetrepResource, endpoint='targetrep',
                  blueprint='replication_api')
    docs.register(TargetrepsResource, endpoint='targetreps',
                  blueprint='replication_api')
    # docs.register(OstMappingResource, endpoint='ostmapping', blueprint='replication_api')
    # docs.register(OstMappingsResource, endpoint='ostmappings', blueprint='replication_api')

    docs.register(ShareResource, endpoint='share', blueprint='nas_api')
    docs.register(SharesResource, endpoint='shares', blueprint='nas_api')
    docs.register(NfsShareResource, endpoint='nfs_share', blueprint='nas_api')
    docs.register(NfsSharesResource, endpoint='nfs_shares',
                  blueprint='nas_api')
    docs.register(NfsShareHostResource,
                  endpoint='nfs_sharehost', blueprint='nas_api')
    docs.register(NfsShareHostsResource,
                  endpoint='nfs_sharehosts', blueprint='nas_api')
    docs.register(NfsNfssettingResource,
                  endpoint='nfs_nfssetting', blueprint='nas_api')
    docs.register(CifsShareResource, endpoint='cifs_share',
                  blueprint='nas_api')
    docs.register(CifsSharesResource, endpoint='cifs_shares',
                  blueprint='nas_api')
    docs.register(CifsShareUserResource,
                  endpoint='cifs_shareuser', blueprint='nas_api')
    docs.register(CifsShareUsersResource,
                  endpoint='cifs_shareusers', blueprint='nas_api')
    docs.register(CifsWorkgroupsResource,
                  endpoint='cifs_workgroups', blueprint='nas_api')
    docs.register(CifsAdsDomainsResource,
                  endpoint='cifs_adsdomains', blueprint='nas_api')
    docs.register(CifsShareAdminResource,
                  endpoint='cifs_shareadmin', blueprint='nas_api')
    docs.register(CifsShareAdminsResource,
                  endpoint='cifs_shareadmins', blueprint='nas_api')
    docs.register(CifsSmbsettingResource,
                  endpoint='cifs_smbsetting', blueprint='nas_api')
    docs.register(AppSpecificShareResource,
                  endpoint='app_specific_share', blueprint='nas_api')
    docs.register(AppSpecificSharesResource,
                  endpoint='app_specific_shares', blueprint='nas_api')

# ===============================================================================
#     docs.register(ShareResource, endpoint='share', blueprint='nas_api')
#     docs.register(SharesResource, endpoint='shares', blueprint='nas_api')
#     docs.register(NfsShareResource, endpoint='nfs_share', blueprint='nas_api')
#     docs.register(NfsSharesResource, endpoint='nfs_shares', blueprint='nas_api')
#     docs.register(NfsShareHostResource, endpoint='nfs_sharehost', blueprint='nas_api')
#     docs.register(NfsShareHostsResource, endpoint='nfs_sharehosts', blueprint='nas_api')
#     docs.register(NfsNfssettingResource, endpoint='nfs_nfssetting', blueprint='nas_api')
#     docs.register(CifsShareResource, endpoint='cifs_share', blueprint='nas_api')
#     docs.register(CifsSharesResource, endpoint='cifs_shares', blueprint='nas_api')
#     docs.register(CifsShareUserResource, endpoint='cifs_shareuser', blueprint='nas_api')
#     docs.register(CifsShareUsersResource, endpoint='cifs_shareusers', blueprint='nas_api')
#     docs.register(CifsWorkgroupsResource, endpoint='cifs_workgroups', blueprint='nas_api')
#     docs.register(CifsAdsDomainsResource, endpoint='cifs_adsdomains', blueprint='nas_api')
#     docs.register(CifsShareAdminResource, endpoint='cifs_shareadmin', blueprint='nas_api')
#     docs.register(CifsShareAdminsResource, endpoint='cifs_shareadmins', blueprint='nas_api')
#     docs.register(CifsSmbsettingResource, endpoint='cifs_smbsetting', blueprint='nas_api')
    docs.register(AppSpecificShareResource,
                  endpoint='app_specific_share', blueprint='nas_api')
    docs.register(AppSpecificSharesResource,
                  endpoint='app_specific_shares', blueprint='nas_api')
    docs.register(AppSpecificShareFilesResource,
                  endpoint='app_specific_share_files', blueprint='nas_api')

#
#     docs.register(PartitionResource, endpoint='partition', blueprint='vtl_api')
#     docs.register(PartitionOnlineResource, endpoint='partition_online', blueprint='vtl_api')
#     docs.register(PartitionOfflineResource, endpoint='partition_offline', blueprint='vtl_api')
#     docs.register(PartitionsResource, endpoint='partitions', blueprint='vtl_api')
#     docs.register(PartitionsOnlineResource, endpoint='partitions_online', blueprint='vtl_api')
#     docs.register(PartitionsOfflineResource, endpoint='partitions_offline', blueprint='vtl_api')
#     docs.register(PartitionDevicesResource, endpoint='partition_devices', blueprint='vtl_api')
#     docs.register(MediaResource, endpoint='media', blueprint='vtl_api')
#     docs.register(MediaImportResource, endpoint='media_import', blueprint='vtl_api')
#     docs.register(MediaExportResource, endpoint='media_export', blueprint='vtl_api')
#     docs.register(MediaWriteProtectEnableResource, endpoint='media_write_protect_enable', blueprint='vtl_api')
#     docs.register(MediaWriteProtectDisableResource, endpoint='media_write_protect_disable', blueprint='vtl_api')
#     docs.register(MediaRecycleResource, endpoint='media_recycle', blueprint='vtl_api')
#     docs.register(MediaUnloadResource, endpoint='media_unload', blueprint='vtl_api')
#     docs.register(MediasResource, endpoint='medias', blueprint='vtl_api')
#     docs.register(MediasImportResource, endpoint='medias_import', blueprint='vtl_api')
#     docs.register(MediasExportResource, endpoint='medias_export', blueprint='vtl_api')
#     docs.register(MediasWriteProtectEnableResource, endpoint='medias_write_protect_enable', blueprint='vtl_api')
#     docs.register(MediasWriteProtectDisableResource, endpoint='medias_write_protect_disable', blueprint='vtl_api')
#     docs.register(MediasRecycleResource, endpoint='medias_recycle', blueprint='vtl_api')
# ===============================================================================
    delete_running_tasks()
    vacuum()
    session = get_session()
    start_worker(session)
    return app
