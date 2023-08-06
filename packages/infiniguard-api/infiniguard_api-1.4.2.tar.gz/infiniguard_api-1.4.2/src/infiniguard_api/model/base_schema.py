from marshmallow import Schema, pre_dump
from marshmallow.fields import Int, String, Nested, Boolean
from represent import ReprHelper
from schematics.models import Model


class ValidatedMixin(object):
    # noinspection PyArgumentList
    @classmethod
    def validated(cls, **kwargs):
        """Return validated instance, instantiating from kwargs

        :param kwargs: Model fields
        """
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        params = cls(kwargs)
        params.validate()
        return params

    def __repr__(self):
        r = ReprHelper(self)
        for (key, value) in self._data.items():
            r.keyword_with_value(key, value)
        return str(r)


class ConfigModel(ValidatedMixin, Model):
    # noinspection PyClassHasNoInit
    class Options:
        serialize_when_none = False


class DataModel(ValidatedMixin, Model):
    # noinspection PyClassHasNoInit
    class Options:
        serialize_when_none = True


class APIModel(ValidatedMixin, Model):
    # noinspection PyClassHasNoInit
    class Options:
        serialize_when_none = True


class ReadySchema(Schema):
    ready = Boolean(description='metadata ready',
                    required=True,
                    default=True,
                    example=True)


class PaginationSchema(ReadySchema):
    pages_total = Int(
        description='Total pages to represent response with chosen page size', default=1, example=1)
    page = Int(description='Current page number', default=1, example=1)
    page_size = Int(description='Page size', default=50, example=50)
    number_of_objects = Int(
        description='Number of objects in the output', example=1)


class EmptyErrorSchema(Schema):
    error = String(required=True,
                   default=None,
                   example=None,
                   description="Error",
                   allow_none=True
                   )


class ErrorSchema(Schema):
    code = String(description="A machine readable string - can be used to tag and group messages",
                  example='SYSTEM_ERROR')
    message = String(description="Error message",
                     example='Error message')

    @pre_dump
    def convert_error_to_string(self, out_data, **kwargs):
        message = out_data.get('message')
        if isinstance(message, list):
            message = " ,".join([a for a in message])

        out_data['message'] = message
        return out_data


class PaginatedResponseSchema(EmptyErrorSchema):
    metadata = Nested(PaginationSchema,
                      description="metadata such as pagination, sort etc",
                      example={
                          "number_of_objects": 1,
                          "page": 1,
                          "page_size": 50,
                          "pages_total": 1,
                          "ready": True
                      })

    # error = Nested(ErrorSchema, description="error messages",
    #                example={
    #                    "code": "WRONG FIELD VALUES",
    #                    "message": ["password: Missing data",
    #                                "role: missing data"]},
    #                 required=True)


class NonPaginatedResponseSchema(Schema):
    metadata = Nested(ReadySchema,
                      description="metadata such as pagination, sort etc",
                      example={
                          "ready": True
                      })

    error = String(required=True,
                   default=None,
                   example=None,
                   description="Error",
                   allow_none=True
                   )


class ErrorResponseSchema(Schema):
    metadata = Nested(ReadySchema,
                      required=True,
                      description="metadata such as pagination, sort etc",
                      example={
                          "ready": True
                      })
    error = Nested(ErrorSchema, description="error messages",
                   required=True,
                   example={
                       "code": "WRONG FIELD VALUES",
                       "message": ["password: Missing data",
                                   "role: missing data"]
                   })
    result = String(required=True,
                    default=None,
                    example=None,
                    description="Error result",
                    allow_none=True
                    )


class MessageSchema(EmptyErrorSchema):
    metadata = Nested(ReadySchema,
                      description="metadata such as pagination, sort etc",
                      example={
                          "ready": True
                      })
    message = String(description="System Response Message",
                     example="Reboot the DDE for the command to be applied.")


class EmptyResponseSchema(NonPaginatedResponseSchema):
    result = Boolean(description='Result',
                     required=True,
                     default=True,
                     example=True)


class DeleteMessageSchema(EmptyErrorSchema):
    message = String(description="Delete Successful Message",
                     example="Delete object_name succeeded")
    metadata = Nested(ReadySchema,
                      description="metadata such as pagination, sort etc",
                      example={
                          "ready": True
                      })


class JoinMessageSchema(EmptyErrorSchema):
    metadata = Nested(ReadySchema,
                      description="metadata such as pagination, sort etc",
                      example={
                          "ready": True
                      })
    message = String(description="Join Successful Message",
                     example="Join adsdomain/workgroup succeeded")


class DisjoinMessageSchema(EmptyErrorSchema):
    metadata = Nested(ReadySchema,
                      description="metadata such as pagination, sort etc",
                      example={
                          "ready": True
                      })
    message = String(description="Disjoin Successful Message",
                     example="Disjoin adsdomain/workgroup succeeded")


schema_classes = (
    PaginationSchema,
    ErrorSchema,
    PaginatedResponseSchema,
    ErrorResponseSchema,
    MessageSchema,
    DeleteMessageSchema,
    JoinMessageSchema,
    DisjoinMessageSchema,
    EmptyResponseSchema
)
