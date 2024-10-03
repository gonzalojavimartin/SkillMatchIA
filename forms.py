from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, Length
from email_validator import validate_email, EmailNotValidError
from models import UserRol


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    rol = SelectField('Rol',validators=[DataRequired()],choices=[(UserRol.APPLICANT.name,"Candidato"),(UserRol.RECRUITER.name,"Reclutador")])
    submit = SubmitField('Registrar')

class MatchingApplicantsForm(FlaskForm):
    job_description = TextAreaField('job_description', validators=[DataRequired()])