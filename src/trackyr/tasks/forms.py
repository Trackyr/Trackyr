from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class TaskForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    frequency = StringField('Frequency (Minutes)', validators=[DataRequired()])
    source = SelectField('Source', validators=[DataRequired()], coerce=int)
    notification_agent = SelectField('Notification Agent', validators=[DataRequired()], coerce=int)
    colour_flag = StringField('Colour Flag')
    must_contain = StringField('Must Contain')
    exclude = StringField('Exclude')
    prime_count = StringField('Number of ads to show when the task is created')
    submit = SubmitField('Save')