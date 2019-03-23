from flask import Flask 
from flask import flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login.utils import current_user, login_user, logout_user 

from config import app, db
from tables import Users
from functions import login_required, is_admin, debug_print, is_safe_url, \
get_redirect_target, update_password, add_admin, send_email, update_email
from proxmox_functions import proxmox_data, select_vm



@app.route('/')
@login_required
def index():
    fields = ['id', 'name', 'status', 'node']
    return render_template('index.html', fields = fields, vms = proxmox_data(),
                           username = current_user.name)


@app.route('/<string:node>/<string:type>/<int:id>')
@login_required
def show_vm(node, type, id):
    vm = select_vm(node, type, id)
    return render_template('show_vm.html', vm=vm)



@app.route('/settings/add_admin', methods = ['GET', 'POST'])
@login_required
def settings_add_admin():
    if request.method == 'GET':
        return render_template('settings_add_admin.html')
    is_valid = add_admin(app, db, request.form)
    if is_valid:
        flash('{} is now an administrator.'.format(request.form['name']), 'success')
    else:
        flash('An error occurred while creating a new administrator', 'error')
    return render_template('settings_add_admin.html')


@app.route('/settings/update_admin', methods = ['GET', 'POST'])
@login_required
def settings_update_admin():
    kwargs = {'name': current_user.name}
    user = db.session.query(Users).filter_by(**kwargs).first()
    if request.method == 'POST':
        result = update_email(app, db, request.form)
    return render_template('settings_update_admin.html', email = user.email)


@app.route('/settings/reset_admin', methods = ['GET', 'POST'])
@login_required
def settings_reset_admin():
    if request.method != 'POST':
        result = update_password(app, db, request.form)
    return render_template('settings_reset_admin.html')


@app.route('/login', methods = ['GET', 'POST']) 
def login(): 
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
        return redirect(url_for('index')) 


@app.route('/forgot', methods = ['GET', 'POST']) 
def forgot(): 
    if request.method == 'GET':
        return render_template('forgot-password.html')
    is_valid, email = send_email(app, db, request.form)
    if is_valid:
        flash('An email has been sent to <u>{}</u>'.format(email), 'success')
    else:
        flash('An error occurred while trying to send your new password by '
              'email, you might have been provided a wrong username or email.', 'error')
    return render_template('forgot-password.html')


@app.route('/logout') 
@login_required
def logout(): 
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
