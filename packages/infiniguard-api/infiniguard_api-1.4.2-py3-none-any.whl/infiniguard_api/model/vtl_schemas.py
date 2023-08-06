from marshmallow import Schema
from marshmallow.fields import Int, String, Nested, Boolean
from marshmallow import validate, ValidationError
from marshmallow.decorators import validates_schema
from infiniguard_api.model.base_schema import PaginatedResponseSchema


class VtlPartitionSchema(Schema):
    name = String(
        required=True,
        description='VTL partition name',
        example='myvtl')
    mode = String(
        dump_only=True,
        validate=validate.OneOf(['online', 'offline']),
        description='VTL partition state',
        example='online')
    model = String(
        description='VTL partition model',
        example='Infinidat IBA B4260 DDE')
    drivemodel = String(
        description='VTL partition drive model',
        example='HP LTO-5')
    drives = Int(
        description='number of virtual tape drives attached to the VTL',
        example=20)
    media = Int(
        dump_only=True,
        description='number of media in the VTL',
        example=200)
    slots = Int(
        description='number of storage slots for the VTL',
        example=5000)
    ieslots = Int(
        dump_only=True,
        description='I/E slots for the VTL',
        example=240)
    dedup = Boolean(
        description='whether data dedupliation is enabled',
        example=True)
    autoexport = Boolean(
        description='whether auto-export is enabled',
        example=True)
    replication = Boolean(
        dump_only=True,
        description='whether replication is enabled',
        example=True)


class VtlPartitionsPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlPartitionSchema,
                    many=True)


class VtlPartitionPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlPartitionSchema,
                    many=False)


class VtlPartitionCreateSchema(Schema):
    name = String(
        required=True,
        description='VTL partition name',
        example='myvtl')
    model = String(
        required=True,
        description='VTL partition model',
        example='DXi6900')
    drivemodel = String(
        required=True,
        description='VTL partition drive model',
        example='HPLTO5')
    drives = Int(
        required=True,
        description='number of virtual tape drives attached to the VTL',
        example=2)
    slots = Int(
        required=True,
        description='number of storage slots for the VTL',
        example=20)
    dedup = Boolean(
        description='whether data dedupliation is enabled',
        example=True)
    autoexport = Boolean(
        required=True,
        description='whether auto-export is enabled',
        example=True)


class VtlPartitionEditSchema(Schema):
    name = String(
        required=True,
        description='VTL partition name',
        example='myvtl')
    model = String(
        description='VTL partition model',
        example='DXi6900')
    drivemodel = String(
        description='VTL partition drive model',
        example='HPLTO5')
    drives = Int(
        description='number of virtual tape drives attached to the VTL',
        example=2)
    slots = Int(
        description='number of storage slots for the VTL',
        example=20)
    autoexport = Boolean(
        description='whether auto-export is enabled',
        example=True)


class VtlPartitionDeviceSchema(Schema):
    type = String(
        required=True,
        description='device type',
        example='VMC')
    serial = String(
        description='device serial number',
        example='VD001C2TQKQ2')


class VtlPartitionDevicesPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlPartitionDeviceSchema,
                    many=True)


class VtlPartitionStorageLocationSchema(Schema):
    index = Int(
        description='index of the element',
        example=2)
    address = String(
        description='address',
        example='4103')
    drive_serial_number = String(
        description='drive serial number',
        example='VD001C2TQKQ2')
    barcode = String(
        description='barcode of the media',
        example='SDL101')
    writeprotect = Boolean(
        description='enable/disable write protect',
        example=True)
    access = String(
        description='access type of the media',
        example='scratch')
    used = String(
        description='used percentage of the media',
        example='0.10%')


class VtlPartitionStorageLocationsPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlPartitionStorageLocationSchema,
                    many=True)


