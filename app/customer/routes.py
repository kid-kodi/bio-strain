import os
import os
import xlrd
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
    return render_template('customer/index.html', customers=customers, title="Client")


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
    return render_template('customer/form.html', form=form, title="Client")


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
    return render_template('customer/form.html', form=form, title="Client")


@bp.route('/customer/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    customer = Customer.query.get(id)
    return render_template('customer/detail.html', customer=customer, title="Client")


@bp.route("/customer/export", methods=['GET'])
@login_required
def export_data():
    return excel.make_response_from_tables(db.session, [Customer], "xls", file_name="client")


@bp.route("/customer/import", methods=['GET', 'POST'])
@login_required
def import_data():
    if request.method == 'POST':
        # save the file with name and open url of this file
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('Aucun fichier selectionné')
            return redirect(url_for('customer.import_data'))
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('Aucun fichier selectionné')
            return redirect(url_for('customer.import_data'))

        def customer_init(row):
            c = Customer()
            c.display_as = row['Raison sociale']
            c.first_name = row['Nom']
            c.last_name = row['Prénoms']
            c.address = row['Adresse']
            c.telephone = row['Téléphone']
            c.email = row['Email']
            c.timestamp = datetime.utcnow()
            return c

        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[Customer],
            initializers=[customer_init])
        # Write file to static directory and do the hot dog check
        flash(_('Fichier charger avec success!'))
        return redirect(url_for('customer.index'))
    return render_template('customer/import.html', title="Client")


@bp.route("/customer/format/<filename>", methods=['GET', 'POST'])
@login_required
def format_data(filename):
    customer_row = [column.key for column in Customer.__table__.columns]
    header_row = []
    book = xlrd.open_workbook(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    for sheet in book.sheets():
        if sheet.name == 'DATA':
            data_sheet = book.sheet_by_name("DATA")
            header_row = data_sheet.row(0)

    if request.method == 'POST':
        data_sheet = book.sheet_by_name("DATA")
        for r in range(1, data_sheet.nrows):
            for c in customer_row:
                customer = Customer()
                customer[c] = r.cell(r, 6).value
                print(c + " # " + request.form[c])

        # Delete image when done with analysis
        # os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('customer.index'))
    return render_template('customer/format.html', title="Client", header_row=header_row, customer_row=customer_row)
