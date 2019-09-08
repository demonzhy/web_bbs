from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *
from models.topic import Topic
from models.board import Board


main = Blueprint('topic', __name__)


@main.route("/")
def index():
    u = current_user()
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        ms = Topic.all()
    else:
        ms = Topic.all(board_id=board_id)
    token = new_csrf_token()
    bs = Board.all()
    return render_template("topic/index.html", ms=ms, token=token, bs=bs, bid=board_id, u=u)


@main.route('/<int:id>')
def detail(id):
    # id = int(request.args['id'])
    # http://localhost:3000/topic/1
    # m = Topic.one(id=id)
    m = Topic.get(id)

    # 不应该放在路由里面
    # m.views += 1
    # m.save()

    # 传递 topic 的所有 reply 到 页面中
    return render_template("topic/detail.html", topic=m)


@main.route("/new")
def new():
    log('你进入new')
    board_id = int(request.args.get('board_id',-1))
    bs = Board.all()
    # return render_template("topic/new.html", bs=bs, bid=board_id)
    token = new_csrf_token()
    log('new-token', token)
    return render_template("topic/new.html", bs=bs, token=token, bid=board_id)


@main.route("/delete")
@csrf_required
def delete():
    id = int(request.args.get('id'))
    u = current_user()
    print('删除 topic 用户是', u, id)
    Topic.delete(id)
    return redirect(url_for('.index'))


@main.route("/add", methods=["POST"])
@csrf_required
def add():
    form = request.form.to_dict()
    log('bf form', form)
    if form['title'] == None or form['content'] == None:
        log('bf if ', form)
        return redirect(url_for('.index'))
    else:
        u = current_user()
        Topic.new(form, user_id=u.id)
        return redirect(url_for('.index'))



