import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from scipy import stats
import numpy as np

# Cargamos el modelo y los codificadores entrenados
data = pd.read_csv('static/datasets/sysarmy_encuesta_salarial_2024.1.csv')

# Seleccion de columnas relevantes y preprocesamiento
relevant_columns = ['seniority', 'donde_estas_trabajando', 'me_identifico_genero',
                    'ultimo_salario_mensual_o_retiro_bruto_en_tu_moneda_local']
filtered_data = data[relevant_columns].dropna()

label_encoders = {
    'seniority': LabelEncoder(),
    'donde_estas_trabajando': LabelEncoder(),
    'me_identifico_genero': LabelEncoder()
}

def get_trained_model():

    for column, encoder in label_encoders.items():
        filtered_data[column] = encoder.fit_transform(filtered_data[column])

    X = filtered_data.drop(columns=['ultimo_salario_mensual_o_retiro_bruto_en_tu_moneda_local'])
    Y = filtered_data['ultimo_salario_mensual_o_retiro_bruto_en_tu_moneda_local']

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    return model

def get_job_positions():
    df = data
    conteo = df['trabajo_de'].value_counts()
    # Filtrar los valores que aparecen al menos 5 veces
    valores_minimo_5 = conteo[conteo >= 5].index.tolist()
    return valores_minimo_5

def get_seniorities():
    return data['seniority'].unique()

def get_genders():
    df = data
    conteo = df['me_identifico_genero'].value_counts()
    # Filtrar los valores que aparecen al menos 5 veces
    valores_minimo_5 = conteo[conteo >= 5].index.tolist()
    return valores_minimo_5

def get_cities():
    return data['donde_estas_trabajando'].unique()