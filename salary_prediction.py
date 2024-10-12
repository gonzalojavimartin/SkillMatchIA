import pandas as pd
from static.models.salary_prediction.salary_prediction_terms import *

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

def setup_input_model(job_position,seniority,gender,dedication,experience,technologies):
    df = pd.DataFrame([{
        "trabajo_de": job_position,
        "dedicacion": dedication,
        "seniority": seniority,
        "genero": gender,
        "rango_experiencia": experience,
        'plataformas_sisop': 0,
        'plataformas_container': 0,
        'plataformas_cloud': 0,
        'plataformas_virtualization': 0,
        'lenguajes_dev_web_front': 0,
        'lenguajes_dev_web_back': 0,
        'lenguajes_dev_desktop_app': 0,
        'lenguajes_dev_scripting': 0,
        'framework_front': 0,
        'framework_back': 0,
        'framework_webmaster': 0,
        'databases_sql': 0,
        'databases_nosql': 0,
        'qa_testing_api': 0,
        'qa_testing_unit': 0,
        'qa_testing_auto': 0
    }])

    technologies = pd.DataFrame(technologies)

    df['plataformas_sisop'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in sisop_terms) else 0
    )

    df['plataformas_container'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in container_terms) else 0
    )

    df['plataformas_cloud'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in cloud_terms) else 0
    )

    df['plataformas_virtualization'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in virtualization_terms) else 0
    )
    
    df['lenguajes_dev_web_front'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in dev_front_terms) else 0
    )

    df['lenguajes_dev_web_back'] = technologies.apply(
        lambda x: 1 if (
                any(term in str(x).lower() for term in dev_back_terms) or
                ('java' in str(x).lower() and (str(x).strip().lower() == 'java' or str(x).lower().endswith('java,')))
        ) else 0
    )

    df['lenguajes_dev_desktop_app'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in dev_desktop_terms) else 0
    )

    df['lenguajes_dev_scripting'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in dev_scripting_terms) else 0
    )

    df['framework_front'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in front_terms) else 0
    )

    df['framework_back'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in back_terms) else 0
    )

    df['framework_webmaster'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in webmaster_terms) else 0
    )
    
    df['databases_sql'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in sql_terms) else 0
    )

    df['databases_nosql'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in nosql_terms) else 0
    )
    
    df['qa_testing_api'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in api_terms) else 0
    )

    df['qa_testing_unit'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in unit_terms) else 0
    )

    df['qa_testing_auto'] = technologies.apply(
        lambda x: 1 if any(term in str(x).lower() for term in auto_terms) else 0
    )

    return df