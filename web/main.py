from flask import Flask 
from flask import flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login.utils import current_user, login_user, logout_user 

from config import app, db
from tables import Users
from functions import is_admin, debug_print, is_safe_url, get_redirect_target



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods = ['GET', 'POST']) 
def login(): 
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    if request.method == 'GET':
        return render_template('login.html')
    user, verify = is_admin(app, db, request.form)
    if verify:
        login_user(user) 
        nextTarget = get_redirect_target() 
        flash('You are logged in as an administrator', 'success')
        return redirect(nextTarget or url_for('admin.index')) 
    else:
        flash('Authentication failure.', 'error')
        return redirect(url_for('login')) 


@app.route('/logout') 
def logout(): 
    return render_template('login.html')
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    try:
        logout_user()
        flash('Logout done successfully.', 'success')
    except Exception as exception:
        print(exception)
        flash('An error occurred while logging out.', 'error')
    return redirect(url_for('index'))


@app.route('/register') 
def register(): 
    return render_template('register.html')


if __name__=='__main__':
    app.run(host='0.0.0.0')
