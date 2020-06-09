from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms import Form as NoCsrfForm
from wtforms.utils import unset_value

class AddSourceForm(NoCsrfForm):
    source_select = SelectField('Source', validators=[DataRequired()], coerce=int)

class AddNotificationAgentForm(NoCsrfForm):
    notification_agent_select = SelectField('Notification Agent', validators=[DataRequired()], coerce=int)

class TaskForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    frequency = StringField('Frequency (Minutes)', validators=[DataRequired()])
    sources = FieldList(FormField(AddSourceForm), min_entries=1)
    add_source = SubmitField('Add another source')
    notification_agents = FieldList(FormField(AddNotificationAgentForm), min_entries=1)
    add_notification_agent = SubmitField('Add another notification agent')
    colour_flag = StringField('Colour Flag')
    must_contain = StringField('Must Contain')
    exclude = StringField('Exclude')
    prime_count = StringField('Number of ads to show when the task is created (0 = No notifications during priming)', default='3')
    submit = SubmitField('Save')
