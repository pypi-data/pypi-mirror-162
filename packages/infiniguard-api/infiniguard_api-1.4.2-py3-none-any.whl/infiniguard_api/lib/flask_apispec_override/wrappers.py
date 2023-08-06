import flask
from webargs import flaskparser
import functools
import flask_apispec.annotations
import werkzeug
from flask_apispec import (FlaskApiSpec, MethodResource, Ref, ResourceMeta, doc, marshal_with, use_kwargs, utils,
                           wrap_with, wrapper)


class PatchedWrapper(wrapper.Wrapper):
    pass
    # def call_view(self, *args, **kwargs):
    #     config = flask.current_app.config
    #     parser = config.get('APISPEC_WEBARGS_PARSER', flaskparser.parser)
    #     parser.location="json_or_form"
    #     annotation = utils.resolve_annotations(self.func,
    #                                            'args',
    #                                            self.instance)
    #     if annotation.apply is not False:
    #         for option in annotation.options:
    #             schema = utils.resolve_resource(option['args'])
    #             parsed = parser.parse(schema,
    #                                   locations=option['kwargs']['locations'])
    #             if getattr(schema, 'many', False):
    #                 args += tuple(parsed)
    #             else:
    #                 # noinspection PyProtectedMember
    #                 kwargs.update(parsed)
    #     return self.func(*args, **kwargs)

#     def __call__(self, *args, **kwargs):
#         response = self.call_view(*args, **kwargs)
#         if isinstance(response, werkzeug.Response):
#             return response
#         unpacked = wrapper.unpack(response)
#         qualifier = unpacked[1] if unpacked[2] is not None else 'default'
#         status_code = unpacked[1] if unpacked[2] is None else unpacked[2]
#         return self.marshal_result(unpacked, status_code, qualifier)
#
#     def marshal_result(self, unpacked, status_code='default', qualifier='default'):
#         config = flask.current_app.config
#         format_response = config.get('APISPEC_FORMAT_RESPONSE', flask.jsonify) or identity
#         annotation = utils.resolve_annotations(self.func, 'schemas', self.instance)
#         schemas = utils.merge_recursive(annotation.options)
#         qualifier_schema = schemas.get(qualifier, schemas.get('default'))
#         schema = qualifier_schema.get(status_code, qualifier_schema.get('default'))
#         if schema and annotation.apply is not False:
#             schema = utils.resolve_instance(schema['schema'])
#             output = schema.dump(unpacked[0]).data
#         else:
#             output = unpacked[0]
#         rest = unpacked[1:] if unpacked[2] is None else unpacked[2:]
#         return wrapper.format_output((format_response(output), ) + rest)
#
# def marshal_with(schema, code='default', qualifier='default', description='', inherit=None, apply=None):
#     """Marshal the return value of the decorated view function using the
#     specified schema.
#
#     Usage:
#
#     .. code-block:: python
#
#         class PetSchema(Schema):
#             class Meta:
#                 fields = ('name', 'category')
#
#         @marshal_with(PetSchema)
#         def get_pet(pet_id):
#             return Pet.query.filter(Pet.id == pet_id).one()
#
#     :param schema: :class:`Schema <marshmallow.Schema>` class or instance, or `None`
#     :param code: Optional HTTP response code
#     :param qualifier: Optional qualifier value between schemas
#     :param description: Optional response description
#     :param inherit: Inherit schemas from parent classes
#     :param apply: Marshal response with specified schema
#     """
#     def wrapper(func):
#         options = {
#             qualifier: {
#                 code: {
#                     'schema': schema or {},
#                     'description': description,
#                 },
#             }
#         }
#         flask_apispec.annotations.annotate(func, 'schemas', [options], inherit=inherit, apply=apply)
#         return activate(func)
#     return wrapper
#
# flask_apispec.annotations.marshal_with = marshal_with
#
#
def activate(func):
    if isinstance(func, type) or getattr(func,
                                         '__apispec__', {}).get('wrapped'):
        return func

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        instance = args[0] if func.__apispec__.get('ismethod') else None
        annotation = utils.resolve_annotations(func, 'wrapper', instance)
        wrapper_cls = utils.merge_recursive(
            annotation.options).get('wrapper', PatchedWrapper)
        wrapper = wrapper_cls(func, instance)
        return wrapper(*args, **kwargs)

    wrapped.__apispec__['wrapped'] = True
    return wrapped


flask_apispec.annotations.activate = activate

__all__ = [
    'doc',
    'wrap_with',
    'use_kwargs',
    'marshal_with',
    'ResourceMeta',
    'MethodResource',
    'FlaskApiSpec',
    'Ref',
]
