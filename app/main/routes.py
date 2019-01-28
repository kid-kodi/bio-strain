# app/main/views.py
import os
import xlrd
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale

from app import db, excel, images
from . import bp
from ..models import User, Strain, Frame, SampleType, StrainType, Phenotype, Basket, Notification, Message, Origin, \
    Category, Temperature
from .forms import EditProfileForm, ChangePasswordForm, SearchForm, ChangeAvatarForm, MessageForm

basedir = os.path.abspath(os.path.dirname(__file__))


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    #     g.search_form = SearchForm()
    # g.locale = str(get_locale())


@bp.route('/')
def dashboard():
    """
    Render the bppage template on the / route
    """
    user = User.query.all()
    strains = Strain.query.all()
    return render_template('main/index.html', user=user, strains=strains, title="Welcome")


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('bp.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('bp.user', username=current_user.username))
    return render_template('change_password.html', title=_('Change Password'),
                           form=form)


@bp.route('/change_avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    form = ChangeAvatarForm()
    if form.validate_on_submit():
        if 'image' in request.files:
            filename = images.save(request.files['image'])
            url = images.url(filename)
            print('file exist')
        else:
            print('file do not exist')
            filename = 'default.png'
            url = os.path.join(basedir, '/static/img/default.png')

        current_user.avatar = url
        db.session.commit()
        flash('You have successfully modifiy your avatar')
        return redirect(url_for('strain.list'))

    # load strain template
    return render_template('change_avatar.html',
                           form=form,
                           title="Add Strain")


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route("/setup", methods=['GET', 'POST'])
@login_required
def setup():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('Aucun fichier selectionné')
            return redirect(url_for('main.setup'))
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('Aucun fichier selectionné')
            return redirect(url_for('main.setup'))

        filename = file.filename
        # Write file to static directory and do the hot dog check
        file.save(os.path.join(basedir, filename))
        book = xlrd.open_workbook(os.path.join(basedir, filename))
        for sheet in book.sheets():
            if sheet.name == 'Catégorie':
                data_sheet = book.sheet_by_name("Catégorie")
                # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
                for r in range(1, data_sheet.nrows):
                    category = Category(name=data_sheet.cell(r, 0).value, description=data_sheet.cell(r, 1).value)
                    db.session.add(category)
                    db.session.commit()
            if sheet.name == 'Origine':
                data_sheet = book.sheet_by_name("Origine")
                # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
                for r in range(1, data_sheet.nrows):
                    origin = Origin(name=data_sheet.cell(r, 0).value, description=data_sheet.cell(r, 1).value)
                    db.session.add(origin)
                    db.session.commit()
            if sheet.name == 'Produit biologique':
                data_sheet = book.sheet_by_name("Produit biologique")
                # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
                for r in range(1, data_sheet.nrows):
                    sample_type = SampleType(name=data_sheet.cell(r, 0).value, description=data_sheet.cell(r, 1).value)
                    db.session.add(sample_type)
                    db.session.commit()
            if sheet.name == 'Cadre de receuille':
                data_sheet = book.sheet_by_name("Cadre de receuille")
                # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
                for r in range(1, data_sheet.nrows):
                    frame = Frame(name=data_sheet.cell(r, 0).value, description=data_sheet.cell(r, 1).value)
                    db.session.add(frame)
                    db.session.commit()
            if sheet.name == 'Nom de souche':
                data_sheet = book.sheet_by_name("Nom de souche")
                # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
                for r in range(1, data_sheet.nrows):
                    strain_type = StrainType(name=data_sheet.cell(r, 0).value, description=data_sheet.cell(r, 1).value)
                    db.session.add(strain_type)
                    db.session.commit()
            if sheet.name == 'Phenotype':
                data_sheet = book.sheet_by_name("Phenotype")
                # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
                for r in range(1, data_sheet.nrows):
                    item = Phenotype(name=data_sheet.cell(r, 0).value, description=data_sheet.cell(r, 1).value)
                    db.session.add(item)
                    db.session.commit()

            if sheet.name == 'Temperature':
                data_sheet = book.sheet_by_name("Temperature")
                # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
                for r in range(1, data_sheet.nrows):
                    item = Temperature(name=data_sheet.cell(r, 0).value, description=data_sheet.cell(r, 1).value)
                    db.session.add(item)
                    db.session.commit()

        # Delete image when done with analysis
        os.remove(os.path.join(basedir, filename))
        flash('Initialisation des données effecutées')
        return redirect(url_for('.dashboard'))
    return render_template('main/setup.html')


@bp.route('/basketto')
@login_required
def basketto():
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    count = len(basket.strains.all())
    return jsonify({"count": count})


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(Notification.timestamp > since).order_by(
        Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])
