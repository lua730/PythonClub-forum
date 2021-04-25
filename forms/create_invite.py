from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms import SubmitField


class Create_inviteForm(FlaskForm):
    invite = TextAreaField("Код приглашения", validators=[DataRequired()])
    submit = SubmitField('Создать')