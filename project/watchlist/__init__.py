"""
The watchlist blueprint handles the stock watchlist of users for this application.
"""
from flask import Blueprint

watchlist_blueprint = Blueprint('watchlist', __name__, template_folder='templates')

from . import routes
