from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l


class CustomerForm(FlaskForm):
    category = SelectField(_l('Catégorie'), coerce=int)
    display_as = StringField(_l('Raison sociale'), validators=[DataRequired()])
    first_name = StringField(_l('Nom'))
    last_name = StringField(_l('Prénoms'))
    telephone = StringField(_l('Téléphone'), validators=[DataRequired()])
    email = StringField(_l('Adresse email'), validators=[DataRequired()])
    address = TextAreaField(_l('Adresse'),
                            validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Enregistrer'))
