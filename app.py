import time
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import secret
from models.base_model import db
from models.topic import Topic
from models.user import User
from models.board import Board

from utils import log

"""
在 flask 中，模块化路由的功能由 蓝图（Blueprints）提供
蓝图可以拥有自己的静态资源路径、模板路径（现在还没涉及）
用法如下
"""
# 注册蓝图
# 有一个 url_prefix 可以用来给蓝图中的每个路由加一个前缀
# import routes.index as index_view
from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.board import main as board_routes
from routes.message import main as mail_routes

from routes.index import not_found

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# db = SQLAlchemy(app)


class BaseModelview(ModelView):
    def getinfo(self):
        return "this is another model"
# @app.template_filter()


def count(input):
    log('count using jinja filter')
    return len(input)


def format_time(unix_timestamp):
    # enum Year():
    #     2013
    #     13
    # f = Year.2013
    f = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(unix_timestamp)
    formatted = time.strftime(f, value)
    return formatted


# def timedelta(unix_timestamp):
#     now = int(time.time())
#     return now-unix_timestamp
def timedelta(unix_timestamp):
    now = int(time.time())
    _period = now - unix_timestamp
    if _period < 60:
        return "刚刚"
    elif 60 <= _period < 3600:
        return "%s分钟前" % int(_period / 60)
    elif 3600 <= _period < 86400:
        return "%s小时前" % int(_period / 3600)
    elif 86400 <= _period < 2592000:
        return "%s天前" % int(_period / 86400)
    else:
        return time.strftime('%Y-%m-%d %H:%M')


def configured_app():
    app = Flask(__name__)
    # 设置 secret_key 来使用 flask 自带的 session
    # 这个字符串随便你设置什么内容都可以
    app.secret_key = secret.secret_key
    # 数据返回顺序
    # mysql -> pymysql -> sqlalchemy -> route
    # 初始化顺序
    # app -> flask-sqlalchemy -> sqlalchemy -> pymysql -> mysql

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:{}@localhost/web19?charset=utf8mb4'.format(
    #     secret.database_password
    # )
    uri = 'mysql+pymysql://root:{}@localhost/new_web?charset=utf8mb4'.format(
        secret.database_password
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(index_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(reply_routes, url_prefix='/reply')
    app.register_blueprint(board_routes, url_prefix='/board')
    app.register_blueprint(mail_routes, url_prefix='/message')
    log('url map', app.url_map)

    # @app.template_filter()
    app.template_filter()(count)
    app.template_filter()(format_time)
    app.template_filter()(timedelta)
    app.errorhandler(404)(not_found)

    admin = Admin(app, name='web17', template_mode='bootstrap3')
    admin.add_view(BaseModelview(User, db.session))
    admin.add_view(BaseModelview(Topic, db.session, endpoint='Topic'))
    # admin.add_view(ModelView(Reply, db.session))
    admin.add_view(ModelView(Board, db.session, endpoint='Board'))
    return app


if __name__ == '__main__':
    app = configured_app()
    # debug 模式可以自动加载你对代码的变动, 所以不用重启程序
    # host 参数指定为 '0.0.0.0' 可以让别的机器访问你的代码
    # 自动 reload jinja
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    config = dict(
        debug=True,
        host='localhost',
        port=3000,
        threaded=True,
    )
    app.run(**config)