from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db
from app.box.forms import BoxForm, SearchForm
from app.models import Box, BoxType, Rack, Hole
from app.box import bp


@bp.route('/box', methods=['GET', 'POST'])
@login_required
def index():
    list = []
    search_form = SearchForm()
    if search_form.validate_on_submit():
        name = search_form.name.data
        if name != '':
            list = Box.query.filter_by(name=name).all()
        else:
            list = Box.query.all()
    else:
        list = Box.query.all()
    return render_template('box/list.html',
                           list=list, title="boxs", search_form=search_form)


@bp.route('/box/add', methods=['GET', 'POST'])
@login_required
def add():
    add = True
    form = BoxForm()
    form.rack.choices = [(c.id, c.name) for c in Rack.query.all()]
    form.box_type.choices = [(c.id, c.name) for c in BoxType.query.all()]
    if form.validate_on_submit():
        box = Box(name=form.name.data,
                  rack_id=form.rack.data,
                  horizontal=form.horizontal.data,
                  vertical=form.vertical.data,
                  status=0,
                  box_type_id=form.box_type.data,
                  created_at=datetime.utcnow(),
                  created_by=current_user.id)
        db.session.add(box)
        db.session.commit()

        for max in range(box.box_type.max_number):
            print(max)
            hole = Hole(box_id=box.id,
                        name=max + 1,
                        status=0,
                        created_at=datetime.utcnow(),
                        created_by=current_user.id)
            db.session.add(hole)
            db.session.commit()

        flash(_('Boite crée avec sucess!'))
        return redirect(url_for('box.index'))
    return render_template('box/form.html', action="Add",
                           add=add, form=form,
                           title="Add box")


@bp.route('/box/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    add = False
    box = Box.query.get_or_404(id)
    form = BoxForm(obj=box)
    form.rack.choices = [(c.id, c.name) for c in Rack.query.all()]
    form.box_type.choices = [(c.id, c.name) for c in BoxType.query.all()]
    if form.validate_on_submit():
        box.name = form.name.data
        box.rack_id = form.rack.data
        box.horizontal = form.horizontal.data
        box.vertical = form.vertical.data
        db.session.commit()
        flash('You have successfully edited the box.')

        # redirect to the bps page
        return redirect(url_for('box.index'))

    form.name.data = box.name
    form.rack.data = box.rack_id
    form.box_type.data = box.box_type_id
    return render_template('box/form.html', action="Edit",
                           add=add, form=form,
                           box=box, title="Edit box")


@bp.route('/box/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    box = Box.query.get_or_404(id)
    return render_template('box/detail.html', box=box)


@bp.route('/box/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    box = Box.query.get_or_404(id)
    db.session.delete(box)
    db.session.commit()
    flash('You have successfully deleted the box.')

    # redirect to the bps page
    return redirect(url_for('box.index'))
