import pandas as pd

trabajo_de = pd.read_csv('static/models/salary_prediction/trabajo_de.csv')
dedicacion = pd.read_csv('static/models/salary_prediction/dedicacion.csv')
seniority = pd.read_csv('static/models/salary_prediction/seniority.csv')
genero = pd.read_csv('static/models/salary_prediction/genero.csv')
rango_experiencia = pd.read_csv('static/models/salary_prediction/rango_experiencia.csv')

def get_job_positions():
    return trabajo_de

def get_seniorities():
    return seniority

def get_genders():
    return genero

def get_dedications():
    return dedicacion

def get_experiences():
    return rango_experiencia

def get_label_by_encoding(target, encoding):
    if target == "job_position":
        df = trabajo_de
        label = 'trabajo_de'
    if target == "dedication":
        df = dedicacion
        label = 'dedicacion'
    if target == "seniority":
        df = seniority
        label = 'seniority'
    if target == "gender":
        df = genero
        label = 'genero'
    if target == "experience":
        df = rango_experiencia
        label = 'rango_experiencia'

    for index, row in df.iterrows():
        if row['encoding'] == int(encoding):
            return row[label]