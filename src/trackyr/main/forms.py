################################################################
# The purpose of this file is to create a "blank form" so that #
# /src/trackyr/templates/sources.html and                      #
# /src/trackyr/templates/notification-agents.html can have a   #
# form.hidden_tag() for csrf.                                  #
################################################################

from flask_wtf import FlaskForm
from wtforms import SubmitField

class BlankForm(FlaskForm):
    submit = SubmitField('Save')