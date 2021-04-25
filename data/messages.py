import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

class Messages(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'messages'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    theme_id = sqlalchemy.Column(sqlalchemy.INTEGER)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.INTEGER, sqlalchemy.ForeignKey("users.id"))
    parent = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=True)
    user = orm.relation('User')
