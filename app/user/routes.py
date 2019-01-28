# app/trainee/views.py

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import user
from .forms import userForm
from .. import db
from ..models import User

# user Views

@user.route('/users', methods=['GET', 'POST'])
@login_required
def list():
    """
    List all user
    """

    list = User.query.all()

    return render_template('user/list.html',
                           list=list, title="users")

@user.route('/users/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Add a user to the database
    """

    add = True

    form = userForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                username=form.username.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=form.password.data)
        try:
            # add user to the database
            db.session.add(user)
            db.session.commit()
            flash('You have successfully added a new user.')
        except:
            # in case user name already exists
            flash('Error: user name already exists.')

        # redirect to users page
        return redirect(url_for('user.list'))

    # load user template
    return render_template('user/form.html', action="Add",
                           add=add, form=form,
                           title="Add user")

@user.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit a user
    """

    add = False

    user = User.query.get_or_404(id)
    form = userForm(obj=user)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.password = form.password.data
        db.session.commit()
        flash('You have successfully edited the user.')

        # redirect to the trainees page
        return redirect(url_for('user.list'))

    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.email.data = user.email
    return render_template('user/form.html', action="Edit",
                           add=add, form=form,
                           user=user, title="Edit user")

@user.route('/users/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    """
    Delete a trainee from the database
    """

    user = user.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('You have successfully deleted the user.')

    # redirect to the trainees page
    return redirect(url_for('user.list'))