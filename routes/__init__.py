
import uuid
from functools import wraps

import redis
from flask import session, request, abort
from requests import Session

from models.user import User
from utils import log
import json
# csrf_tokens = dict()
cache = redis.StrictRedis(host='127.0.0.1', port=6379)


def current_user():
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
        # s = Session.one_for_session_id(session_id=session_id)
        key = 'session_id_{}'.format(session_id)
        user_id = int(cache.get(key))
        log('current_user key <{}> user_id <{}>'.format(key, user_id))
        u = User.one(id=user_id)
        return u
    else:
        return None


def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']
        k = 'csrf_token_{}'.format(token)

        u = current_user()
        v = cache.get(k)
        v = json.loads(v)
        if cache.exists(k) and v == u.id:
            cache.delete(k)
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


def new_csrf_token():
    u = current_user()
    token = str(uuid.uuid4())
    k = 'csrf_token_{}'.format(token)
    v = json.dumps(u.id)
    cache.set(k, v)
    return token