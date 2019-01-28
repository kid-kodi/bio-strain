# app/sample_type/views.py

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import bp
from .forms import SampleTypeForm
from .. import db
from ..models import SampleType


# SampleType Views

@bp.route('/sample_type', methods=['GET', 'POST'])
@login_required
def list():
    """
    List all sample_type
    """

    list = SampleType.query.all()

    return render_template('sample_type/list.html',
                           list=list, title="SampleTypes")


@bp.route('/sample_type/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Add a sample_type to the database
    """

    add = True

    form = SampleTypeForm()
    if form.validate_on_submit():
        sample_type = SampleType(name=form.name.data,
                                 description=form.description.data)
        try:
            # add sample_type to the database
            db.session.add(sample_type)
            db.session.commit()
            flash('You have successfully added a new sample_type.')
        except:
            # in case sample_type name already exists
            flash('Error: sample_type name already exists.')

        # redirect to sample_type page
        return redirect(url_for('sample_type.list'))

    # load sample_type template
    return render_template('sample_type/form.html', action="Add",
                           add=add, form=form,
                           title="Add SampleType")


@bp.route('/sample_type/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit a sample_type
    """

    add = False

    sample_type = SampleType.query.get_or_404(id)
    form = SampleTypeForm(obj=sample_type)
    if form.validate_on_submit():
        sample_type.name = form.name.data
        sample_type.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the sample_type.')

        # redirect to the sample_type page
        return redirect(url_for('sample_type.list'))

    form.description.data = sample_type.description
    form.name.data = sample_type.name
    return render_template('sample_type/form.html', action="Edit",
                           add=add, form=form,
                           sample_type=sample_type, title="Edit SampleType")


@bp.route('/sample_type/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    """
    Delete a sample_type from the database
    """

    sample_type = SampleType.query.get_or_404(id)
    db.session.delete(sample_type)
    db.session.commit()
    flash('You have successfully deleted the sample_type.')

    # redirect to the sample_type page
    return redirect(url_for('sample_type.list'))
