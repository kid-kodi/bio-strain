from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db
from app.box_type.forms import BoxTypeForm, SearchForm
from app.models import BoxType
from app.box_type import bp


@bp.route('/box_type', methods=['GET', 'POST'])
@login_required
def index():
    list = []
    search_form = SearchForm()
    if search_form.validate_on_submit():
        name = search_form.name.data
        if name != '':
            list = BoxType.query.filter_by(name=name).all()
        else:
            list = BoxType.query.all()
    else:
        list = BoxType.query.all()
    return render_template('box_type/list.html',
                           list=list, title="Type de boite", search_form=search_form)


@bp.route('/box_type/add', methods=['GET', 'POST'])
@login_required
def add():
    add = True
    form = BoxTypeForm()
    if form.validate_on_submit():
        box_type = BoxType(name=form.name.data,
                          max_number=form.max_number.data,
                          description=form.description.data,
                          created_at=datetime.utcnow(),
                          created_by=current_user.id)
        db.session.add(box_type)
        db.session.commit()
        flash(_('Data saved!'))
        return redirect(url_for('box_type.index'))
    return render_template('box_type/form.html', action="Add",
                           add=add, form=form,
                           title="Add box_type")


@bp.route('/box_type/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    add = False
    box_type = BoxType.query.get_or_404(id)
    form = BoxTypeForm(obj=box_type)
    if form.validate_on_submit():
        box_type.name = form.name.data
        box_type.max_number = form.max_number.data
        box_type.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the box_type.')

        # redirect to the bps page
        return redirect(url_for('box_type.index'))

    form.name.data = box_type.name
    form.max_number.data = box_type.max_number
    form.description.data = box_type.description
    return render_template('box_type/form.html', action="Edit",
                           add=add, form=form,
                           box_type=box_type, title="Edit box_type")


@bp.route('/box_type/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    box_type = BoxType.query.get_or_404(id)
    return render_template('box_type/detail.html', box_type=box_type)


@bp.route('/box_type/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    box_type = BoxType.query.get_or_404(id)
    db.session.delete(box_type)
    db.session.commit()
    flash('You have successfully deleted the box_type.')

    # redirect to the bps page
    return redirect(url_for('box_type.index'))
