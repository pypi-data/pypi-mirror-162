__import__("pkg_resources").declare_namespace(__name__)

from flask import Blueprint

replication_api = Blueprint('replication_api', __name__)