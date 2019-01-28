# app/phenotype/views.py

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import bp
from .forms import PhenotypeForm
from .. import db
from ..models import Phenotype


# Phenotype Views

@bp.route('/phenotype', methods=['GET', 'POST'])
@login_required
def list():
    """
    List all phenotype
    """

    list = Phenotype.query.all()

    return render_template('phenotype/list.html',
                           list=list, title="Phenotypes")


@bp.route('/phenotype/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Add a phenotype to the database
    """

    add = True

    form = PhenotypeForm()
    if form.validate_on_submit():
        phenotype = Phenotype(name=form.name.data,
                                 description=form.description.data)
        try:
            # add phenotype to the database
            db.session.add(phenotype)
            db.session.commit()
            flash('You have successfully added a new phenotype.')
        except:
            # in case phenotype name already exists
            flash('Error: phenotype name already exists.')

        # redirect to phenotype page
        return redirect(url_for('phenotype.list'))

    # load phenotype template
    return render_template('phenotype/form.html', action="Add",
                           add=add, form=form,
                           title="Add Phenotype")


@bp.route('/phenotype/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit a phenotype
    """

    add = False

    phenotype = Phenotype.query.get_or_404(id)
    form = PhenotypeForm(obj=phenotype)
    if form.validate_on_submit():
        phenotype.name = form.name.data
        phenotype.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the phenotype.')

        # redirect to the phenotype page
        return redirect(url_for('phenotype.list'))

    form.description.data = phenotype.description
    form.name.data = phenotype.name
    return render_template('phenotype/form.html', action="Edit",
                           add=add, form=form,
                           phenotype=phenotype, title="Edit Phenotype")


@bp.route('/phenotype/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    """
    Delete a phenotype from the database
    """

    phenotype = Phenotype.query.get_or_404(id)
    db.session.delete(phenotype)
    db.session.commit()
    flash('You have successfully deleted the phenotype.')

    # redirect to the phenotype page
    return redirect(url_for('phenotype.list'))
