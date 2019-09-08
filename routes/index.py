import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory,
    current_app)
from werkzeug.datastructures import FileStorage

from models.reply import Reply
from models.topic import Topic
from models.user import User
from models.message import *
# from routes import current_user, cache
from routes import *

import json

from utils import log
import gevent
import time

main = Blueprint('index', __name__)


# def current_user():
#     # 从 session 中找到 user_id 字段, 找不到就 -1
#     # 然后用 id 找用户
#     # 找不到就返回 None
#     uid = session.get('user_id', -1)
#     u = User.one(id=uid)
#     return u


"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route("/")
def index():
    u = current_user()
    return render_template("index.html", user=u)


@main.route("/register", methods=['POST'])
def register():
    # form = request.args
    form = request.form
    # 用类函数来判断
    log('bf regester', form)
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    log('be login', form, form['username'])
    u = User.validate_login(form)
    print('login user <{}>'.format(u))
    if u is None:
        log('bf u')
        # 转到 topic.index 页面
        return redirect(url_for('.index'))
    else:
        # # # session 中写入 user_id
        # session['user_id'] = u.id
        # # # 设置 cookie 有效期为 永久
        # session.permanent = True
        # return redirect(url_for('topic.index'))
        session_id = str(uuid.uuid4())
        key = 'session_id_{}'.format(session_id)
        log('index login key <{}> user_id <{}>'.format(key, u.id))
        uid = json.dumps(u.id)
        cache.set(key, uid)

        redirect_to_index = redirect(url_for('topic.index'))
        response = current_app.make_response(redirect_to_index)
        response.set_cookie('session_id', value=session_id)
        # 转到 topic.index 页面
        return response


def created_topic(user_id):
    # O(n)
    ts = Topic.all(user_id=user_id)
    ts = sorted(ts, key=lambda m: m.created_time, reverse=True)
    return ts


def replied_topic(user_id):
    # O(k)+O(m*n)
    rs = Reply.all(user_id=user_id)
    ts = []
    for r in rs:
        t = Topic.one(id=r.topic_id)
        ts.append(t)
    ts = sorted(ts, key=lambda m: m.created_time, reverse=True)
    return ts


@main.route('/profile')
def profile():
    log('running profile route')
    # u = current_user()
    username = request.args.get('username', current_user().username)
    u = User.one(username=username)
    if u is None:
        return redirect(url_for('.index'))
    else:
        # last_reply_1 = last_reply(u.id)
        topics = created_topic(u.id)
        my_topics = replied_topic(u.id)
        return render_template(
            'profile.html',
            u=u,
            # last_reply=last_reply_1,
            topics=topics,
            my_topics=my_topics
        )


@main.route('/user/<int:id>')
def user_detail(id):
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        return render_template('profile.html', user=u)


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file: FileStorage = request.files['avatar']
    # file = request.files['avatar']
    # filename = file.filename
    # ../../root/.ssh/authorized_keys
    # images/../../root/.ssh/authorized_keys
    # filename = secure_filename(file.filename)
    suffix = file.filename.split('.')[-1]
    if suffix not in ['gif', 'jpg', 'jpeg', 'png']:
        abort(400)
        log('不接受的后缀, {}'.format(suffix))
    else:
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        path = os.path.join('images', filename)
        file.save(path)

        u = current_user()
        User.update(u.id, image='/images/{}'.format(filename))

        return redirect(url_for('.setting'))


@main.route('/images/<filename>')
def image(filename):
    # 不要直接拼接路由，不安全，比如
    # http://localhost:3000/images/..%5Capp.py
    # path = os.path.join('images', filename)
    # print('images path', path)
    # return open(path, 'rb').read()
    # if filename in os.listdir('images'):
    #     return
    return send_from_directory('images', filename)


@main.route('/setting')
def setting():
    # form = request.form.to_dict()
    u = current_user()
    return render_template("setting.html", u=u)


@main.route('/setting/sign', methods=['POST'])
def update_sgin():
    u = current_user()
    form = request.form.to_dict()
    # new_username = form['username']
    new_signature = form['signature']
    new_email = form['email']
    new_location = form['location']
    new_blog = form['blog']
    new_github = form['github']

    u.update(u.id, signature=new_signature, location=new_location, blog=new_blog, github=new_github, email=new_email)
    return redirect(url_for('.setting'))


@main.route('/setting/password', methods=['POST'])
def update_password():
    u = current_user()
    form = request.form.to_dict()
    new_password = form['new_password']

    new_password = User.salted_password(new_password)
    u.update(u.id, password=new_password)
    return redirect(url_for('.index'))


@main.route('/image/update', methods=['POST'])
def avatar_update():
    file: FileStorage = request.files['new_avatar']
    suffix = file.filename.split('.')[-1]
    if suffix not in ['gif', 'jpg', 'jpeg', 'png']:
        abort(400)
        log('不接受的后缀, {}'.format(suffix))
    else:
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        path = os.path.join('images', filename)
        file.save(path)

        u = current_user()
        User.update(u.id, image='/images/{}'.format(filename))

        return redirect(url_for('.setting'))


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('.index'))


@main.route('/reset/send', methods=['POST'])
def reset_send():
    form = request.form.to_dict()
    log('form', form)
    username = form['username']
    log('reset pas', username)
    log('usernameis', username)
    u = User.one(username=username)
    token = str(uuid.uuid4())
    csrf_tokens[token] = u.id
    content = 'http://localhost:3000/reset/view?token={}'.format(token)
    title = '更换密码'
    send_mail(
        subject=title,
        author=admin_mail,
        to=u.email,
        content='更换密码连接：\n {}'.format(content),
    )
    return redirect(url_for('.index'))


@main.route('/reset/view')
def reser_view():
    token = request.args['token']
    if token in csrf_tokens:
        return render_template('changepwd.html', token=token)
    else:
        abort(401)


@main.route('/reset/update', methods=['POST'])
def reset_update():
    token = request.args['token']
    password = request.form['password']
    password = User.salted_password(password)
    if token in csrf_tokens:
        current_id = csrf_tokens[token]
        u = User.one(id=current_id)
        u.update(id=current_id, password=password)
        csrf_tokens.pop(token)
        return render_template('changepwd.html')
    else:
        abort(401)


def not_found(e):
    return render_template('404.html')
