import time

from sqlalchemy import Unicode, Column

from models.base_model import db, SQLMixin
# from user import User


class Board(SQLMixin, db.Model):
    title = Column(Unicode(50), nullable=False)


    # def user(self):
    #     u = .one(id=self.user_id)
    #     return u