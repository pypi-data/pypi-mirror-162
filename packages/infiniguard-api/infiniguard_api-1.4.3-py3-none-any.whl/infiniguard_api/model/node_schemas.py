from marshmallow import Schema
from marshmallow.fields import Int
from marshmallow import validate


class NodeRebootSchema(Schema):
    wait_time = Int(
        required=False,
        validate=validate.Range(min=1, max=600),
        example=20
    )
