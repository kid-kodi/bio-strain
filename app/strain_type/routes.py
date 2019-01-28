# app/strain_type/views.py

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import bp
from .forms import StrainTypeForm
from .. import db
from ..models import StrainType


# StrainType Views

@bp.route('/strain_type', methods=['GET', 'POST'])
@login_required
def list():
    """
    List all strain_type
    """

    list = StrainType.query.all()

    return render_template('strain_type/list.html',
                           list=list, title="StrainTypes")


@bp.route('/strain_type/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Add a strain_type to the database
    """

    add = True

    form = StrainTypeForm()
    if form.validate_on_submit():
        strain_type = StrainType(name=form.name.data,
                                 description=form.description.data)
        try:
            # add strain_type to the database
            db.session.add(strain_type)
            db.session.commit()
            flash('You have successfully added a new strain_type.')
        except:
            # in case strain_type name already exists
            flash('Error: strain_type name already exists.')

        # redirect to strain_type page
        return redirect(url_for('strain_type.list'))

    # load strain_type template
    return render_template('strain_type/form.html', action="Add",
                           add=add, form=form,
                           title="Add StrainType")


@bp.route('/strain_type/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit a strain_type
    """

    add = False

    strain_type = StrainType.query.get_or_404(id)
    form = StrainTypeForm(obj=strain_type)
    if form.validate_on_submit():
        strain_type.name = form.name.data
        strain_type.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the strain_type.')

        # redirect to the strain_type page
        return redirect(url_for('strain_type.list'))

    form.description.data = strain_type.description
    form.name.data = strain_type.name
    return render_template('strain_type/form.html', action="Edit",
                           add=add, form=form,
                           strain_type=strain_type, title="Edit StrainType")


@bp.route('/strain_type/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    """
    Delete a strain_type from the database
    """

    strain_type = StrainType.query.get_or_404(id)
    db.session.delete(strain_type)
    db.session.commit()
    flash('You have successfully deleted the strain_type.')

    # redirect to the strain_type page
    return redirect(url_for('strain_type.list'))
