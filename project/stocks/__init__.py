"""
The stocks blueprint handles the user management for this application.
Specifically, this blueprint allows for users to add, edit, and delete
stock data from their portfolio.
"""
from flask import Blueprint

stocks_blueprint = Blueprint('stocks', __name__, template_folder='templates')

from . import routes
