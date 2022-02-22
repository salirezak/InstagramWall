from flask import render_template, request, session, abort, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError

from app import db
from . import admin
from .forms import LoginForm, RegisterForm, ChangePasswordForm, EditAdminsForm, DeleteAccountForm, ConfirmDeleteAccountForm
from .models import Admin
from .utils import root_view, admin_view, viewer_view, banned_view



@admin.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if session.get('adminID'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        if not form.validate_on_submit(): abort(400)

        admin = Admin.query.filter(Admin.username.ilike(form.username.data)).first()
        flag = True

        if admin and admin.role_name() == 'banned':
            flag = False
            flash('You are banned', 'secondary')
            return render_template('admin/login.html', form=form), 403
        if not admin or not admin.check_password(form.password.data):
            flag = False
            flash('Incorrect username or password', 'secondary')

        if flag:
            session['adminID'] = admin.id
            return redirect(url_for('admin.dashboard'))

    return render_template('admin/login.html', form=form)


@admin.route('/logout/')
@banned_view
def logout():
    del session['adminID']
    return redirect(url_for('admin.login'))


@admin.route('/register-admin/', methods=['GET', 'POST'])
@root_view
def register_admin():
    admin = Admin.query.get(session.get('adminID'))
    form = RegisterForm(request.form)

    if request.method == 'POST':
        if not form.validate_on_submit(): abort(400)

        new_admin = Admin.query.filter(Admin.username.ilike(form.new_username.data)).first()
        flag = True

        if not admin or not admin.check_password(form.current_password.data):
            flag = False
            flash('Incorrect password', 'secondary')
        if form.new_password.data != form.confirm_password.data:
            flag = False
            flash('Different passwords', 'secondary')
        if new_admin:
            flag = False
            flash(f'{new_admin.username} is taken.', 'secondary')

        if flag:
            new_admin = Admin()
            new_admin.username = form.new_username.data
            new_admin.role = form.role.data
            new_admin.set_password(form.new_password.data)

            try:
                db.session.add(new_admin)
                db.session.commit()
                flash(f'{new_admin.username} added.', 'tertiary')
            except IntegrityError:
                db.session.rollback()
                flash(f'{new_admin.username} is taken.', 'secondary')


    return render_template('admin/register_admin.html', form=form, admin=(admin.username, admin.role_name()))


@admin.route('/change-password/', methods=['GET', 'POST'])
@viewer_view
def change_password():
    admin = Admin.query.get(session.get('adminID'))
    form = ChangePasswordForm(request.form)

    if request.method == 'POST':
        if not form.validate_on_submit(): abort(400)

        flag = True

        if not admin or not admin.check_password(form.current_password.data):
            flag = False
            flash('Incorrect current password', 'secondary')
        if admin.check_password(form.new_password.data):
            flag = False
            flash('Same new and current password', 'secondary')
        if form.new_password.data != form.confirm_password.data:
            flag = False
            flash('Different passwords', 'secondary')

        if flag:
            admin.set_password(form.new_password.data)
            db.session.commit()
            flash(f'Password changed.', 'tertiary')

    return render_template('admin/change_password.html', form=form, admin=(admin.username, admin.role_name()))


@admin.route('/edit-admins/', methods=['GET', 'POST'])
@root_view
def edit_admins():
    admin = Admin.query.get(session.get('adminID'))
    form = EditAdminsForm(request.form)
    print(form.errors, form.form_errors)
    admins_list, admins_table = get_admins_list_table(admin)
    form.admins_list.choices = admins_list

    selected_admins = [Admin.query.get(id) for id in form.admins_list.data]
    flag = True

    if request.method == 'POST':
        if not form.validate_on_submit(): abort(400)

        if not admin or not admin.check_password(form.current_password.data):
            flash('Incorrect password', 'secondary')
            flag = False

        if flag:
            for selected_admin in selected_admins:
                if form.action.data == 'delete':
                    db.session.delete(selected_admin)
                    db.session.commit()
                    flash(f'{selected_admin.username} deleted.', 'tertiary')
                else:
                    selected_admin.role = form.action.data
                    db.session.commit()
                    flash(f'{selected_admin.username} edited to {form.action.data}.', 'tertiary')

            admins_list, admins_table = get_admins_list_table(admin)
            form.admins_list.choices = admins_list

    if len(admins_list) == 0: size_admins = 1
    elif len(admins_list) < 4: size_admins = len(admins_list)
    else: size_admins = 4

    return render_template('admin/edit_admins.html', form=form, size_admins=size_admins, admin=(admin.username, admin.role_name()), admins_table=admins_table)

def get_admins_list_table(admin):
    admins_list = Admin.query.order_by(Admin.role).all()
    admins_table = admins_list.copy()
    admins_list.remove(admin)
    admins_list = [(x.id, f"{x.username}={x.role_name()}") for x in admins_list]

    return admins_list, admins_table

@admin.route('/delete-account/', methods=['GET', 'POST'])
@viewer_view
def delete_account():
    admin = Admin.query.get(session.get('adminID'))
    forms = (DeleteAccountForm(request.form), ConfirmDeleteAccountForm(request.form))

    admins_list = Admin.query.filter(Admin.role.ilike('root')).all()
    if len(admins_list) == 1 and admins_list[0] == admin:
        session['deleteAccountStage'] = 'error'
    stage = session.get('deleteAccountStage')

    if not session.get('deleteAccountStage'):
        if request.method == 'POST':
            if not forms[0].validate_on_submit(): abort(400)

            flag = True

            if not admin or not admin.check_password(forms[0].password.data) or not admin.check_password(forms[0].confirm_password.data):
                flag = False
                flash('Incorrect password', 'secondary')
            if forms[0].password.data != forms[0].confirm_password.data:
                flag = False
                flash('Different passwords', 'secondary')

            if flag:
                session['deleteAccountStage'] = 'confirm'

    elif session.get('deleteAccountStage') == 'confirm':
        del session['deleteAccountStage']
        if request.method == 'POST':
            if not forms[1].validate_on_submit(): abort(400)

            flag = True

            if admin.username != forms[1].username.data:
                flag = False
                flash('Incorrect username', 'secondary')

            if flag:
                db.session.delete(admin)
                db.session.commit()
                del session['adminID']
                flash(f'{forms[1].username.data} deleted.', 'tertiary')
                return redirect(url_for('admin.login'))

    elif session.get('deleteAccountStage') == 'error':
        del session['deleteAccountStage']
        return render_template('admin/delete_account.html', forms=forms, stage='error', admin=(admin.username, admin.role_name()))

    stage = session.get('deleteAccountStage')
    return render_template('admin/delete_account.html', forms=forms, stage=stage, admin=(admin.username, admin.role_name()))