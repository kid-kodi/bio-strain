# app/departement/forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email
from app import images


class SearchForm(FlaskForm):
    biobank_number = StringField('Numéro biobank')
    serial_number = StringField("Numéro d\'origine")
    origin_id = SelectField("Origine de la souche", choices=[], coerce=int)
    customer_id = SelectField("Origine de la souche", choices=[], coerce=int)
    submit = SubmitField('Recherche')


class StrainForm(FlaskForm):
    customer_id = SelectField(choices=[], coerce=int, label="Service d\'origine")
    origin_id = SelectField(choices=[], coerce=int, label="Origine de la souche")
    frame_id = SelectField(choices=[], coerce=int, label="Cadre de receuille")
    receive_date = StringField('Date de reception')
    strain_type_id = SelectField(choices=[], coerce=int, label="Nom de la souche")
    sample_type_id = SelectField(choices=[], coerce=int, label="Produit biologique")
    phenotype_id = SelectField(choices=[], coerce=int, label="Phenotype")
    serial_number = StringField("Numéro d\'origine")
    biobank_number = HiddenField()
    mutation_type = StringField('Type de mutation')
    identity = StringField('Identification malditof')
    conservation_date = StringField('Date de conservavtion')
    # room_id = SelectField(choices=[], coerce=int, label="Choisir la salle")
    # equipment_id = SelectField(choices=[], coerce=int, label="Choisir l'équipement")
    # rack_id = SelectField(choices=[], coerce=int, label="Choisir le rack")
    # box_id = SelectField(choices=[], coerce=int, label="Choisir la boite")
    # hole_id = SelectField(choices=[], coerce=int, label="Choisir le puit")
    submit = SubmitField('Enregistrer')
