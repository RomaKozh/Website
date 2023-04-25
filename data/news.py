import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.BLOB)
    created_date = sqlalchemy.Column(sqlalchemy.Date, default=datetime.date.today())
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    def set_title(self, title):
        self.title = title

    def set_description(self, description):
        self.description = description

    def set_content(self, content):
        self.content = content

    def set_photo(self, photo):
        self.photo = photo
