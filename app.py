import os.path
import gensim.downloader as api
import spacy
from flask import Flask, render_template, redirect, request, url_for, jsonify
from models import *
from forms import *
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import gensim
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
login_manager = LoginManager(app)
login_manager.login_view = "login"

users.append(User(len(users) + 1, "SysAdmin", "admin@skillmatchia.com", "123", UserRol.ADMIN))
users.append(User(len(users) + 1, "Gonzalo Martin", "gonzalojavimartin@gmail.com", "123", UserRol.APPLICANT))
users.append(User(len(users) + 1, "Empresa Reclutadora", "reclutamiento@empresa.com", "123", UserRol.RECRUITER))

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

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        # Registra el CV y vuelve al home
        applicant_id = 1234
        return redirect(url_for('applicant_resume',applicant_id=applicant_id))

@app.route('/applicant-resume/<applicant_id>')
@login_required
def applicant_resume(applicant_id):
    return render_template('applicant-resume.html', applicant_id=applicant_id)

# Función para calcular la similitud entre dos palabras usando GloVe y gensim
def calcular_similitud(tec_puesto, tec_candidato):
    similitudes = []

    for tec_p in tec_puesto:
        max_similitud = 0
        for tec_c in tec_candidato:
            try:
                # Si ambas tecnologías están en el vocabulario de GloVe
                # Guardamos la máxima similitud encontrada
                sim = glove_model.similarity(tec_p.lower(), tec_c.lower())
                max_similitud = max(max_similitud, sim)
            except KeyError:
                continue
        similitudes.append(max_similitud)

    # Calculamos la similitud promedio
    return np.mean(similitudes) if similitudes else 0

@app.route('/match-applicants', methods=['GET', 'POST'])
@login_required
def match_applicants():
    form = MatchingApplicantsForm()
    if form.validate_on_submit():
        job_description = form.job_description
        user_input = job_description.data
        nlp = spacy.load("model_upgrade_techs")
        doc = nlp(user_input)
        skills_required = []

        for ent in doc.ents:
            if ent.label_ in ["ORG", "TECHNOLOGY", "TECH"]:
                skills_required.append(ent.text)

        # Obtener candidatos desde la base de datos
        candidatos = list_candidatos

        # Calcular la similitud
        resultados = []
        for candidato in candidatos:
            similitud = calcular_similitud(skills_required, candidato.skills_tech)
            resultados.append((candidato.full_name,candidato.email, candidato.skills_tech, similitud))

        # Ordenar resultados por la similitud (de mayor a menor)
        top_candidatos = sorted(resultados, key=lambda x: x[3], reverse=True)

        # Filtrar solo aquellos con alguna similitud > 0
        top_candidatos = [res for res in top_candidatos if res[3] > 0]
        top_candidatos = top_candidatos[:5]
        top_candidatos_json = [
            {
                'full_name': candidato[0],
                'email': candidato[1],
                'skills_tech': candidato[2],
                'similitud': float(candidato[3])
            }
            for candidato in top_candidatos
        ]
        return render_template('match-applicants.html', job_description=user_input, skills_required=skills_required,top_candidatos=top_candidatos_json)

    return render_template('match-applicants-form.html', form=form)

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
