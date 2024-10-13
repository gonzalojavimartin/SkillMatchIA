import pandas as pd
from collections import Counter

data = pd.read_csv('static/datasets/2024.1_encuesta-sysarmy.csv')

relevant_columns = [
    'plataformas_que_utilizas_en_tu_puesto_actual',
    'lenguajes_de_programacion_o_tecnologias_que_utilices_en_tu_puesto_actual',
    'frameworksherramientas_y_librerias_que_utilices_en_tu_puesto_actual',
    'bases_de_datos',
    'qa_testing'
]

filtered_data = data[relevant_columns].dropna()

columns_rename = {
    "plataformas_que_utilizas_en_tu_puesto_actual" : "plataformas",
    "lenguajes_de_programacion_o_tecnologias_que_utilices_en_tu_puesto_actual" : "lenguajes",
    "frameworksherramientas_y_librerias_que_utilices_en_tu_puesto_actual" : "frameworks",
    "bases_de_datos":"databases"
}

filtered_data.rename(columns=columns_rename, inplace=True)


relevant_columns = [
    "plataformas",
    "lenguajes",
    "frameworks",
    "databases",
    "qa_testing"
]

tech_terms = []

for col in relevant_columns:
    column_terms = filtered_data[col].str.split(',').explode().str.strip()
    column_terms = column_terms[~column_terms.isin(['.','-','','Ninguna de las anteriores','Ninguno de los anteriores'])]
    for term in column_terms:
        tech_terms.append(term)

technologies = pd.DataFrame({ "tech_terms" : tech_terms })
most_common_techs = Counter(tech_terms).most_common(150)

aux = pd.DataFrame(most_common_techs)
techs_to_save = pd.DataFrame(aux[0])
techs_to_save.rename(columns={0 : 'tech_terms'}, inplace=True)
filepath = 'static/models/technologies.csv'
techs_to_save.to_csv(filepath, index=False)