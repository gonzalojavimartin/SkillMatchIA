from crypt import methods

from flask import Flask, render_template, redirect, request, url_for

app = Flask(__name__)

@app.route('/register', methods=['GET', 'POST'])
def register():  # put application's code here
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        # Registra el CV y vuelve al home
        applicant_id = 1234
        return redirect(url_for('applicant_resume',applicant_id=applicant_id))

@app.route('/applicant-resume/<applicant_id>')
def applicant_resume(applicant_id):  # put application's code here
    return render_template('applicant-resume.html', applicant_id=applicant_id)


@app.route('/match-applicants', methods=['GET', 'POST'])
def match_applicants():  # put application's code here
    if request.method == "GET":
        return render_template('match-applicants-form.html')
    if request.method == "POST":
        # Aplica el modelo para determinar los mejores candidatos
        skills = ["Java","C#","TypeScript"]
        return render_template('match-applicants.html', skills=skills)

@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
