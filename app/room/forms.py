from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import Room


class SearchForm(FlaskForm):
    name = StringField(_l('Nom de la salle'))
    submit = SubmitField('Search')


class RoomForm(FlaskForm):
    name = StringField(_l('Nom de la salle'), validators=[DataRequired()])
    TextAreaField(_l('Description'))
    submit = SubmitField(_l('Enregistrer'))
