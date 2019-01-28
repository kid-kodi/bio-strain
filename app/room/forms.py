from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import Room


class SearchForm(FlaskForm):
    name = StringField(_l('Room name'))
    submit = SubmitField('Search')


class RoomForm(FlaskForm):
    name = StringField(_l('Nom de la salle'), validators=[DataRequired()])
    submit = SubmitField(_l('Enregistrer'))
