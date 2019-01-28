from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db
from app.rack.forms import RackForm, SearchForm
from app.models import Rack, Equipment
from app.rack import bp


@bp.route('/rack', methods=['GET', 'POST'])
@login_required
def index():
    pagination = []
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    if search_form.validate_on_submit():
        name = search_form.name.data
        if name != '':
            pagination = Rack.query.filter_by(name=name) \
                .order_by(Rack.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
        else:
            pagination = Rack.query \
                .order_by(Rack.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
    else:
        pagination = Rack.query \
            .order_by(Rack.created_at.desc()).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'],
            error_out=False)
    list = pagination.items
    return render_template('rack/list.html',
                           list=list, pagination=pagination,
                           title="equipment", search_form=search_form)


@bp.route('/rack/add', methods=['GET', 'POST'])
@login_required
def add():
    add = True
    form = RackForm()
    form.equipment.choices = [(c.id, c.name) for c in Equipment.query.all()]
    if form.validate_on_submit():
        rack = Rack(name=form.name.data,
                    equipment_id=form.equipment.data,
                    horizontal=form.horizontal.data,
                    vertical=form.vertical.data,
                    max_number=int(form.vertical.data) + int(form.horizontal.data),
                    status=0,
                    created_at=datetime.utcnow(),
                    created_by=current_user.id)
        db.session.add(rack)
        db.session.commit()
        flash(_('Data saved!'))
        return redirect(url_for('rack.index'))
    return render_template('rack/form.html', action="Add",
                           add=add, form=form,
                           title="Add rack")


@bp.route('/rack/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    add = False
    rack = Rack.query.get_or_404(id)
    form = RackForm(obj=rack)
    form.equipment.choices = [(c.id, c.name) for c in Equipment.query.all()]
    if form.validate_on_submit():
        rack.equipment_id = form.equipment.data
        rack.max_number = form.max_number.data
        rack.name = form.name.data
        db.session.commit()
        flash('You have successfully edited the rack.')

        # redirect to the bps page
        return redirect(url_for('rack.index'))

    form.equipment.data = rack.equipment_id
    form.max_number.data = rack.max_number
    form.name.data = rack.name
    return render_template('rack/form.html', action="Edit",
                           add=add, form=form,
                           rack=rack, title="Edit rack")


@bp.route('/rack/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    rack = Rack.query.get_or_404(id)
    return render_template('rack/detail.html', rack=rack)


@bp.route('/rack/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    rack = Rack.query.get_or_404(id)
    db.session.delete(rack)
    db.session.commit()
    flash('You have successfully deleted the rack.')

    # redirect to the bps page
    return redirect(url_for('rack.index'))
