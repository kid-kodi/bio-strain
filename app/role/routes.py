# app/role/views.py

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import role
from .forms import RoleForm
from .. import db
from ..models import Role

# Role Views

@role.route('/roles', methods=['GET', 'POST'])
@login_required
def list():
    """
    List all roles
    """

    list = Role.query.all()

    return render_template('role/list.html',
                           list=list, title="Roles")

@role.route('/roles/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Add a role to the database
    """

    add = True

    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data,
                                description=form.description.data)
        try:
            # add role to the database
            db.session.add(role)
            db.session.commit()
            flash('You have successfully added a new role.')
        except:
            # in case role name already exists
            flash('Error: role name already exists.')

        # redirect to roles page
        return redirect(url_for('role.list'))

    # load role template
    return render_template('role/form.html', action="Add",
                           add=add, form=form,
                           title="Add Role")

@role.route('/roles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit a role
    """

    add = False

    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the role.')

        # redirect to the roles page
        return redirect(url_for('role.list'))

    form.description.data = role.description
    form.name.data = role.name
    return render_template('role/form.html', action="Edit",
                           add=add, form=form,
                           role=role, title="Edit Role")

@role.route('/roles/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    """
    Delete a role from the database
    """

    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('You have successfully deleted the role.')

    # redirect to the roles page
    return redirect(url_for('role.list'))