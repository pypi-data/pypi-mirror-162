from marshmallow import Schema
from marshmallow.fields import Int, String, Nested
from marshmallow import validate, ValidationError
from marshmallow.decorators import validates_schema
from infiniguard_api.model.base_schema import PaginatedResponseSchema
from infiniguard_api.model import custom_fields


class TaskIDSchema(Schema):
    task_id = Int(required=True, description='Task id',
                  example=1572992039781)
    result_uri = String(required=True,
                        description='Resulting URI for task',
                        example='/asynctasks/1572992039781')


class TaskMetadataSchema(Schema):
    code = String(required=True,
                  default='ACCEPTED',
                  example='ACCEPTED',
                  description="Task code"
                  )
    message = String(required=True,
                     example='Task ID 1572992039781 Accepted',
                     description="Task message"
                     )


class TaskSchema(Schema):
    result = Nested(TaskIDSchema,
                    many=False)

    metadata = Nested(TaskMetadataSchema,
                      description="System Response Message")
    error = String(required=True,
                   default=None,
                   example=None,
                   description="Error")
