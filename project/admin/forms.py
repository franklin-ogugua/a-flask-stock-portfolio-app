from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, Length


class PasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Email(), Length(min=6, max=100)])
    submit = SubmitField('Submit')
