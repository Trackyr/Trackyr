from flask_wtf import FlaskForm
from wtforms import SubmitField

class ConfigForm(FlaskForm):
    submit = SubmitField('Update')