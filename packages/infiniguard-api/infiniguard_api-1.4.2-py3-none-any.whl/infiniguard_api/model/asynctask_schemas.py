from marshmallow import Schema
from marshmallow.fields import String, Int, Float, Nested, DateTime, Boolean
from infiniguard_api.model.base_schema import PaginatedResponseSchema, NonPaginatedResponseSchema, MessageSchema, ReadySchema


class AsynctaskSchema(Schema):
    task_id = Int(required=True, description='Task id',
                  example='1572992039781')
    rc = Int(required=True, description='Task return code', example='0')
    status = String(required=True, description='Task status',
                    example='FINISHED')
    stdout = String(description='Task STDOUT', example='Success\n')
    stderr = String(description='Task STDERR', example='')
    start = DateTime(description='Start time',
                     format='%s', example='1562787389')
    end = DateTime(description='End time', format='%s', example='1562787589')
    duration = Float(
        description='Task execution time in second', example='0.25')
    command = String(required=True, description='Command ran by task',
                     example='ping -f 1.2.3.4')
    name = String(required=True, description='Command name',
                  example='ping')


class AsynctasksPaginatedSchema(PaginatedResponseSchema):
    result = Nested(AsynctaskSchema,
                    many=True)
    error = String(required=True,
                   default=None,
                   example=None,
                   description="Error"
                   )


class AsynctaskPaginatedSchema(NonPaginatedResponseSchema):
    result = Nested(AsynctaskSchema,
                    many=False)
    error = String(required=True,
                   default=None,
                   example=None,
                   description="Error"
                   )


class AsynctaskResultSchema(Schema):
    message = String(description="Operation Success Message",
                     example="Delete object_name succeeded")


class AsynctaskMetadataSchema(Schema):
    code = String(required=True,
                  default='DELETED',
                  example='DELETED',
                  description="Task deletion code"
                  )
    ready = Boolean(description='metadata ready',
                    required=True,
                    default=True,
                    example=True)


class AsynctaskMessageSchema(MessageSchema):
    metadata = Nested(ReadySchema,
                      description="metadata such as pagination, sort etc",
                      example={
                          "ready": True
                      })
    result = Nested(AsynctaskResultSchema,
                    required=True)
    error = String(required=True,
                   default=None,
                   example=None,
                   description="Error"
                   )


class AsynctaskDeleteMessageSchema(Schema):
    result = Nested(AsynctaskResultSchema,
                    required=True)
    metadata = Nested(AsynctaskMetadataSchema,
                      description="metadata such as pagination, sort etc",
                      required=True)
    error = String(required=True,
                   default=None,
                   example=None,
                   description="Error"
                   )


class AsynctaskFilesSchema(Schema):
    gid = Int(required=True, description='Group ID', example=0)
    uid = Int(required=True, description='User ID', example=0)
    mode = Int(required=True, description='File mode', example=33188)
    mtime = Int(required=True, description='File modify time',
                example=1589656234)
    ctime = Int(required=True, description='File create time',
                example=1589656123)
    size = Int(required=True, description='File size in bytes', example=314)
    filename = String(required=True, description='File name',
                      example='file1')
    id = Int(required=True, description='Unique file ID', example=123)


class AsynctaskProgressSchema(Schema):
    timestamp = Int(required=True, description='Line creation time',
                    example=1589656234)
    line = String(required=True, description='Line string',
                  example='From 1.2.3.4 icmp_seq=2 Request timeout')
    stdstream = Int(required=True, description='stdout(1) or stderr(2)',
                    example=1)
    id = Int(required=True, description='Unique line ID', example=123)


class AsynctaskListFilesResultsSchema(PaginatedResponseSchema):
    result = Nested(AsynctaskFilesSchema,
                    required=True,
                    many=True)
    error = String(required=True,
                   default=None,
                   example=None,
                   description="Error"
                   )


class AsynctaskListProgressResultsSchema(PaginatedResponseSchema):
    result = Nested(AsynctaskProgressSchema,
                    required=True,
                    many=True)
    error = String(required=True,
                   default=None,
                   example=None,
                   description="Error"
                   )


schema_classes = [AsynctaskSchema,
                  AsynctasksPaginatedSchema,
                  AsynctaskPaginatedSchema,
                  AsynctaskMessageSchema,
                  AsynctaskDeleteMessageSchema,
                  AsynctaskListFilesResultsSchema,
                  AsynctaskListProgressResultsSchema]
