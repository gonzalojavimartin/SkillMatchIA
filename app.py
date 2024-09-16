from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/register')
def register():  # put application's code here
    return render_template('register.html')

@app.route('/match-applicants')
def match_applicants():  # put application's code here
    return render_template('match-applicants.html')

@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
