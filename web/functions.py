from functools import wraps
from flask import flash, request, render_template
from flask_login.utils import current_user
from urllib.parse import urlparse, urljoin
import hashlib

from tables import Users


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return render_template('login.html')
        return f(*args, **kwargs)
    return decorated_function


def debug_print(app, form):
    debug_message = '\n'.join([ str({field: form[field]}) for field in form ])
    app.logger.debug('POST Request: %s', '\n' + debug_message)


def is_safe_url(target): 
    ref_url = urlparse(request.host_url) 
    test_url = urlparse(urljoin(request.host_url, target)) 
    return (test_url.scheme in ('http', 'https') and 
            ref_url.netloc == test_url.netloc)


def get_redirect_target(): 
    for target in request.values.get('next'), request.referrer: 
        if not target: 
            continue 
        if is_safe_url(target): 
            return target


def is_admin(app, db, form):
    if 'username' not in form:
        return None, False
    if 'password' not in form:
        return None, False
    username, password = form['username'], form['password']
    password = hashlib.sha512(password.encode()).hexdigest()
    kwargs = dict(name=username, password=password)

    req = db.session.query(Users).filter_by(**kwargs).first()
    if req is not None:
        return req, True

    """ First connexion """
    kwargs = dict(name=username)
    req = db.session.query(Users).filter_by(**kwargs).first()
    if req is not None:
        req.password = password 
        db.session.commit()
        return req, True
    else:
        return None, False


def update_password(app, db, form):
    kwargs = dict(name=current_user.name)
    req = db.session.query(Users).filter_by(**kwargs).first()
    if req is not None:
        try:
            req.password = hashlib.sha512(form['password'].encode()).hexdigest()
            db.session.commit()
            return True
        except Exception as exception:
            return False
    else:
        return False


def add_admin(app, db, form):
    kwargs = {}
    try:
        for item in form.keys():
            kwargs[item] = form[item]
        user = Users(**kwargs)
        db.session.add(user)
        db.session.commit()
        return True
    except Exception as exception:
        return False
