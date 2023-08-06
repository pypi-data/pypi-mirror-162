import six
from marshmallow import Schema, fields, post_load
from marshmallow.schema import SchemaMeta


class GenericModel(object):
    def __init__(self, schema, **kwargs):
        self.__schema__ = schema
        for attr in schema.declared_fields:
            if hasattr(schema.declared_fields[attr], 'many'):
                setattr(self, attr, [])
            else:
                setattr(self, attr, None)
        for k, v in kwargs.items():
            if k in schema.declared_fields:
                setattr(self, k, v)

    def __repr__(self):
        return str(self.to_json())

    def to_json(self):
        out = {}
        for key in self.__schema__.declared_fields:
            v = getattr(self, key)
            if isinstance(v, GenericModel):
                out[key] = str(v)
            elif isinstance(v, (int, float)) or v is None:
                out[key] = v
            else:
                out[key] = str(v)
        return out


# noinspection PyTypeChecker
class BaseSchema(Schema):
    @post_load
    def create_object(self, data, **kwargs):
        return GenericModel(self, **data)


class _MetaClass(SchemaMeta):
    def __call__(cls, *args, **kwargs):
        keys = ['only', 'exclude', 'many', 'context', 'load_only', 'dump_only', 'partial', 'unknown']
        if len(kwargs) > 0 and list(kwargs.keys())[0] in keys:
            inst = super(_MetaClass, cls).__call__(*args, **kwargs)
        else:
            inst = super(_MetaClass, cls).__call__()

        for attr in inst.declared_fields:
            if hasattr(inst.declared_fields[attr], 'many'):
                setattr(inst, attr, [])
            else:
                setattr(inst, attr, None)
        for k, v in kwargs.items():
            if k in inst.declared_fields:
                setattr(inst, k, v)
        return inst


class BaseClass(six.with_metaclass(_MetaClass), Schema):

    @post_load
    def create(self, data, **kwargs):
        return self.__class__(**data)

    def __repr__(self):
        return str(self.to_json())

    def to_json(self):
        out = {}
        for key in self.declared_fields:
            v = getattr(self, key)
            if isinstance(v, BaseClass):
                out[key] = str(v)
            elif isinstance(v, (int, float)) or v is None:
                out[key] = v
            else:
                out[key] = str(v)
        return out


#   class BaseSchema(Schema):
#     pass
#
#   class BaseClass(Schema):
#     pass

if __name__ == '__main__':
    def as_schema():
        class Student(BaseSchema):
            name = fields.String()

        class Class(BaseSchema):
            class_name = fields.String()
            students = fields.Nested(Student, many=True)  # type List[Student]

        print('Defining base schema as schema')
        data = dict(class_name='Science', students=[dict(name='Jody')])
        result = Class().load(data).data
        print(result)


    def as_class():
        class Student(BaseClass):
            name = fields.String()

        class Class(BaseClass):
            class_name = fields.String()
            students = fields.Nested(Student, many=True)  # type List[Student]

        print('Defining base class as class')
        data = dict(class_name='Science', students=[dict(name='Jody')])
        result = Class().load(data).data
        print(result)


    as_schema()
    as_class()
