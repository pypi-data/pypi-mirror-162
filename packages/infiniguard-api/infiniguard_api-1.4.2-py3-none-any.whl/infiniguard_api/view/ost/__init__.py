__import__("pkg_resources").declare_namespace(__name__)

from flask import Blueprint

ost_api = Blueprint('ost_api', __name__)