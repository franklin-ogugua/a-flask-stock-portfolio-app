from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired, Length


class WatchStockForm(FlaskForm):
    stock_symbol = StringField('Stock Symbol', validators=[DataRequired(), Length(min=1, max=10)])
    submit = SubmitField('Add')
