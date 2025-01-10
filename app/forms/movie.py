from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SelectMultipleField, FileField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.file import FileAllowed

class MovieForm(FlaskForm):
    title = StringField('Título', 
        validators=[DataRequired(), Length(min=1, max=200)])
    
    description = TextAreaField('Descripción',
        validators=[DataRequired(), Length(min=10, max=2000)])
    
    release_date = StringField('Fecha de Estreno',
        validators=[DataRequired()])
    
    duration = IntegerField('Duración (minutos)',
        validators=[DataRequired(), NumberRange(min=1, max=999)])
    
    content_type = SelectField('Tipo',
        choices=[('movie', 'Película'), ('series', 'Serie')],
        validators=[DataRequired()])
    
    genres = SelectMultipleField('Géneros',
        coerce=int,
        validators=[DataRequired()])
    
    poster = FileField('Póster',
        validators=[FileAllowed(['jpg', 'png'], 'Solo imágenes!')])