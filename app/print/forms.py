from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l


class PrintForm(FlaskForm):
    samples = SelectMultipleField(_l('Liste des échantillons à imprimer'), coerce=int)
    label= SelectField(_l('Selectionner un format'), coerce=int)
    submit = SubmitField(_l('Enregistrer'))
