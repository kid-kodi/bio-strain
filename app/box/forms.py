from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import Box


class SearchForm(FlaskForm):
    name = StringField(_l('Box name'))
    submit = SubmitField('Search')


class BoxForm(FlaskForm):
    rack = SelectField(choices=[], coerce=int, label="Choisir le rack")
    box_type = SelectField(choices=[], coerce=int, label="Choisir le type de box")
    name = StringField(_l('Box name'), validators=[DataRequired()])
    horizontal = StringField(_l('Nombre de ligne'), validators=[DataRequired()])
    vertical = StringField(_l('Nombre de colonne'), validators=[DataRequired()])
    submit = SubmitField(_l('Save'))
