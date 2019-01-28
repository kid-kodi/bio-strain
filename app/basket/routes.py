from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.basket.forms import BasketForm, SearchForm
from app.models import Customer, Basket, Strain
from app.basket import bp


# @bp.route('/basket', methods=['GET', 'POST'])
# @login_required
# def index():
#     pagination = []
#     search_form = SearchForm()
#     page = request.args.get('page', 1, type=int)
#     if search_form.validate_on_submit():
#         name = search_form.name.data
#         if name != '':
#             pagination = Basket.query.filter_by(name=name) \
#                 .order_by(Basket.created_at.desc()).paginate(
#                 page, per_page=current_app.config['FLASK_PER_PAGE'],
#                 error_out=False)
#         else:
#             pagination = Basket.query \
#                 .order_by(Basket.created_at.desc()).paginate(
#                 page, per_page=current_app.config['FLASK_PER_PAGE'],
#                 error_out=False)
#     else:
#         pagination = Basket.query \
#             .order_by(Basket.created_at.desc()).paginate(
#             page, per_page=current_app.config['FLASK_PER_PAGE'],
#             error_out=False)
#     list = pagination.items
#     return render_template('basket/index.html',
#                            list=list, pagination=pagination,
#                            title="salles", search_form=search_form)


@bp.route('/basket', methods=['GET', 'POST'])
@login_required
def index():
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    return render_template('basket/detail.html', basket=basket)


@bp.route('/basket/add', methods=['GET', 'POST'])
@login_required
def add():
    add = True
    form = BasketForm()
    if form.validate_on_submit():
        basket = Basket(name=form.name.data,
                        created_at=datetime.utcnow(),
                        created_by=current_user.id)
        db.session.add(basket)
        db.session.commit()
        flash(_('Data saved!'))
        return redirect(url_for('basket.index'))
    return render_template('basket/form.html', action="Add",
                           add=add, form=form,
                           title="Add basket")


@bp.route('/basket/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    add = False
    basket = Basket.query.get_or_404(id)
    form = BasketForm(obj=basket)
    if form.validate_on_submit():
        basket.name = form.name.data
        db.session.commit()
        flash('You have successfully edited the basket.')

        # redirect to the bps page
        return redirect(url_for('basket.index'))

    form.name.data = basket.name
    return render_template('basket/form.html', action="Edit",
                           add=add, form=form,
                           basket=basket, title="Edit basket")


@bp.route('/basket/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    basket = Basket.query.get_or_404(id)
    return render_template('basket/detail.html', basket=basket)


@bp.route('/basket/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    basket = Basket.query.get_or_404(id)
    db.session.delete(basket)
    db.session.commit()
    flash('You have successfully deleted the basket.')

    # redirect to the bps page
    return redirect(url_for('basket.index'))


@bp.route('/basket/remove_all', methods=['GET'])
@login_required
def remove_all():
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    for strain in basket.strains:
        basket.strains.remove(strain)
        strain.basket_id = 0
        db.session.commit()
    return redirect(url_for('basket.index'))


@bp.route('/basket/removefromlist/<int:id>', methods=['GET'])
@login_required
def removefromlist(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    strain = Strain.query.get(id)
    basket.strains.remove(strain)
    strain.basket_id = 0
    db.session.commit()
    return redirect(url_for('basket.index'))
