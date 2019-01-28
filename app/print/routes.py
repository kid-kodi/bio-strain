import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, make_response
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, current_app
from app.print.forms import PrintForm
from app.models import Hole, Sample, Basket, Label, Print, PrintItem
from app.translate import translate
from app.print import bp
import pdfkit



@bp.route('/print', methods=['GET', 'POST'])
@login_required
def index():
    prints = Print.query.all()
    return render_template('print/list.html', prints=prints)


@bp.route('/print/add', methods=['GET', 'POST'])
@login_required
def add():
    form = PrintForm()
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    form.samples.choices = [(c.id, c.code) for c in basket.samples.filter_by(status=0).all()]
    form.label.choices = [(c.id, c.name) for c in Label.query.all()]
    if form.validate_on_submit():
        print = Print()
        print.serial = datetime.utcnow().strftime("%d%m%Y%H%M%S")
        print.label_id = form.label.data
        print.status = 0
        print.timestamp = datetime.utcnow()
        print.created_by = current_user.id
        for sample_id in form.samples.data:
            print_item = PrintItem()
            print_item.sample_id = sample_id
            print_item.status = 0
            print_item.created_by = current_user.id
            print_item.timestamp = datetime.utcnow()
            print.print_items.append(print_item)
        db.session.add(print)
        db.session.commit()
        flash(_('Enregistrement effectué avec succèss'))
        return redirect(url_for('print.index'))
    return render_template('print/form.html', form=form, basket=basket)


@bp.route('/print/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    print = Print.query.get(id)
    return render_template('print/detail.html', print=print)


@bp.route('/print/proceed/<int:id>', methods=['GET', 'POST'])
@login_required
def proceed(id):
    print = Print.query.get(id)
    samples = []
    for print_items in print.print_items:
        sample = print_items.sample
        samples.append(sample)
        sample.status = 1
        print_items.status = 1
        db.session.commit()
    print.status = 1
    db.session.commit()
    html = render_template('_bar_code.html', samples=samples)
    css = current_app.config['APP_CSS'] + 'print.css'
    pdf = pdfkit.from_string(html, False, css=css)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=code.pdf'
    return response


@bp.route('/sample/print_selected', methods=['GET', 'POST'])
@login_required
def print_selected(data):
    all_args = request.args.to_dict()
    print(all_args)
    sample = []
    html = render_template('_bar_code.html', sample=sample)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=code.pdf'
    return response
