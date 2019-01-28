from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db
from app.room.forms import RoomForm, SearchForm
from app.models import Customer, Room
from app.room import bp


@bp.route('/room', methods=['GET', 'POST'])
@login_required
def index():
    pagination = []
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    if search_form.validate_on_submit():
        name = search_form.name.data
        if name != '':
            pagination = Room.query.filter_by(name=name) \
                .order_by(Room.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
        else:
            pagination = Room.query \
                .order_by(Room.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
    else:
        pagination = Room.query \
            .order_by(Room.created_at.desc()).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'],
            error_out=False)
    list = pagination.items
    return render_template('room/list.html',
                           list=list, pagination=pagination,
                           title="salles", search_form=search_form)


@bp.route('/room/add', methods=['GET', 'POST'])
@login_required
def add():
    add = True
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(name=form.name.data,
                    created_at=datetime.utcnow(),
                    created_by=current_user.id)
        db.session.add(room)
        db.session.commit()
        flash(_('Data saved!'))
        return redirect(url_for('room.index'))
    return render_template('room/form.html', action="Add",
                           add=add, form=form,
                           title="Add room")


@bp.route('/room/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    add = False
    room = Room.query.get_or_404(id)
    form = RoomForm(obj=room)
    if form.validate_on_submit():
        room.name = form.name.data
        db.session.commit()
        flash('You have successfully edited the room.')

        # redirect to the bps page
        return redirect(url_for('room.index'))

    form.name.data = room.name
    return render_template('room/form.html', action="Edit",
                           add=add, form=form,
                           room=room, title="Edit room")


@bp.route('/room/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    room = Room.query.get_or_404(id)
    return render_template('room/detail.html', room=room)


@bp.route('/room/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    room = Room.query.get_or_404(id)
    db.session.delete(room)
    db.session.commit()
    flash('You have successfully deleted the room.')

    # redirect to the bps page
    return redirect(url_for('room.index'))
