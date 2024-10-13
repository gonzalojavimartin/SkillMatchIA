from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import TextAreaField, FileField
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
    job_description = TextAreaField('Descripcion de puesto', validators=[DataRequired()])

class UploadCurriculumForm(FlaskForm):
    file_cv = FileField('Curriculum', validators=[DataRequired()])

class SalaryPredictionForm(FlaskForm):
    job_position = SelectField('Puesto', validators=[DataRequired()])
    seniority = SelectField('Seniority', validators=[DataRequired()])
    dedication = SelectField('Dedicacion', validators=[DataRequired()])
    gender = SelectField('Genero', validators=[DataRequired()])
    experience = SelectField('Experiencia', validators=[DataRequired()])