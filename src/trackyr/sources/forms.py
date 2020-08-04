from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class SourceForm(FlaskForm): 
    MODULE_CHOICES = [(0,'Please Select a Module')]
    module = SelectField('Module', validators=[DataRequired()], coerce=int)
    name = StringField('Name', validators=[DataRequired()])
    website = StringField('Website')
    location = StringField('Location')
    range = StringField('Range (km)')
    # subreddit = StringField('Subreddit (without "r/" , "r/localsales" --> "localsales")')
    submit = SubmitField('Save')
    test = SubmitField('Test')
