import os
import xlrd
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db, documents
from app.expedition.forms import ExpeditionForm, ImportForm
from app.models import Expedition, Customer, Strain, Origin, StrainType, Frame, Phenotype, SampleType, Temperature, Basket
from app.expedition import bp

basedir = ''


@bp.route('/expedition', methods=['GET', 'POST'])
@login_required
def index():
    expeditions = Expedition.query.all()
    return render_template('expedition/index.html', expeditions=expeditions)


@bp.route('/expedition/download_file/<filename>')
def download_file(filename):
    return send_from_directory(current_app.config['UPLOADS_DEFAULT_DEST'], filename, as_attachment=True)


@bp.route('/expedition/add', methods=['GET', 'POST'])
@login_required
def add():
    form = ExpeditionForm()
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    form.strains.choices = [(c.id, c.code) for c in basket.strains.filter_by(status=0).all()]
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.frame.choices = [(c.id, c.name) for c in Frame.query.all()]
    form.temperature.choices = [(c.id, c.name) for c in Temperature.query.all()]

    if form.validate_on_submit():
        expedition = Expedition()
        expedition.serial = get_expedition_code()
        expedition.frame_id = form.frame.data
        expedition.customer_id = form.customer.data
        expedition.first_name = form.first_name.data
        expedition.last_name = form.last_name.data
        expedition.telephone = form.telephone.data
        expedition.expedition_date = form.expedition_date.data
        expedition.temperature_id = form.temperature.data
        expedition.nbr_pack = form.nbr_pack.data
        expedition.timestamp = datetime.utcnow()
        expedition.user_id = current_user.id
        for strain_id in form.strains.data:
            strain = Strain.query.get(strain_id)
            strain.status = 10
            db.session.commit()
        expedition.status = 0
        db.session.add(expedition)
        db.session.commit()

        flash(_('Informations du dépôt enregistrées!'))
        return redirect(url_for('expedition.detail', id=expedition.id))

    return render_template('expedition/form.html', form=form)


@bp.route('/expedition/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    expedition = Expedition.query.get(id)
    return render_template('expedition/detail.html', expedition=expedition)


@bp.route('/expedition/validate/<int:id>', methods=['GET', 'POST'])
@login_required
def validate(id):
    expedition = Expedition.query.get(id)
    filename = expedition.file_url
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

        expedition.status = 1
        db.session.commit()
        # and check sample id if already in db
    flash(_('Traitement effectué avec succes!'))
    return redirect(url_for('expedition.detail', id=expedition.id))


@bp.route('/expedition/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    expedition = Expedition.query.get(id)
    form = ExpeditionForm(obj=expedition)
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.frame.choices = [(c.id, c.name) for c in Frame.query.all()]
    form.temperature.choices = [(c.id, c.name) for c in Temperature.query.all()]

    if form.validate_on_submit():

        expedition.customer_id = form.customer.data
        expedition.frame_id = form.frame.data
        expedition.first_name = form.first_name.data
        expedition.last_name = form.last_name.data
        expedition.telephone = form.telephone.data
        expedition.expedition_date = form.expedition_date.data
        expedition.temperature_id = form.temperature.data
        expedition.nbr_pack = form.nbr_pack.data
        expedition.strains = basket.strains
        db.session.commit()
        flash(_('Modification effectuée avec succèss!!'))
        return redirect(url_for('expedition.detail', id=expedition.id))
    form.customer.data = expedition.customer.id
    form.frame.data = expedition.frame.id
    form.first_name.data = expedition.first_name
    form.last_name.data = expedition.last_name
    form.telephone.data = expedition.telephone
    form.expedition_date.data = expedition.expedition_date
    form.nbr_pack.data = expedition.nbr_pack
    form.temperature.data = expedition.temperature_id

    return render_template('expedition/form.html', form=form)


@bp.route('/expedition/process/<int:id>', methods=['GET', 'POST'])
@login_required
def process(id):
    expedition = Expedition.query.get(id)
    return render_template('expedition/detail.html', expedition=expedition)


@bp.route('/expedition/addtolist/<int:id>', methods=['GET'])
@login_required
def addtolist(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    sample = Strain.query.get_or_404(id)
    basket.samples.append(sample)
    sample.basket_id = basket.id
    db.session.commit()
    return redirect(url_for('expedition.detail', id=sample.patient.expedition_id))


@bp.route('/expedition/removefromlist/<int:id>', methods=['GET'])
@login_required
def removefromlist(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    sample = Strain.query.get(id)
    basket.samples.remove(sample)
    sample.basket_id = 0
    db.session.commit()
    return redirect(url_for('expedition.detail', id=sample.patient.expedition_id))


@bp.route('/expedition/add_all/<int:id>', methods=['GET'])
@login_required
def add_all(id):
    expedition = Expedition.query.get(id)
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    for patient in expedition.patients:
        for sample in patient.samples:
            basket.samples.append(sample)
            sample.basket_id = basket.id
            db.session.commit()
    return redirect(url_for('expedition.detail', id=id))


@bp.route('/expedition/remove_all/<int:id>', methods=['GET'])
@login_required
def remove_all(id):
    expedition = Expedition.query.get(id)
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    for patient in expedition.patients:
        for sample in patient.samples:
            basket.samples.remove(sample)
            sample.basket_id = 0
            db.session.commit()
    return redirect(url_for('expedition.detail', id=id))


def get_expedition_code():
    size = len(Expedition.query.all()) + 1
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
