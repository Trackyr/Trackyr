from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SourceForm(FlaskForm): 
    submit = SubmitField('Save')
    test = SubmitField('Test')
