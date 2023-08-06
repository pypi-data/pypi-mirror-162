__import__("pkg_resources").declare_namespace(__name__)

from flask import Blueprint

nas_api = Blueprint('nas_api', __name__)