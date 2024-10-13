import uuid

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class UserRol(Enum):
    ADMIN = 'admin'
    APPLICANT = 'applicant'
    RECRUITER = 'recruitment'

class User(UserMixin):

    def __init__(self, id, name, email, password, rol, is_admin=False):
        self.id = id
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
        self.rol = rol
        self.is_admin = is_admin

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_applicant(self):
        return self.rol == UserRol.APPLICANT

    def is_recruiter(self):
        return self.rol == UserRol.RECRUITER

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

users = []

def get_user(email):
    for user in users:
        if user.email == email:
            return user
    return None

class Candidato:
    def __init__(self, full_name, email, skills_tech):
        self.id = str(uuid.uuid4())
        self.full_name = full_name
        self.email = email
        self.skills_tech = skills_tech

    def __repr__(self):
        return '<Candidato {} {} {}>'.format(self.full_name, self.email, self.skills_tech)

    def get_id(self):
        return self.id

data = {
    'full_name': ['Juan Pérez', 'María López', 'Carlos Fernández', 'Ana Gómez', 'Ricardo Martínez',
                        'Laura Hernández', 'José Ramírez', 'Sofía Torres', 'Diego Sánchez', 'Elena García',
                        'Pedro Gómez', 'Isabel Vargas', 'Fernando Castillo', 'Luisa Méndez',
                        'Francisco Reyes', 'Gloria Suárez', 'Alberto Silva', 'Clara Romero',
                        'Victor Ruiz', 'Daniela Medina'],
    'email': ['juan.perez@email.com', 'maria.lopez@email.com', 'carlos.fernandez@email.com', 'ana.gomez@email.com',
              'ricardo.martinez@email.com', 'laura.hernandez@email.com', 'jose.ramirez@email.com',
              'sofia.torres@email.com', 'diego.sanchez@email.com', 'elena.garcia@email.com',
              'pedro.gomez@email.com', 'isabel.vargas@email.com', 'fernando.castillo@email.com',
              'luisa.mendez@email.com', 'francisco.reyes@email.com', 'gloria.suarez@email.com',
              'alberto.silva@email.com', 'clara.romero@email.com', 'victor.ruiz@email.com',
              'daniela.medina@email.com'],
    'skills_tech': ['Python, Django, Flask, PostgreSQL', 'JavaScript, React, Node.js, MongoDB',
                    'Java, Spring, Hibernate, MySQL', 'C#, .NET, ASP.NET, SQL Server',
                    'Ruby, Rails, PostgreSQL, Redis', 'PHP, Laravel, Vue.js, MySQL',
                    'Kotlin, Android, Firebase, SQLite', 'Swift, iOS, Core Data, Xcode',
                    'JavaScript, Angular, TypeScript, CSS', 'Python, Machine Learning, TensorFlow, PyTorch',
                    'Go, Docker, Kubernetes, AWS', 'C++, Qt, OpenGL, Boost', 'Scala, Akka, Play Framework, Kafka',
                    'JavaScript, Vue.js, Nuxt.js, Firebase, Java', 'Java, Spring Boot, Microservices, Kafka',
                    'Python, Flask, PostgreSQL, Docker', 'JavaScript, Node.js, Express.js, MongoDB',
                    'PHP, Symfony, MySQL, Redis', 'Rust, WebAssembly, Actix, PostgreSQL',
                    'Ruby, Rails, Heroku, PostgreSQL']
}

# Crear la lista de candidatos
list_candidatos = [Candidato(data['full_name'][i], data['email'][i], data['skills_tech'][i].split(', ')) for i in range(len(data['full_name']))]
list_candidatos.append(Candidato('Gonzalo Martin','gonzalojavimartin@gmail.com',['PHP','SQL','Bootstrap']))

def get_candidato_by_email(email):
    for candidato in list_candidatos:
        if candidato.email == email:
            return candidato

def update_cadidato_by_email(applicant):
    for candidato in list_candidatos:
        if candidato.email == applicant.email:
            candidato.skills_tech = applicant.skills_tech
            break