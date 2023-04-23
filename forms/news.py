from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    description = TextAreaField('Описание')
    content = TextAreaField('Содержание', validators=[DataRequired()])
    photo = FileField("Фото")
    submit = SubmitField('Добавить новость')