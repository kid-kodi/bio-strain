# app/strain/views.py
import os
from flask import abort, flash, request, redirect, render_template, url_for, jsonify
# from flask_weasyprint import HTML, render_pdf
from flask_login import current_user, login_required

from . import bp
from .forms import StrainForm, SearchForm
from .. import db, images
from ..models import Strain, Origin, Customer, Frame, User, StrainType, SampleType, Phenotype, Room, Equipment, Rack, \
    Box, Hole, Basket
import xlrd, app
import flask_excel as excel
from datetime import datetime
from flask_weasyprint import HTML, render_pdf

basedir = os.path.abspath(os.path.dirname(__file__))

from sqlalchemy.sql.expression import and_


def get_query(table, lookups, form_data):
    conditions = [
        getattr(table, field_name) == form_data[field_name]
        for field_name in lookups if form_data[field_name]
    ]

    return table.query.filter(and_(*conditions))


# routes order
@bp.route('/strain', methods=['GET', 'POST'])
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    form = SearchForm()
    # form.frame_id.choices = [(c.id, c.name) for c in Frame.query.all()]
    form.customer_id.choices.append((0, 'Tous les services'))
    for customer in Customer.query.all():
        form.customer_id.choices.append((customer.id, customer.display_as))

    form.origin_id.choices.append((0, 'Toutes les origines'))
    for origin in Origin.query.all():
        form.origin_id.choices.append((origin.id, origin.name))

    if form.validate_on_submit():
        serial_number = form.serial_number.data
        biobank_number = form.biobank_number.data
        customer_id = form.customer_id.data
        origin_id = form.origin_id.data
        print(type(origin_id))
        print(origin_id != 0)
        query = Strain.query
        if serial_number:
            query = query.filter(Strain.serial_number == serial_number)
        elif biobank_number:
            query = query.filter(Strain.biobank_number == biobank_number)
        elif customer_id > 0:
            query = query.filter(Strain.customer_id == customer_id)
        elif origin_id > 0:
            query = query.filter(Strain.origin_id == origin_id)

        pagination = query.order_by(Strain.created_at.desc()).paginate(
            page, per_page=25,
            error_out=False)
    else:
        pagination = Strain.query.order_by(Strain.created_at.desc()).paginate(
            page, per_page=25,
            error_out=False)

    _list = pagination.items
    return render_template('strain/list.html', list=_list, form=form, pagination=pagination)


@bp.route('/strain/add', methods=['GET', 'POST'])
@login_required
def add():
    add = True
    form = StrainForm()
    form.biobank_number.data = "#"
    form.origin_id.choices = [(lvl.id, lvl.name) for lvl in Origin.query.all()]
    form.customer_id.choices = [(sp.id, sp.display_as) for sp in Customer.query.all()]
    form.frame_id.choices = [(u.id, u.name) for u in Frame.query.all()]
    form.strain_type_id.choices = [(u.id, u.name) for u in StrainType.query.all()]
    form.sample_type_id.choices = [(u.id, u.name) for u in SampleType.query.all()]
    form.phenotype_id.choices = [(u.id, u.name) for u in Phenotype.query.all()]
    # form.room_id.choices = [(u.id, u.name) for u in Room.query.all()]
    # form.equipment_id.choices = [(u.id, u.name) for u in Equipment.query.all()]
    # form.rack_id.choices = [(u.id, u.name) for u in Rack.query.all()]
    # form.box_id.choices = [(u.id, u.name) for u in Box.query.all()]
    # form.hole_id.choices = [(u.id, u.name) for u in Hole.query.all()]

    if form.validate_on_submit():
        strain = Strain(biobank_number=generateNum(),
                        origin_id=form.origin_id.data,
                        customer_id=form.customer_id.data,
                        frame_id=form.frame_id.data,
                        strain_type_id=form.strain_type_id.data,
                        sample_type_id=form.sample_type_id.data,
                        phenotype_id=form.phenotype_id.data,
                        serial_number=form.serial_number.data,
                        mutation_type=form.mutation_type.data,
                        identity=form.identity.data,
                        receive_date=form.receive_date.data,
                        conservation_date=form.conservation_date.data,
                        created_at=datetime.utcnow(),
                        status=0,
                        created_by=current_user.id)

        db.session.add(strain)
        db.session.commit()
        flash('Enregistrement effectué!')
        return redirect(url_for('strain.list'))

    # load strain template
    return render_template('strain/form.html', action="Add",
                           add=add, form=form,
                           title="Add Strain")


