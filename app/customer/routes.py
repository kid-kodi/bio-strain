from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db, excel
from app.customer.forms import CustomerForm
from app.models import Customer, Category
from app.customer import bp


@bp.route('/customer', methods=['GET', 'POST'])
@login_required
def index():
    customers = Customer.query.all()
    return render_template('customer/index.html', customers=customers)


@bp.route('/customer/add', methods=['GET', 'POST'])
@login_required
def add():
    form = CustomerForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        customer = Customer(category_id=form.category.data, display_as=form.display_as.data,
                            first_name=form.first_name.data, last_name=form.last_name.data,
                            address=form.address.data, telephone=form.telephone.data,
                            email=form.email.data)
        db.session.add(customer)
        db.session.commit()
        flash(_('Nouveau Client ajouté avec succèss!'))
        return redirect(url_for('customer.index', customer_id=customer.id))
    return render_template('customer/form.html', form=form)


@bp.route('/customer/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    customer = Customer.query.get(id)
    form = CustomerForm()

    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        customer.category_id = form.category.data
        customer.display_as = form.display_as.data
        customer.first_name = form.first_name.data
        customer.last_name = form.last_name.data
        customer.address = form.address.data
        customer.telephone = form.telephone.data
        customer.email = form.email.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('customer.detail', id=customer.id))

    form.category.data = customer.category_id
    form.display_as.data = customer.display_as
    form.first_name.data = customer.first_name
    form.last_name.data = customer.last_name
    form.address.data = customer.address
    form.telephone.data = customer.telephone
    form.email.data = customer.email
    return render_template('customer/form.html', form=form)


@bp.route('/customer/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    customer = Customer.query.get(id)
    return render_template('customer/detail.html', customer=customer)


@bp.route("/customer/export", methods=['GET'])
@login_required
def export_data():
    return excel.make_response_from_tables(db.session, [Customer], "xls", file_name="export_data")


@bp.route("/customer/import", methods=['GET', 'POST'])
@login_required
def import_data():
    if request.method == 'POST':
        def customer_init_func(row):
            c = Category.query.filter_by(name=row['category']).first()
            p = Customer(category=c, display_as=row['display_as'], first_name=row['first_name'],
                         last_name=row['last_name'], address=row['address'], telephone=row['telephone'],
                         email=row['email'])
            return p

        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[Customer],
            initializers=[customer_init_func])
        return redirect(url_for('.handson_table'), code=302)
    return render_template('customer/import.html')


@bp.route("/handson_view", methods=['GET'])
def handson_table():
    return excel.make_response_from_tables(
        db.session, [Customer], 'handsontable.html')


@bp.route("/customer/download", methods=['GET'])
@login_required
def download():
    query_sets = Customer.query.filter_by(id=1).all()
    column_names = ['category_id', 'display_as', 'first_name', 'last_name', 'address', 'telephone', 'email']
    return excel.make_response_from_query_sets(query_sets, column_names, "xls", file_name="template")