class VtlMediaSchema(Schema):
    name = String(
        required=True,
        description='VTL partition name',
        example='myvtl')
    barcode = String(
        description='barcode of the media',
        example='SDL101')
    type = String(
        description='type of the media',
        example='SDLT-S4')
    access = String(dump_only=True,
                    description='access type of the media',
                    example='scratch')
    pool = String(
        description='access type of the media',
        example='scratch')
    used = String(
        description='used percentage of the media',
        example='0.10%')
    capacity = String(
        description='total capacity of the media',
        example='100 GB')
    writeprotect = Boolean(
        description='enable/disable write protect',
        example=True)
    free_space = String(
        description='free space capacity',
        example='100 GB')
    used_data = String(
        description='used data capacity',
        example='1 MB')
    raw_data_size = String(
        description='raw data size',
        example='1 MB')
    compression_ratio = String(
        description='compression ratio',
        example='0.00 x')
    import_behavior = String(
        description='import behavior',
        example='scratch')
    export_behavior = String(
        description='export behavior',
        example='I/E Slot')
    pure_virtual = Boolean(
        description='is pure virtual',
        example=True)
    previous_position = String(
        description='previous media position',
        example='Slot 7')
    current_position = String(
        description='current media position',
        example='Slot 7')
    element_address = String(
        description='element address',
        example='4103')


class VtlMediaCreateSchema(Schema):
    name = String(
        required=True,
        description='VTL partition name',
        example='myvtl')
    type = String(
        description='type of the media',
        example='LTO5')
    asyncronous = Boolean(
        missing=False,
        description='Create media in async mode(the creation is done in async task.)',
        example=False)
    media = Int(
        required=True,
        description='number of media in the VTL',
        example=2)
    barcodestart = String(
        required=True,
        description='start barcode of the media',
        example='SDL101')
    location = String(
        required=True,
        validate=validate.OneOf(['slot', 'ieslot']),
        description='enter the slot or I/E slot to assign to the media',
        example='slot')
    capacity = String(
        description='media capacity in GB',
        example='100 GB')
    


class VtlMediaMoveSchema(Schema):
    name = String(
        required=True,
        description='VTL partition name',
        example='myvtl')
    srctype = String(
        required=True,
        validate=validate.OneOf(['slot', 'drive', 'ieslot']),
        description='source location type',
        example='slot')
    srcindex = Int(
        description='index of source location',
        example=0)
    desttype = String(
        required=True,
        validate=validate.OneOf(['slot', 'drive', 'ieslot']),
        description='destination location type',
        example='drive')
    destindex = Int(
        description='index of destination location',
        example=1)
    forceunload = Boolean(
        description='Force the unload from the drive. This parameter refers to virtual drive source locations',
        example=False)


class VtlMediaUnloadSchema(Schema):
    barcode = String(
        description='barcode of the media',
        example='SDL101')
    loctype = String(
        validate=validate.OneOf(['drive', 'ieslot']),
        description='enter the location type from withich to unload the media, either drive or I/E slot',
        example='drive')
    index = Int(
        description='index of the element',
        example=2)
    forceunload = Boolean(
        description='Force the unload from the drive. This parameter refers to virtual drive source locations',
        example=False)

    @validates_schema
    def _validates_schema(self, data, **kwargs):
        barcode = data.get('barcode', None)
        if not barcode:
            if not data.get('loctype', None) or not data.get('index', None):
                raise ValidationError(
                    'Pease set either barcode or (loctype & index)', 'barcode, loctype, index')
        else:
            if data.get('loctype', None) or data.get('index', None):
                raise ValidationError(
                    'Pease set either barcode or (loctype & index)', 'barcode, loctype, index')


class VtlMediasPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlMediaSchema,
                    many=True)


class VtlMediaPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlMediaSchema,
                    many=False)


class VtlHostSchema(Schema):
    wwpn = String(
        description='world wide port name',
        example='112233445566')
    alias = String(
        description='host alias',
        example='test_host')
    connection_status = String(
        dump_only=True,
        validate=validate.OneOf(['active', 'inactive']),
        description='connection status',
        example='active')


class VtlHostCreateSchema(Schema):
    wwpn = String(
        required=True,
        description='world wide port name',
        example='112233445566')
    alias = String(
        required=True,
        description='host alias',
        example='test_host')


class VtlHostsPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlHostSchema,
                    many=True)


class VtlHostPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlHostSchema,
                    many=False)


