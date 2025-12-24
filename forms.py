from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
# from models.note import SubtaskType
from models.task import CompletionStatus, SubtaskType


class SubtaskForm(FlaskForm):
    name = StringField('Subtask Name', validators=[DataRequired()])
    type = SelectField('Type', choices=[(t.name, t.value.title()) for t in SubtaskType], validators=[DataRequired()])
    status = SelectField('Status', choices=[(s.name, s.value.replace('_', ' ').title()) for s in CompletionStatus], validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Update Subtask')
