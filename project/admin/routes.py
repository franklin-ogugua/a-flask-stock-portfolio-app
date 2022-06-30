import click
from . import admin_blueprint
from project import database
from project.models import User, Stock, WatchStock
from flask import render_template, current_app, abort, flash, redirect, url_for, request
from flask_login import login_required, current_user
from .forms import PasswordForm, EmailForm


######################
#### cli commands ####
######################

@admin_blueprint.cli.command('create_admin_user')
@click.argument('email')
@click.argument('password')
def create(email, password):
    """Create a new admin user and add it to the database."""
    admin_user = User(email, password, user_type='Admin')
    database.session.add(admin_user)
    database.session.commit()
    click.echo(f'Created new admin user ({email})!')


###########################
#### request callbacks ####
###########################

@admin_blueprint.before_request
@login_required
def admin_before_request():
    if current_user.user_type != 'Admin':
        current_app.logger.info(
            f'User {current_user.id} attempted to access an ADMIN page ({request.url}, {request.method})!')
        abort(403)


################
#### routes ####
################

@admin_blueprint.route('/users')
def admin_list_users():
    users = User.query.order_by(User.id).all()
    for user in users:
        user.number_of_stocks_in_portfolio = len(Stock.query.filter_by(user_id=user.id).all())
        user.number_of_stocks_in_watchlist = len(WatchStock.query.filter_by(user_id=user.id).all())
    return render_template('admin/users.html', users=users)


@admin_blueprint.route('/users/<id>/delete')
def admin_delete_user(id):
    user = User.query.filter_by(id=id).first_or_404()

    if user.user_type == 'Admin':
        flash(f'Error! Admin user ({id}) cannot be deleted!', 'error')
    else:
        database.session.delete(user)
        database.session.commit()
        flash(f'User ({user.id}: {user.email}) was deleted!', 'success')
        current_app.logger.info(
            f'User ({user.id}: {user.email}) was deleted by admin user: {current_user.id}!')

    return redirect(url_for('admin.admin_list_users'))


@admin_blueprint.route('/users/<id>/confirm_email')
def admin_confirm_email_address(id):
    user = User.query.filter_by(id=id).first_or_404()
    user.confirm_email_address()
    database.session.add(user)
    database.session.commit()
    flash(f"User's email address ({user.id}: {user.email}) was confirmed!", 'success')
    current_app.logger.info(
        f"User's email address ({user.id}: {user.email}) was confirmed by admin user: {current_user.id}!")
    return redirect(url_for('admin.admin_list_users'))


@admin_blueprint.route('/users/<id>/unconfirm_email')
def admin_unconfirm_email_address(id):
    user = User.query.filter_by(id=id).first_or_404()
    user.unconfirm_email_address()
    database.session.add(user)
    database.session.commit()
    flash(f"User's email address ({user.id}: {user.email}) was un-confirmed!", 'success')
    current_app.logger.info(
        f"User's email address ({user.id}: {user.email}) was un-confirmed by admin user: {current_user.id}!")
    return redirect(url_for('admin.admin_list_users'))


@admin_blueprint.route('/users/<id>/change_password', methods=['GET', 'POST'])
def admin_change_password(id):
    user = User.query.filter_by(id=id).first_or_404()
    form = PasswordForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        database.session.add(current_user)
        database.session.commit()
        flash(f"User's password ({user.id}: {user.email}) was updated!", 'success')
        current_app.logger.info(
            f"User's password ({user.id}: {user.email}) was updated by admin user: {current_user.id}!")
        return redirect(url_for('admin.admin_list_users'))

    return render_template('admin/change_password.html', form=form)


@admin_blueprint.route('/users/<id>/change_email', methods=['GET', 'POST'])
def admin_change_email(id):
    user = User.query.filter_by(id=id).first_or_404()
    form = EmailForm()

    if form.validate_on_submit():
        user.email = form.email.data
        database.session.add(current_user)
        database.session.commit()
        flash(f"User's email ({user.id}: {user.email}) was updated!", 'success')
        current_app.logger.info(
            f"User's email ({user.id}: {user.email}) was updated by admin user: {current_user.id}!")
        return redirect(url_for('admin.admin_list_users'))

    return render_template('admin/change_email.html', form=form)
