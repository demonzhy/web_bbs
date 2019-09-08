from sqlalchemy import String, Integer, Column, Text, UnicodeText, Unicode
from models.base_model import SQLMixin, db
from models.user import User
from models.reply import Reply
from models.board import Board


class Topic(SQLMixin, db.Model):
    views = Column(Integer, nullable=False, default=0)
    title = Column(Unicode(50), nullable=False)
    content = Column(UnicodeText, nullable=False)
    user_id = Column(Integer, nullable=False)
    board_id = Column(Integer, nullable=False)

    def board(self):
        u = Board.one(id=self.board_id)
        return u

    @classmethod
    def new(cls, form, user_id):
        form['user_id'] = user_id
        m = super().new(form)
        return m

    @classmethod
    def get(cls, id):
        m = cls.one(id=id)
        m.views += 1
        m.save()
        return m

    @classmethod
    def delete(cls, id):
        # m = cls.one(id=id)
        Topic.query.filter_by(id=id).delete()
        Reply.query.filter_by(topic_id=id).delete()
        db.session.commit()

    def user(self):
        u = User.one(id=self.user_id)
        return u

    def replies(self):
        ms = Reply.all(topic_id=self.id)
        return ms

    def reply_count(self):
        count = len(self.replies())
        return count

    def reply_user_time(self, user_id):

        r = Reply.query\
            .join(Topic,Reply.topic_id==self.id)\
            .filter(Reply.user_id==user_id) \
            .order_by(Reply.created_time.desc()) \
            .limit(1) \
            .first()
        return r

    def last_reply(self):
        r = Reply.query\
            .join(Topic,Reply.topic_id==self.id)\
            .filter(Reply.topic_id==self.id) \
            .order_by(Reply.created_time.desc()) \
            .limit(1) \
            .first()
        return r



