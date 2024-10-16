import os.path
import gensim.downloader as api
import joblib
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

from salary_prediction import *
from technologies import get_technologies

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Cargar el archivo GloVe descargado manualmente
# Para desarrollo local descargar desde https://nlp.stanford.edu/data/glove.6B.zip
glove_file = 'static/models/glove/glove.6B.100d.txt'
if os.path.isfile(glove_file):
    print("Cargando el modelo GloVe desde archivo...")
    glove_model = gensim.models.KeyedVectors.load_word2vec_format(glove_file, binary=False, no_header=True)
else:
    # Descargar los embeddings de GloVe
    print("Cargando el modelo GloVe desde gensim.downloader...")
    glove_model = api.load("glove-wiki-gigaword-100")
print("Modelo GloVe cargado.")

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
    current_applicant = get_candidato_by_email(current_user.email)
    form = UploadCurriculumForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file_cv.data.filename)
        path = 'uploads/' + filename
        form.file_cv.data.save(path)
        text_cv = extract_text_from_pdf(path)
        skills = identify_skills_tech(text_cv)
        os.remove(path)
        applicant = get_candidato_by_email(current_user.email)
        applicant.skills_tech = skills
        update_cadidato_by_email(applicant)
        applicant_id = applicant.get_id()
        return redirect(url_for('applicant_resume', applicant_id=applicant_id))
    else:
        return render_template('upload-cv.html', form=form,current_applicant=current_applicant)

@app.route('/applicant-resume/<applicant_id>')
@login_required
def applicant_resume(applicant_id):
    for applicant in list_candidatos:
        if applicant_id == applicant.id:
            return render_template('applicant-resume.html', applicant=applicant)

def extract_technologies(words_list):
    return [tech for tech in words_list if tech in get_technologies()]

def identify_skills_tech(text):
    text = text.lower()
    nlp = spacy.load("static/models/ner_techs/model_upgrade_techs")
    doc = nlp(text)
    skills = []

    for ent in doc.ents:
        if ent.label_ in ["ORG", "TECHNOLOGY", "TECH"]:
            skills.append(ent.text.lower())

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
    current_applicant = get_candidato_by_email(current_user.email)
    form = SalaryPredictionForm()
    form.job_position.choices = [(row['encoding'], row['trabajo_de']) for index, row in get_job_positions().iterrows()]
    form.seniority.choices = [(row['encoding'], row['seniority']) for index, row in get_seniorities().iterrows()]
    form.gender.choices = [(row['encoding'], row['genero']) for index, row in get_genders().iterrows()]
    form.dedication.choices = [(row['encoding'], row['dedicacion']) for index, row in get_dedications().iterrows()]
    form.experience.choices = [(row['encoding'], row['rango_experiencia']) for index, row in get_experiences().iterrows()]

    if current_applicant:
        technologies = current_applicant.skills_tech
    else:
        technologies = []

    if form.validate_on_submit():
        # Recuperamos los datos de la sesión
        job_position = form.job_position.data
        seniority = form.seniority.data
        gender = form.gender.data
        dedication = form.dedication.data
        experience = form.experience.data

        # Preparar los datos para la predicción
        df_user = setup_input_model(job_position,seniority,gender,dedication,experience,technologies)
        modelo = joblib.load('static/models/salary_prediction/salary_prediction_linear_regression.pkl')
        predicted_salary = modelo.predict(df_user)

        prediction_result = {
            "technologies" : technologies,
            "job_position" : get_label_by_encoding("job_position",job_position),
            "seniority" : get_label_by_encoding('seniority',seniority),
            "dedication" : get_label_by_encoding('dedication',dedication),
            "gender" : get_label_by_encoding('gender',gender),
            "experience" : get_label_by_encoding('experience',experience),
            "predicted_salary" : predicted_salary
        }

        return render_template('salary-prediction-result.html', prediction_result=prediction_result)
    return render_template('salary-prediction.html', form=form,technologies=technologies)

@app.route('/')
@login_required
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
