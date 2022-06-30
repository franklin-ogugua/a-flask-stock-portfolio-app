"""
The admin blueprint handles the management of users for this application.

Specifically, this blueprint allows an administrative (super-user)
to edit and delete users.
"""
from flask import Blueprint

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')

from . import routes
