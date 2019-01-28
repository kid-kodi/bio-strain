from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField, FormField, RadioField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import Form as NoCsrfForm
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l


class ImportForm(FlaskForm):
    document = FileField('Selectionner un fichier')
    submit = SubmitField(_l('Suivant'))


class ExpeditionForm(FlaskForm):
    customer = SelectField(_l('Client'), coerce=int, choices=[])
    frame = SelectField(_l('Projet'), coerce=int, choices=[])
    first_name = StringField(_l('Nom de l\'expediteur'))
    last_name = StringField(_l('Prénoms de l\'expediteur'), validators=[DataRequired()])
    telephone = StringField(_l('Téléphone'), validators=[DataRequired()])
    send_date = StringField(_l('Date d\'expedition'), validators=[DataRequired()])
    temperature = SelectField(_l('Température de transport'), coerce=int, choices=[])
    expedition_date = StringField(_l('Date d\'envoi'), validators=[DataRequired()])
    strains = SelectMultipleField(_l('Liste des souches à stocker'), coerce=int)
    submit = SubmitField(_l('Enregistrer'))
