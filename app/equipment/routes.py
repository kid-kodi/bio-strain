from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db
from app.equipment.forms import EquipmentForm, SearchForm
from app.models import Equipment, EquipmentType, Room
from app.equipment import bp


@bp.route('/equipment', methods=['GET', 'POST'])
@login_required
def index():
    pagination = []
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    if search_form.validate_on_submit():
        name = search_form.name.data
        if name != '':
            pagination = Equipment.query.filter_by(name=name) \
                .order_by(Equipment.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
        else:
            pagination = Equipment.query \
                .order_by(Equipment.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
    else:
        pagination = Equipment.query \
            .order_by(Equipment.created_at.desc()).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'],
            error_out=False)
    list = pagination.items
    return render_template('equipment/list.html',
                           list=list, pagination=pagination,
                           title="equipment", search_form=search_form)


@bp.route('/equipment/add', methods=['GET', 'POST'])
@login_required
def add():
    add = True
    form = EquipmentForm()
    form.equipment_type.choices = [(c.id, c.name) for c in EquipmentType.query.all()]
    form.room.choices = [(c.id, c.name) for c in Room.query.all()]
    if form.validate_on_submit():
        equipment = Equipment(name=form.name.data,
                              equipment_type_id=form.equipment_type.data,
                              horizontal=form.horizontal.data,
                              vertical=form.vertical.data,
                              max_number=int(form.vertical.data) + int(form.horizontal.data),
                              room_id=form.room.data,
                              status=0,
                              created_at=datetime.utcnow(),
                              created_by=current_user.id)
        db.session.add(equipment)
        db.session.commit()
        flash(_('Data saved!'))
        return redirect(url_for('equipment.index'))
    return render_template('equipment/form.html', action="Add",
                           add=add, form=form,
                           title="Add equipment")


@bp.route('/equipment/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    add = False
    equipment = Equipment.query.get_or_404(id)
    form = EquipmentForm(obj=equipment)
    form.equipment_type.choices = [(c.id, c.name) for c in EquipmentType.query.all()]
    form.room.choices = [(c.id, c.name) for c in Room.query.all()]
    if form.validate_on_submit():
        equipment.name = form.name.data
        equipment.max_number = form.max_number.data
        equipment.room_id = form.room.data
        equipment.equipment_type_id = form.equipment_type.data
        db.session.commit()
        flash('You have successfully edited the equipment.')

        # redirect to the bps page
        return redirect(url_for('equipment.index'))

    form.max_number.data = equipment.max_number
    form.room.data = equipment.room_id
    form.name.data = equipment.name
    form.equipment_type.data = equipment.equipment_type_id
    return render_template('equipment/form.html', action="Edit",
                           add=add, form=form,
                           equipment=equipment, title="Edit equipment")


@bp.route('/equipment/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    equipment = Equipment.query.get_or_404(id)
    return render_template('equipment/detail.html', equipment=equipment)


@bp.route('/equipment/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    equipment = Equipment.query.get_or_404(id)
    db.session.delete(equipment)
    db.session.commit()
    flash('You have successfully deleted the equipment.')

    # redirect to the bps page
    return redirect(url_for('equipment.index'))
