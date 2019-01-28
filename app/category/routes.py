# app/category/views.py

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import bp
from .forms import CategoryForm
from .. import db
from ..models import Category


# Category Views

@bp.route('/category', methods=['GET', 'POST'])
@login_required
def list():
    """
    List all category
    """

    list = Category.query.all()

    return render_template('category/list.html',
                           list=list, title="Category")


@bp.route('/category/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Add a category to the database
    """

    add = True

    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data,
                            description=form.description.data)
        try:
            # add category to the database
            db.session.add(category)
            db.session.commit()
            flash('You have successfully added a new category.')
        except:
            # in case category name already exists
            flash('Error: category name already exists.')

        # redirect to category page
        return redirect(url_for('category.list'))

    # load category template
    return render_template('category/form.html', action="Add",
                           add=add, form=form,
                           title="Add Category")


@bp.route('/category/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit a category
    """

    add = False

    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the category.')

        # redirect to the category page
        return redirect(url_for('category.list'))

    form.description.data = category.description
    form.name.data = category.name
    return render_template('category/form.html', action="Edit",
                           add=add, form=form,
                           category=category, title="Edit Category")


@bp.route('/category/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    """
    Delete a category from the database
    """

    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('You have successfully deleted the category.')

    # redirect to the category page
    return redirect(url_for('category.list'))
