import os.path
import gensim.downloader as api
import spacy
from flask import Flask, render_template, redirect, request, url_for, jsonify
from werkzeug.utils import secure_filename

from models import *
from forms import *
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import gensim
import numpy as np
import PyPDF2
import json
import pandas as pd

from salary_prediction import get_trained_model, get_job_positions, get_seniorities, get_genders, get_cities, \
    label_encoders
from technologies import get_technologies

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
login_manager = LoginManager(app)
login_manager.login_view = "login"

users.append(User(len(users) + 1, "SysAdmin", "admin@skillmatchia.com", "123", UserRol.ADMIN))
users.append(User(len(users) + 1, "Gonzalo Martin", "gonzalojavimartin@gmail.com", "123", UserRol.APPLICANT))
users.append(User(len(users) + 1, "Empresa Reclutadora", "reclutamiento@empresa.com", "123", UserRol.RECRUITER))

TECHNOLOGIES = get_technologies()

model_salary_prediction = get_trained_model()

@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None

@app.route("/signup/", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        rol = UserRol[form.rol.data]
        # Creamos el usuario y lo guardamos
        user = User(len(users) + 1, name, email, password, rol)
        users.append(user)
        # Dejamos al usuario logueado
        # login_user(user, remember=True)
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("signup.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

@app.route('/upload-cv', methods=['GET', 'POST'])
@login_required
def upload_cv():
    form = UploadCurriculumForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file_cv.data.filename)
        path = 'uploads/' + filename
        form.file_cv.data.save(path)
        text_cv = extract_text_from_pdf(path)
        skills = identify_skills_tech(text_cv)
        os.remove(path)
        applicant = Candidato(current_user.get_name(), current_user.email, skills)
        list_candidatos.append(applicant)
        applicant_id = applicant.get_id()
        return redirect(url_for('applicant_resume', applicant_id=applicant_id))
    else:
        return render_template('upload-cv.html', form=form)

@app.route('/applicant-resume/<applicant_id>')
@login_required
def applicant_resume(applicant_id):
    for applicant in list_candidatos:
        if applicant_id == applicant.id:
            return render_template('applicant-resume.html', applicant=applicant)

def extract_technologies(words_list):
    return [tech for tech in words_list if tech in TECHNOLOGIES]

def identify_skills_tech(text):
    nlp = spacy.load("model_upgrade_techs")
    doc = nlp(text)
    skills = []

    for ent in doc.ents:
        if ent.label_ in ["ORG", "TECHNOLOGY", "TECH"]:
            skills.append(ent.text)

    found_technologies = extract_technologies(skills)

    return list(set(found_technologies))

# Función para calcular la similitud entre dos palabras usando GloVe y gensim
def similarity(words1, words2):
    similarities = []

    for word1 in words1:
        max_similarity = 0
        for word2 in words2:
            try:
                # Si ambas palabras están en el vocabulario de GloVe
                # Guardamos la máxima similitud encontrada
                sim = glove_model.similarity(word1.lower(), word2.lower())
                max_similarity = max(max_similarity, sim)
            except KeyError:
                continue
        similarities.append(max_similarity)

    # Calculamos la similitud promedio
    return np.mean(similarities) if similarities else 0

@app.route('/match-applicants', methods=['GET', 'POST'])
@login_required
def match_applicants():
    form = MatchingApplicantsForm()
    if form.validate_on_submit():
        job_description = form.job_description
        user_input = job_description.data
        skills_required = identify_skills_tech(user_input)

        # Obtener candidatos desde la base de datos
        applicants = list_candidatos

        # Calcular la similitud
        result = []
        for applicant in applicants:
            simil = similarity(skills_required, applicant.skills_tech)
            result.append((applicant.full_name,applicant.email, applicant.skills_tech, simil))

        # Ordenar resultados por la similitud (de mayor a menor)
        top_applicants = sorted(result, key=lambda x: x[3], reverse=True)

        # Filtrar solo aquellos con alguna similitud > 0
        top_applicants = [res for res in top_applicants if res[3] > 0]
        top_applicants = top_applicants[:5]
        top_applicants_json = [
            {
                'full_name': applicant[0],
                'email': applicant[1],
                'skills_tech': applicant[2],
                'similitud': float(applicant[3])
            }
            for applicant in top_applicants
        ]
        return render_template('match-applicants.html', job_description=user_input, skills_required=skills_required,top_candidatos=top_applicants_json)

    return render_template('match-applicants-form.html', form=form)

@app.route('/salary-prediction', methods=['GET', 'POST'])
@login_required
def salary_prediction():
    form = SalaryPredictionForm()
    form.job_position.choices = [(job_position, job_position) for job_position in get_job_positions()]
    form.seniority.choices  = [(seniority, seniority) for seniority in get_seniorities()]
    form.gender.choices  = [(gender, gender) for gender in get_genders()]
    form.city.choices  = [(city, city) for city in get_cities()]
    technologies = get_candidato_by_email(current_user.email).skills_tech
    if form.validate_on_submit():
        # Recuperamos los datos de la sesión
        puesto = form.job_position.data
        tecnologias = technologies
        seniority = form.seniority.data
        ciudad = form.city.data
        genero = form.gender.data

        # Convertimos las respuestas del usuario en los formatos correctos usando los codificadores entrenados
        seniority_encoded = label_encoders['seniority'].transform([seniority])[0]
        ciudad_encoded = label_encoders['donde_estas_trabajando'].transform([ciudad])[0]
        genero_encoded = label_encoders['me_identifico_genero'].transform([genero])[0]

        # Preparar los datos para la predicción
        user_data = np.array([[seniority_encoded, ciudad_encoded, genero_encoded]])
        predicted_salary = model_salary_prediction.predict(user_data)[0]

        prediction_result = {
            "job_position" : puesto,
            "seniority" : seniority,
            "city" : ciudad,
            "gender" : genero,
            "technologies" : technologies,
            "predicted_salary" : predicted_salary
        }

        return render_template('salary-prediction-result.html', prediction_result=prediction_result)
    return render_template('salary-prediction.html', form=form,technologies=technologies)

@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Cargar el archivo GloVe descargado manualmente
# Para desarrollo local descargar desde https://nlp.stanford.edu/data/glove.6B.zip
glove_file = 'static/glove/glove.6B.100d.txt'

if  os.path.isfile(glove_file):
    print("Cargando el modelo GloVe desde archivo...")
    glove_model = gensim.models.KeyedVectors.load_word2vec_format(glove_file, binary=False, no_header=True)
else:
    # Descargar los embeddings de GloVe
    print("Cargando el modelo GloVe desde gensim.downloader...")
    glove_model = api.load("glove-wiki-gigaword-100")

print("Modelo GloVe cargado.")

if __name__ == '__main__':
    app.run(debug=True)
