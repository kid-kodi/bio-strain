from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class SampleTypeForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Enregistrer')
