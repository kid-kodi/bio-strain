import os
import xlrd
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db, documents
from app.order.forms import OrderForm, ImportForm
from app.models import Order, Customer, Strain, Origin, StrainType, Frame, Phenotype, SampleType, Temperature, Basket
from app.order import bp

basedir = ''


@bp.route('/order', methods=['GET', 'POST'])
@login_required
def index():
    orders = Order.query.all()
    return render_template('order/index.html', orders=orders, Order=Order)


@bp.route('/order/download_file/<filename>')
def download_file(filename):
    return send_from_directory(current_app.config['UPLOADS_DEFAULT_DEST'], filename, as_attachment=True)


@bp.route('/order/add', methods=['GET', 'POST'])
@login_required
def add():
    form = OrderForm()
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.frame.choices = [(c.id, c.name) for c in Frame.query.all()]
    form.temperature.choices = [(c.id, c.name) for c in Temperature.query.all()]

    if form.validate_on_submit():
        order = Order()

        if 'file' in request.files:
            file = request.files['file']
            order.file_name = documents.save(file)
            order.file_url = documents.url(order.file_name)

        order.serial = get_order_code()
        order.frame_id = form.frame.data
        order.customer_id = form.customer.data
        order.first_name = form.first_name.data
        order.last_name = form.last_name.data
        order.telephone = form.telephone.data
        order.receive_date = form.receive_date.data
        order.send_date = form.send_date.data
        order.temperature_id = form.temperature.data
        order.nbr_pack = form.nbr_pack.data
        order.timestamp = datetime.utcnow()
        order.user_id = current_user.id
        order.status = 0
        db.session.add(order)
        db.session.commit()

        flash(_('Informations du dépôt enregistrées!'))
        return redirect(url_for('order.detail', id=order.id))

    return render_template('order/form.html', form=form)


@bp.route('/order/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    order = Order.query.get(id)
    return render_template('order/detail.html', order=order)


@bp.route('/order/validate/<int:id>', methods=['GET', 'POST'])
@login_required
def validate(id):
    order = Order.query.get(id)
    filename = order.file_name
    print(filename)
    # Write file to static directory and do the hot dog check
    book = xlrd.open_workbook(os.path.join(basedir, filename))
    for sheet in book.sheets():
        if sheet.name == 'DATA':
            data_sheet = book.sheet_by_name("DATA")
            # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
            for r in range(1, data_sheet.nrows):
                strain = Strain()
                strain.receive_date = str(
                    datetime(*xlrd.xldate_as_tuple(data_sheet.cell(r, 0).value, book.datemode)))
                strain.conservation_date = str(
                    datetime(*xlrd.xldate_as_tuple(data_sheet.cell(r, 1).value, book.datemode)))
                strain.customer = Customer.query.filter_by(display_as=data_sheet.cell(r, 2).value).first()
                strain.origin = Origin.query.filter_by(name=data_sheet.cell(r, 3).value).first()
                # strain.frame = Frame.query.filter_by(name=data_sheet.cell(r, 4).value).first()
                strain.strain_type = StrainType.query.filter_by(name=data_sheet.cell(r, 5).value).first()
                strain.identity = data_sheet.cell(r, 6).value
                strain.serial_number = str(data_sheet.cell(r, 7).value)
                strain.biobank_number = str(data_sheet.cell(r, 8).value)
                strain.sample_type = SampleType.query.filter_by(name=data_sheet.cell(r, 9).value).first()
                strain.phenotype = Phenotype.query.filter_by(name=data_sheet.cell(r, 10).value).first()
                strain.mutation_type = data_sheet.cell(r, 11).value
                strain.created_at = datetime.utcnow()
                strain.created_by = current_user.id
                db.session.add(strain)
                db.session.commit()

        order.status = 1
        db.session.commit()
        # and check sample id if already in db
    flash(_('Traitement effectué avec succes!'))
    return redirect(url_for('order.detail', id=order.id))


@bp.route('/order/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    order = Order.query.get(id)
    form = OrderForm(obj=order)
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.frame.choices = [(c.id, c.name) for c in Frame.query.all()]
    form.temperature.choices = [(c.id, c.name) for c in Temperature.query.all()]

    if form.validate_on_submit():

        if 'file' in request.files:
            file = request.files['file']
            order.file_name = documents.save(file)
            order.file_url = documents.url(order.file_name)

        order.customer_id = form.customer.data
        order.frame_id = form.frame.data
        order.first_name = form.first_name.data
        order.last_name = form.last_name.data
        order.telephone = form.telephone.data
        order.send_date = form.send_date.data
        order.temperature_id = form.temperature.data
        order.nbr_pack = form.nbr_pack.data
        db.session.commit()
        flash(_('Modification effectuée avec succèss!!'))
        return redirect(url_for('order.detail', id=order.id))
    form.customer.data = order.customer.id
    form.frame.data = order.frame.id
    form.first_name.data = order.first_name
    form.last_name.data = order.last_name
    form.telephone.data = order.telephone
    form.send_date.data = order.send_date
    form.receive_date.data = order.receive_date
    form.nbr_pack.data = order.nbr_pack
    form.temperature.data = order.temperature_id

    return render_template('order/form.html', form=form)


@bp.route('/order/process/<int:id>', methods=['GET', 'POST'])
@login_required
def process(id):
    order = Order.query.get(id)
    return render_template('order/detail.html', order=order)


@bp.route('/order/addtolist/<int:id>', methods=['GET'])
@login_required
def addtolist(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    sample = Strain.query.get_or_404(id)
    basket.samples.append(sample)
    sample.basket_id = basket.id
    db.session.commit()
    return redirect(url_for('order.detail', id=sample.patient.order_id))


@bp.route('/order/removefromlist/<int:id>', methods=['GET'])
@login_required
def removefromlist(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    sample = Strain.query.get(id)
    basket.samples.remove(sample)
    sample.basket_id = 0
    db.session.commit()
    return redirect(url_for('order.detail', id=sample.patient.order_id))


@bp.route('/order/add_all/<int:id>', methods=['GET'])
@login_required
def add_all(id):
    order = Order.query.get(id)
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    for patient in order.patients:
        for sample in patient.samples:
            basket.samples.append(sample)
            sample.basket_id = basket.id
            db.session.commit()
    return redirect(url_for('order.detail', id=id))


@bp.route('/order/remove_all/<int:id>', methods=['GET'])
@login_required
def remove_all(id):
    order = Order.query.get(id)
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    for patient in order.patients:
        for sample in patient.samples:
            basket.samples.remove(sample)
            sample.basket_id = 0
            db.session.commit()
    return redirect(url_for('order.detail', id=id))


def get_order_code():
    size = len(Order.query.all()) + 1
    num = str(size).zfill(5)
    return num


def get_bio_code(s):
    size = len(Strain.query.all()) + 1
    num = s + str(size).zfill(10)
    return num


def generateCode(s, index):
    jonc_type_str = ''
    if s.jonc_type:
        jonc_type_str = str(s.jonc_type.siggle)
    s.code = str(s.number) + '-' + str(s.sample_nature.siggle) + str(index) + '-' + jonc_type_str
    db.session.commit()
    # 3SURur2 - fn - rouge
    return s
