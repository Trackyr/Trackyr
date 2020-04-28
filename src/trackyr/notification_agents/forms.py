from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class NotificationAgentForm(FlaskForm):
    MODULE_CHOICES = [(0,'Please Select a Module'), (1,'Discord')]
    module = SelectField('Module', validators=[DataRequired()], coerce=int, choices=MODULE_CHOICES)
    name = StringField('Name', validators=[DataRequired()])
    webhook_url = StringField('Webhook URL')
    username = StringField('Username')
    icon = StringField('Icon')
    channel = StringField('Channel')
    submit = SubmitField('Save')
    test = SubmitField('Test')
