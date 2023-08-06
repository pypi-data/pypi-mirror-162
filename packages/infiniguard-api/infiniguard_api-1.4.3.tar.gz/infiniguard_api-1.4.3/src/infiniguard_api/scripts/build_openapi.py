import os
import json
from infiniguard_api.lib.logging import iguard_logging
import logging

os.environ['PDF_GEN'] = "1"
os.environ['OPENAPI_GEN'] = "1"

from infiniguard_api.api_server.infiniguard_api_app import create_app  # @IgnorePep8


def add_ddeid_param(j):
    j['parameters'] = dict(ddeIdRef={'in': 'path',
                                     'name': 'ddeId',
                                     'required': True,
                                     'type': 'integer'})

    paths = j['paths']
    ref = '#/parameters/ddeIdRef'
    for route, p in paths.items():
        if 'ddeId' not in route:
            continue
        param = p.get('parameters', None) or list()
        param.append({'$ref': ref})
        p['parameters'] = param


def main():
    iguard_logging.setup_application_logger(console_level=logging.ERROR)
    app = create_app()
    spec = app.config['APISPEC_SPEC']
    specdict = spec.to_dict()
    add_ddeid_param(specdict)
    print(json.dumps(specdict, indent=2))


if __name__ == '__main__':
    main()
