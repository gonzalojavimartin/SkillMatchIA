from crypt import methods
from flask import Flask, render_template, redirect, request, url_for
from models import *
from forms import *
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
login_manager = LoginManager(app)
login_manager.login_view = "login"

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
        # Creamos el usuario y lo guardamos
        user = User(len(users) + 1, name, email, password)
        users.append(user)
        # Dejamos al usuario logueado
        login_user(user, remember=True)
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
def register():  # put application's code here
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        # Registra el CV y vuelve al home
        applicant_id = 1234
        return redirect(url_for('applicant_resume',applicant_id=applicant_id))

@app.route('/applicant-resume/<applicant_id>')
@login_required
def applicant_resume(applicant_id):  # put application's code here
    return render_template('applicant-resume.html', applicant_id=applicant_id)


@app.route('/match-applicants', methods=['GET', 'POST'])
@login_required
def match_applicants():  # put application's code here
    if request.method == "GET":
        return render_template('match-applicants-form.html')
    if request.method == "POST":
        # Aplica el modelo para determinar los mejores candidatos
        skills = ["Java","C#","TypeScript"]
        return render_template('match-applicants.html', skills=skills)

@app.route('/')
@login_required
def index():  # put application's code here
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
