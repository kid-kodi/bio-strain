# app/frame/views.py

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import bp
from .forms import FrameForm
from .. import db
from ..models import Frame

# Frame Views

@bp.route('/frame', methods=['GET', 'POST'])
@login_required
def list():
    """
    List all frame
    """

    list = Frame.query.all()

    return render_template('frame/list.html',
                           list=list, title="Frame")

@bp.route('/frame/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Add a frame to the database
    """

    add = True

    form = FrameForm()
    if form.validate_on_submit():
        frame = Frame(name=form.name.data,
                                description=form.description.data)
        try:
            # add frame to the database
            db.session.add(frame)
            db.session.commit()
            flash('You have successfully added a new frame.')
        except:
            # in case frame name already exists
            flash('Error: frame name already exists.')

        # redirect to frame page
        return redirect(url_for('frame.list'))

    # load frame template
    return render_template('frame/form.html', action="Add",
                           add=add, form=form,
                           title="Add Frame")

@bp.route('/frame/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit a frame
    """

    add = False

    frame = Frame.query.get_or_404(id)
    form = FrameForm(obj=frame)
    if form.validate_on_submit():
        frame.name = form.name.data
        frame.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the frame.')

        # redirect to the frame page
        return redirect(url_for('frame.list'))

    form.description.data = frame.description
    form.name.data = frame.name
    return render_template('frame/form.html', action="Edit",
                           add=add, form=form,
                           frame=frame, title="Edit Frame")

@bp.route('/frame/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    """
    Delete a frame from the database
    """

    frame = Frame.query.get_or_404(id)
    db.session.delete(frame)
    db.session.commit()
    flash('You have successfully deleted the frame.')

    # redirect to the frame page
    return redirect(url_for('frame.list'))