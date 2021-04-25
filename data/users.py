import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash

class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    themes = orm.relation ( "Themes", back_populates='user' )
    messages = orm.relation ( "Messages", back_populates='user' )
    invites = orm.relation("Invites", back_populates='user')
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    inviter = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    available_invites = sqlalchemy.Column(sqlalchemy.Integer)

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.created_date)

    def set_password(self, password):
        self.hashed_password = generate_password_hash ( password )

    def check_password(self, password):
        return check_password_hash ( self.hashed_password, password )
