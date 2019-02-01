from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import EquipmentType


class SearchForm(FlaskForm):
    name = StringField(_l('Nom du type d\'équipement'))
    submit = SubmitField('Rechercher')


class EquipmentTypeForm(FlaskForm):
    name = StringField(_l('Nom du type d\'équipement'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'),
                                validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Enregistrer'))
