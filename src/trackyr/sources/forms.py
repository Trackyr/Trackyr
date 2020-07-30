from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

import lib.utils.logger as log
from trackyr.models import Module

class SourceForm(FlaskForm):
    MODULE_CHOICES = [(0,'Please Select a Module')]

    modules = Modules.query.all()

    for m in modules:
        if m.category == "source":
            MODULE_CHOICES.append(m.id, m.name)

    #MODULE_CHOICES = [(0,'Please Select a Module'), (1,'Kijiji')]

    log.info_print(f"MODULE_CHOICES: {MODULE_CHOICES}")

    module = SelectField('Module', validators=[DataRequired()], coerce=int, choices=MODULE_CHOICES)
    name = StringField('Name', validators=[DataRequired()])
    website = StringField('Website')
    location = StringField('Location')
    range = StringField('Range (km)')
    # subreddit = StringField('Subreddit (without "r/" , "r/localsales" --> "localsales")')
    submit = SubmitField('Save')
    test = SubmitField('Test')