@bp.route('/strain/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit a strain
    """

    add = False

    strain = Strain.query.get_or_404(id)
    form = StrainForm(obj=strain)
    form.origin_id.choices = [(lvl.id, lvl.name) for lvl in Origin.query.all()]
    form.customer_id.choices = [(sp.id, sp.display_as) for sp in Customer.query.all()]
    form.frame_id.choices = [(u.id, u.name) for u in Frame.query.all()]
    form.strain_type_id.choices = [(u.id, u.name) for u in StrainType.query.all()]
    form.sample_type_id.choices = [(u.id, u.name) for u in SampleType.query.all()]
    form.phenotype_id.choices = [(u.id, u.name) for u in Phenotype.query.all()]
    if form.validate_on_submit():
        strain.origin_id = form.origin_id.data
        strain.customer_id = form.customer_id.data
        strain.frame_id = form.frame_id.data
        strain.biobank_number = form.biobank_number.data
        strain.serial_number = form.serial_number.data
        strain.strain_type_id = form.strain_type_id.data
        strain.sample_type_id = form.sample_type_id.data
        strain.phenotype_id = form.phenotype_id.data
        strain.mutation_type = form.mutation_type.data
        strain.identity = form.identity.data
        strain.receive_date = form.receive_date.data
        strain.conservation_date = form.conservation_date.data

        db.session.commit()
        flash('You have successfully edited the strain.')

        # redirect to the strain page
        return redirect(url_for('strain.list'))

    form.origin_id.data = strain.origin_id
    form.biobank_number.data = strain.biobank_number
    form.customer_id.data = strain.customer_id
    form.frame_id.data = strain.frame_id
    form.strain_type_id.data = strain.strain_type_id
    form.sample_type_id.data = strain.sample_type_id
    form.phenotype_id.data = strain.phenotype_id
    form.serial_number.data = strain.serial_number
    form.mutation_type.data = strain.mutation_type
    form.identity.data = strain.identity
    form.receive_date.data = strain.receive_date
    form.conservation_date.data = strain.conservation_date

    return render_template('strain/form.html', action="Edit",
                           add=add, form=form,
                           strain=strain, title="Edit Strain")


@bp.route('/strain/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    strain = Strain.query.get(id)
    return render_template('strain/detail.html', strain=strain)


@bp.route('/strain/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    """
    Delete a strain from the database
    """

    strain = Strain.query.get_or_404(id)
    db.session.delete(strain)
    db.session.commit()
    flash('You have successfully deleted the strain.')

    # redirect to the strain page
    return redirect(url_for('strain.list'))


@bp.route("/strain/import", methods=['GET', 'POST'])
@login_required
def import_in():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('Aucun fichier selectionné')
            return redirect(url_for('strain.import_in'))
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('Aucun fichier selectionné')
            return redirect(url_for('strain.import_in'))

        filename = file.filename
        # Write file to static directory and do the hot dog check
        file.save(os.path.join(basedir, filename))
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
                    strain.frame = Frame.query.filter_by(name=data_sheet.cell(r, 4).value).first()
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

        # Delete image when done with analysis
        os.remove(os.path.join(basedir, filename))
        return redirect(url_for('strain.list'))
    return render_template('strain/import.html')


@bp.route("/strain/export", methods=['GET'])
@login_required
def export_out():
    list = Strain.query.all()
    column_names = ['biobank_number', 'first_name', 'last_name', 'origin_id', 'frame_id',
                    'school', 'email', 'phone', 'theme']
    return excel.make_response_from_query_sets(list, column_names, "xls", file_name="strain_data")


@bp.route('/strain/print', methods=['GET', 'POST'])
@login_required
def print_to():
    data = request.get_json()
    ids = data['items']
    print(data['items'])
    strain = Strain.query.filter(Strain.id.in_(ids)).all()
    for value in strain:
        print(value)
    # Make a PDF straight from HTML in a string.
    return jsonify({'strain': [strain.to_json() for strain in strain]})


@bp.route('/strain/addtolist/<int:id>', methods=['GET'])
@login_required
def addtolist(id):
    basket = Basket.query.first()
    strain = Strain.query.get_or_404(id)
    basket.strains.append(strain)
    strain.basket_id = basket.id
    db.session.commit()
    return redirect(url_for('strain.list'))


@bp.route('/strain/removefromlist/<int:id>', methods=['GET'])
@login_required
def removefromlist(id):
    basket = Basket.query.first()
    strain = Strain.query.get(id)
    basket.strains.remove(strain)
    strain.basket_id = 0
    db.session.commit()
    return redirect(url_for('strain.list'))


@bp.route('/strain/pdf', methods=['GET', 'POST'])
@login_required
def pdf():
    name = 'kone'
    # Make a PDF straight from HTML in a string.
    html = render_template('strain/pdf.html', name=name)
    return render_pdf(HTML(string=html))


def generateNum():
    now = datetime.utcnow()
    year = now.year
    number = str(Strain.query.count() + 1).zfill(10)
    return number
