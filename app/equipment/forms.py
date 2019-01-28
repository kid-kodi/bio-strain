from flask import request
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import Equipment


class SearchForm(FlaskForm):
    name = StringField(_l('Nom de l\'equipment'))
    submit = SubmitField('Search')


class EquipmentForm(FlaskForm):
    name = StringField(_l('Nom de l\'equipment'), validators=[DataRequired()])
    room = SelectField(choices=[], coerce=int, label="Choisir la salle")
    equipment_type = SelectField(choices=[], coerce=int, label="Choisir le type")
    horizontal = StringField(_l('Nombre de ligne'), validators=[DataRequired()])
    vertical = StringField(_l('Nombre de colonne'), validators=[DataRequired()])
    max_number = IntegerField(_l('Espace maximum'))
    submit = SubmitField(_l('Enregistrer'))
