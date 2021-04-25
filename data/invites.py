import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

class Invites(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'invites'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    active = sqlalchemy.Column(sqlalchemy.Boolean)
    creator = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.name"))
    invited_user = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    invite = sqlalchemy.Column(sqlalchemy.String)
    user = orm.relation('User')
