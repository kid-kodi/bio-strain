from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    name = StringField('Nom de la catégorie', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Enregistrer')
