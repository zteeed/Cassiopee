from config import db
from flask_login import UserMixin


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=True)
    token_reset = db.Column(db.String(200), unique=False, nullable=True)
    password_reset = db.Column(db.String(200), unique=False, nullable=True)

    def __repr__(self):
        return '<Users %r>' % self.name
