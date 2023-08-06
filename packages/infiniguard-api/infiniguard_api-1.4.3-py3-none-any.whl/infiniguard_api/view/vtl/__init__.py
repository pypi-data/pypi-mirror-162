__import__("pkg_resources").declare_namespace(__name__)

from flask import Blueprint

vtl_api = Blueprint('vtl_api', __name__)