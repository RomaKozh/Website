from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, FileField
from wtforms.validators import DataRequired


class EditForm(FlaskForm):
    name = StringField('Имя пользователя',  validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    avatar = FileField('Аватар профиля', validators=[DataRequired()])
    submit = SubmitField('Изменить')
