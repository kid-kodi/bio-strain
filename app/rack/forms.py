from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import Rack


class SearchForm(FlaskForm):
    name = StringField(_l('Nom du rack'))
    submit = SubmitField('Search')


class RackForm(FlaskForm):
    equipment = SelectField(choices=[], coerce=int, label="Choisir l'équipement")
    name = StringField(_l('Nom du rack'), validators=[DataRequired()])
    horizontal = StringField(_l('Nombre de ligne'), validators=[DataRequired()])
    vertical = StringField(_l('Nombre de colonne'), validators=[DataRequired()])
    max_number = IntegerField(_l('Espace maximum'), validators=[DataRequired()])
    submit = SubmitField(_l('Enregistrer'))
