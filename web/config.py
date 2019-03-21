from flask import Flask, flash, redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from flask_login.utils import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_security import login_required, Security, SQLAlchemyUserDatastore 
import hashlib

from secrets_use import SECRET_KEY, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
""" Default SQLALCHEMY_DATABASE_URI """
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/postgres'
""" Docker SQLALCHEMY_DATABASE_URI """
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@database_postgres/postgres'
app.config["SQLALCHEMY_ECHO"] = True 
app.config["SQLALCHEMY_MAX_OVERFLOW"] = 3 
app.config["SQLALCHEMY_POOL_TIMEOUT"] = 4
app.config["LANGUAGES"] = ['fr']
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
babel = Babel(app)

from tables import Users 


class UsersModelView(ModelView):
    page_size = 5
    column_searchable_list = ['name']
    column_exclude_list = ['password']
    form_excluded_columns = ['password']
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        flash('Access forbidden ! Please identify yourself.', 'error')
        return redirect(url_for('login'))


class DefaultModelView(ModelView):
    page_size = 5
    column_searchable_list = ['name']
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        flash('Access forbidden ! Please identify yourself.', 'error')
        return redirect(url_for('login'))


class MyAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        flash('Access forbidden ! Please identify yourself.', 'error')
        return redirect(url_for('login'))
    def _handle_view(self, name, *args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not self.is_accessible():
            flash('Access forbidden ! Please identify yourself.', 'error')
            return redirect(url_for('login'))


login_manager = LoginManager() 
login_manager.init_app(app) 
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
#app.config['FLASK_ADMIN_SWATCH'] = 'darkly'
admin = Admin(app, name='Cassiopee HackademINT', index_view=MyAdminView(url='/admin'))
admin.add_view(UsersModelView(Users, db.session))

"""
from flask import Blueprint
my_blueprint = Blueprint('my_blueprint', __name__, url_prefix='/admin')
app.register_blueprint(my_blueprint)
"""

@app.before_first_request
def create_user():
    db.create_all()
    users = Users.query.all()
    if len(users) > 0: return
    password = hashlib.sha512(DEFAULT_ADMIN_PASSWORD.encode()).hexdigest()
    kwargs = {'name': DEFAULT_ADMIN_USERNAME, 'email': DEFAULT_ADMIN_EMAIL, 
              'password': password}
    user = Users(**kwargs)
    db.session.add(user)
    db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)
