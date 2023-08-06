from infiniguard_api.common.messages import paginated_params_desc
from infiniguard_api.controller.network.bonds import create_bond, delete_bond, retrieve_bond, update_bond
from flask_apispec import (MethodResource,
                           doc,
                           marshal_with,
                           use_kwargs)
from infiniguard_api.model.base_schema import MessageSchema, ErrorResponseSchema
from infiniguard_api.model.network import (
    BondCreateSchema, BondResponse, BondsResponse)
from infiniguard_api.view.network.common import network_api
from infiniguard_api.lib.rest.common import http_code
from infiniguard_api.lib.documentation import ddoc


@ddoc
class BondsResource(MethodResource):
    """
    :Methods: POST,GET
    :Tags: Network Bond Interfaces
    """

    @ddoc
    @doc(operationId='create_bond')
    @use_kwargs(BondCreateSchema)
    @marshal_with(BondResponse, code=http_code.ACCEPTED, description="BondPaginatedSchema on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def post(self, **kwargs):
        """
        :Summary: Create bond interface
        """
        response, code = create_bond(kwargs)
        return response, code

    # FIXME: configured not being set correctly?
    @ddoc
    @doc(operationId='retrieve_bonds')
    @doc(params=paginated_params_desc)
    @marshal_with(BondsResponse, code=http_code.OK, description="BondPaginatedSchema on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return all the bond devices
        """
        response, qualifier, code = retrieve_bond(kwargs)
        return response, code


@ddoc
class BondResource(MethodResource):
    """
    :Methods: GET,DELETE
    :Tags: Network Bond Interfaces
    """
    @ddoc
    @doc(operationId='retrieve_bond')
    @doc(params=paginated_params_desc)
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'bond0',
                  'name': 'name',
                  'required': True,
                  'description': 'Bond device name'}
                 })
    @marshal_with(BondResponse, code=http_code.OK, description="BondPaginatedSchema on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def get(self, **kwargs):
        """
        :Summary: Return the bond device
        """
        response, qualifier, code = retrieve_bond(kwargs)
        return response, code

    @ddoc
    @doc(operationId='update_bond')
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'bond0',
                  'name': 'name',
                  'required': True,
                  'description': 'Bond device name'}
                 })
    @use_kwargs(BondCreateSchema(only=('slave_names', 'mode')))
    @marshal_with(BondResponse, code=http_code.ACCEPTED, description="BondPaginatedSchema on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema on failure")
    def patch(self, **kwargs):
        """
        :Summary: Update the bond interface configuration
        """
        response, code = update_bond(kwargs)
        return response, code

    @ddoc
    @doc(operationId='delete_bond')
    @doc(params={'name':
                 {'in': 'path',
                  'type': 'string',
                  'x-example': 'bond0',
                  'name': 'name',
                  'required': True,
                  'description': 'Bond device name'}
                 })
    @marshal_with(MessageSchema, http_code.ACCEPTED, description="MessageSchema returned on success")
    @marshal_with(ErrorResponseSchema, description="ErrorResponseSchema (errors) returned on failure")
    def delete(self, **kwargs):
        """
        :Summary: Delete the bond interface with the specified name
        """
        response, code = delete_bond(**kwargs)
        return response, code


bonds_view_func = BondsResource.as_view('bonds')
bond_view_func = BondResource.as_view('bond')
network_api.add_url_rule(
    'bonds/', view_func=bonds_view_func, methods=['POST', 'GET'])
network_api.add_url_rule(
    'bonds/<string:name>', view_func=bond_view_func, methods=['GET', 'PATCH', 'DELETE'])
