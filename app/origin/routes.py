# app/origin/views.py

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import bp
from .forms import OriginForm
from .. import db
from ..models import Origin


# Origin Views

@bp.route('/origin', methods=['GET', 'POST'])
@login_required
def list():
    """
    List all origin
    """

    list = Origin.query.all()

    return render_template('origin/list.html',
                           list=list, title="Origin")


@bp.route('/origin/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Add a origin to the database
    """

    add = True

    form = OriginForm()
    if form.validate_on_submit():
        origin = Origin(name=form.name.data,
                        description=form.description.data)
        try:
            # add origin to the database
            db.session.add(origin)
            db.session.commit()
            flash('You have successfully added a new origin.')
        except:
            # in case origin name already exists
            flash('Error: origin name already exists.')

        # redirect to origin page
        return redirect(url_for('origin.list'))

    # load origin template
    return render_template('origin/form.html', action="Add",
                           add=add, form=form,
                           title="Add Origin")


@bp.route('/origin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit a origin
    """

    add = False

    origin = Origin.query.get_or_404(id)
    form = OriginForm(obj=origin)
    if form.validate_on_submit():
        origin.name = form.name.data
        origin.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the origin.')

        # redirect to the origin page
        return redirect(url_for('origin.list'))

    form.description.data = origin.description
    form.name.data = origin.name
    return render_template('origin/form.html', action="Edit",
                           add=add, form=form,
                           origin=origin, title="Edit Origin")


@bp.route('/origin/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    """
    Delete a origin from the database
    """

    origin = Origin.query.get_or_404(id)
    db.session.delete(origin)
    db.session.commit()
    flash('You have successfully deleted the origin.')

    # redirect to the origin page
    return redirect(url_for('origin.list'))