class VtlHostmappingSchema(Schema):
    vtlname = String(
        description='VTL partition name',
        attribute='vtl_name',
        example='ICICI-test')
    groupname = String(
        description='Group name',
        attribute='group_name',
        example='test_group')
    wwpn = String(
        description='Host world wide port name',
        attribute='host',
        example='112233445566')
    target = String(
        description='Target port world wide port name',
        example='500e09e200150110')
    useccl = Boolean(
        dump_only=True,
        description='Command and Control LUN (CCL) feature',
        attribute='ccl_in_use',
        example=False)
    total_device_count = Int(
        description='number of devices mapped',
        example=20),
    devices = String(
        description='Devices summary',
        example='0 VMC, 10 VTDs')


class VtlHostmappingCreateSchema(Schema):
    name = String(
        description='VTL partition name',
        example='ICICI-test')
    groupname = String(
        description='Group name',
        example='test_group')
    wwpn = String(
        description='Host world wide port name',
        example='112233445566')
    target = String(
        description='Target port world wide port name',
        example='500e09e200150110')
    useccl = Boolean(
        description='Command and Control LUN (CCL) feature',
        example=False)
    device = String(
        description='device serial number',
        example='VD001C2TQKQ2')
    lun = String(
        description='desired LUN',
        example='2')


class VtlHostmappingsPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlHostmappingSchema,
                    many=True)


class VtlHostmappingPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlHostmappingSchema,
                    many=False)


class VtlTargetSchema(Schema):
    wwpn = String(
        required=True,
        description='world wide port name',
        example='500e09e200150113')
    alias = String(
        description='alias(FC port)',
        example='fc5p4')
    node = String(
        description='node number',
        example='1')


class VtlTargetsPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlTargetSchema,
                    many=True)


class VtlLibrarySchema(Schema):
    productid = String(
        required=True,
        description='Product id',
        example='DXi6900')
    description = String(
        description='Product description',
        example='Infinidat IBA B4260 DDE')


class VtlLibrariesPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlLibrarySchema,
                    many=True)


class VtlDriveSchema(Schema):
    modelnumber = String(
        required=True,
        description='Model number',
        example='HPLTO5')
    description = String(
        required=True,
        description='Drive description',
        example='HP LTO-5')


class VtlDrivesPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlDriveSchema,
                    many=True)


class VtlMediatypeSchema(Schema):
    type = String(
        required=True,
        description='Media type',
        example='LTO4')
    capability = String(
        validate=validate.OneOf(['RW', 'RO']),
        description='media capability',
        example='RW')
    nativecapacity = String(
        required=True,
        description='Native capacity',
        example='200 GB')
    maxcapacity = String(
        required=True,
        description='Max capacity',
        example='6000 GB')


class VtlMediatypesPaginatedSchema(PaginatedResponseSchema):
    result = Nested(VtlMediatypeSchema,
                    many=True)


schema_classes = [
    VtlPartitionSchema,
    VtlPartitionsPaginatedSchema,
    VtlPartitionPaginatedSchema,
    VtlPartitionCreateSchema,
    VtlPartitionEditSchema,
    VtlPartitionDeviceSchema,
    VtlPartitionDevicesPaginatedSchema,
    VtlPartitionStorageLocationSchema,
    VtlPartitionStorageLocationsPaginatedSchema,
    VtlMediaSchema,
    VtlMediaCreateSchema,
    VtlMediaUnloadSchema,
    VtlMediasPaginatedSchema,
    VtlMediaPaginatedSchema,
    VtlHostSchema,
    VtlHostCreateSchema,
    VtlHostsPaginatedSchema,
    VtlHostPaginatedSchema,
    VtlHostmappingSchema,
    VtlHostmappingCreateSchema,
    VtlHostmappingsPaginatedSchema,
    VtlHostmappingPaginatedSchema,
    VtlTargetSchema,
    VtlTargetsPaginatedSchema,
    VtlLibrarySchema,
    VtlLibrariesPaginatedSchema,
    VtlDriveSchema,
    VtlDrivesPaginatedSchema,
    VtlMediatypeSchema,
    VtlMediatypesPaginatedSchema
]
