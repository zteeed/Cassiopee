from flask import Flask 
from flask import flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login.utils import current_user, login_user, logout_user 

from config import app, db
from tables import Users
from functions import is_admin, debug_print, is_safe_url, get_redirect_target
from proxmox_functions import proxmox_data, select_vm



@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    fields = ['id', 'name', 'status', 'node']
    return render_template('index.html', fields = fields, vms = proxmox_data())


@app.route('/<string:node>/<int:id>')
def show_vm(node, id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    vm = select_vm(node, id)
    return render_template('show_vm.html', vm=vm)


@app.route('/login', methods = ['GET', 'POST']) 
def login(): 
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('login.html')
    user, verify = is_admin(app, db, request.form)
    if verify:
        login_user(user) 
        nextTarget = get_redirect_target() 
        flash('You are logged in as an administrator', 'success')
        return redirect(nextTarget or url_for('index'))
    else:
        flash('Authentication failure.', 'error')
        return redirect(url_for('login')) 


@app.route('/logout') 
def logout(): 
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    try:
        logout_user()
        flash('Logout done successfully.', 'success')
    except Exception as exception:
        print(exception)
        flash('An error occurred while logging out.', 'error')
    return redirect(url_for('index'))


@app.errorhandler(403)
def forbidden(error):
    flash('Error {}'.format(error), 'error')
    return redirect(url_for('index')) 


@app.errorhandler(404)
def not_found(error):
    flash('Error {}'.format(error), 'error')
    return redirect(url_for('index')) 


@app.errorhandler(500)
def internal_server_error(error):
    flash('Error {}'.format(error), 'error')
    return redirect(url_for('index')) 


if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)
