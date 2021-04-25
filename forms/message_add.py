from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms import HiddenField
from wtforms.validators import DataRequired


class Message_addForm(FlaskForm):
    title = HiddenField()
    content = TextAreaField("Ответить в тему:", validators=[DataRequired()])
    submit = SubmitField('Отправить')
