from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import BoxType


class SearchForm(FlaskForm):
    name = StringField(_l('Type de boîte'))
    submit = SubmitField('Rechercher')


class BoxTypeForm(FlaskForm):
    name = StringField(_l('Nom du type de boite'), validators=[DataRequired()])
    max_number = StringField(_l('Nombre de puit'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'),
                                validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Enregistrer'))
