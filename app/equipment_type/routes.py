from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db
from app.equipment_type.forms import EquipmentTypeForm, SearchForm
from app.models import Customer, EquipmentType
from app.equipment_type import bp


@bp.route('/equipment_type', methods=['GET', 'POST'])
@login_required
def index():
    pagination = []
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    if search_form.validate_on_submit():
        name = search_form.name.data
        if name != '':
            pagination = EquipmentType.query.filter_by(name=name) \
                .order_by(EquipmentType.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
        else:
            pagination = EquipmentType.query \
                .order_by(EquipmentType.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
    else:
        pagination = EquipmentType.query \
            .order_by(EquipmentType.created_at.desc()).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'],
            error_out=False)
    list = pagination.items
    return render_template('equipment_type/list.html',
                           list=list, pagination=pagination,
                           title="equipment", search_form=search_form)


@bp.route('/equipment_type/add', methods=['GET', 'POST'])
@login_required
def add():
    add = True
    form = EquipmentTypeForm()
    if form.validate_on_submit():
        equipementType = EquipmentType(name=form.name.data,
                                       description=form.description.data,
                                       created_at=datetime.utcnow(),
                                       created_by=current_user.id)
        db.session.add(equipementType)
        db.session.commit()
        flash(_('Data saved!'))
        return redirect(url_for('equipment_type.index'))
    return render_template('equipment_type/form.html', action="Add",
                           add=add, form=form,
                           title="Add equipment_type")


@bp.route('/equipment_type/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    add = False
    equipementType = EquipmentType.query.get_or_404(id)
    form = EquipmentTypeForm(obj=equipementType)
    if form.validate_on_submit():
        equipementType.name = form.name.data
        equipementType.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the equipment_type.')

        # redirect to the bps page
        return redirect(url_for('equipment_type.index'))

    form.name.data = equipementType.name
    return render_template('equipment_type/form.html', action="Edit",
                           add=add, form=form,
                           equipementType=equipementType, title="Edit equipment_type")


@bp.route('/equipment_type/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    equipementType = EquipmentType.query.get_or_404(id)
    return render_template('equipment_type/detail.html', equipementType=equipementType)


@bp.route('/equipment_type/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    equipementType = EquipmentType.query.get_or_404(id)
    db.session.delete(equipementType)
    db.session.commit()
    flash('You have successfully deleted the equipment_type.')

    # redirect to the bps page
    return redirect(url_for('equipment_type.index'))
