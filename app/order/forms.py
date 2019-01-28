from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FieldList, FormField, RadioField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import Form as NoCsrfForm
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l


class ImportForm(FlaskForm):
    document = FileField('Selectionner un fichier')
    submit = SubmitField(_l('Suivant'))


class OrderForm(FlaskForm):
    customer = SelectField(_l('Client'), coerce=int, choices=[])
    frame = SelectField(_l('Frame'), coerce=int, choices=[])
    first_name = StringField(_l('Nom du deposant'))
    last_name = StringField(_l('Prénoms du deposant'), validators=[DataRequired()])
    telephone = StringField(_l('Téléphone'), validators=[DataRequired()])
    send_date = StringField(_l('Date d\'expedition'), validators=[DataRequired()])
    temperature = SelectField(_l('Température de transport'), coerce=int, choices=[])
    receive_date = StringField(_l('Date de reception'), validators=[DataRequired()])
    nbr_pack = StringField(_l('Nombre de paquet'), validators=[DataRequired()])
    file = FileField('Selectionner un fichier')
    submit = SubmitField(_l('Suivant'))
