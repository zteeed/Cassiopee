from flask import Flask, flash, redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel
from flask_login import LoginManager
from flask_login.utils import current_user
from flask_mail import Mail
from flask_security import login_required, Security, SQLAlchemyUserDatastore 
from flask_sqlalchemy import SQLAlchemy
from passlib.context import CryptContext


from secrets_use import SECRET_KEY, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_EMAIL, \
DEFAULT_ADMIN_PASSWORD, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, \
MAIL_USE_TLS, MAIL_USE_SSL


pwd_context = CryptContext(
        schemes=["pbkdf2_sha256", "des_crypt"],
        deprecated="auto")


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """ Default SQLALCHEMY_DATABASE_URI """
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost/postgres'
    """ Docker SQLALCHEMY_DATABASE_URI """
    #SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@database_postgres/postgres'
    SQLALCHEMY_ECHO = True 
    SQLALCHEMY_MAX_OVERFLOW = 3 
    SQLALCHEMY_POOL_TIMEOUT = 4
    LANGUAGES = ['fr']
    SECRET_KEY = SECRET_KEY

    FLASK_ADMIN_SWATCH = 'cerulean'
    #FLASK_ADMIN_SWATCH = 'darkly'

    MAIL_SERVER = MAIL_SERVER   
    MAIL_PORT = MAIL_PORT                 
    MAIL_USERNAME = MAIL_USERNAME
    MAIL_PASSWORD = MAIL_PASSWORD     
    MAIL_USE_TLS = MAIL_USE_TLS                       
    MAIL_USE_SSL = MAIL_USE_SSL


app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
#mail.init_app(app)
app.debug = True
db = SQLAlchemy(app)
babel = Babel(app)

from tables import Users 


class UsersModelView(ModelView):
    page_size = 5
    column_searchable_list = ['name']
    column_exclude_list = ['password', 'token_reset', 'password_reset']
    form_excluded_columns = ['password', 'token_reset', 'password_reset']
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


@app.before_first_request
def create_user():
    db.create_all()
    users = Users.query.all()
    if len(users) > 0: return
    password = pwd_context.hash(DEFAULT_ADMIN_PASSWORD)
    kwargs = {'name': DEFAULT_ADMIN_USERNAME, 'email': DEFAULT_ADMIN_EMAIL, 
              'password': password}
    user = Users(**kwargs)
    db.session.add(user)
    db.session.commit()


login_manager = LoginManager() 
login_manager.init_app(app) 
admin = Admin(app, name='Cassiopee HackademINT', index_view=MyAdminView(url='/admin'))
admin.add_view(UsersModelView(Users, db.session))


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)
