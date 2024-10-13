import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Cargamos el modelo y los codificadores entrenados
data = pd.read_csv('static/datasets/2024.1_encuesta-sysarmy.csv')

# Seleccion de columnas relevantes y preprocesamiento
relevant_columns = [
    'trabajo_de',
    'dedicacion',
    'seniority',
    'anos_de_experiencia',
    'me_identifico_genero',
    'plataformas_que_utilizas_en_tu_puesto_actual',
    'lenguajes_de_programacion_o_tecnologias_que_utilices_en_tu_puesto_actual',
    'frameworksherramientas_y_librerias_que_utilices_en_tu_puesto_actual',
    'bases_de_datos',
    'qa_testing',
    'ultimo_salario_mensual_o_retiro_bruto_en_tu_moneda_local'
]

filtered_data = data[relevant_columns].dropna()

columns_rename = {
    "ultimo_salario_mensual_o_retiro_bruto_en_tu_moneda_local" : "salario_bruto",
    "me_identifico_genero" : "genero",
    "anos_de_experiencia" : "experiencia",
    "plataformas_que_utilizas_en_tu_puesto_actual" : "plataformas",
    "lenguajes_de_programacion_o_tecnologias_que_utilices_en_tu_puesto_actual" : "lenguajes",
    "frameworksherramientas_y_librerias_que_utilices_en_tu_puesto_actual" : "frameworks",
    "bases_de_datos":"databases"
}

filtered_data.rename(columns=columns_rename, inplace=True)

# Filtrar y eliminar las filas donde 'salario_bruto' sea mayor a 75000 o menor a 550000
MIN_SAL = 775000
MAX_SAL = 1800000
filtered_data = filtered_data[(filtered_data['salario_bruto'] > MIN_SAL) & (filtered_data['salario_bruto'] < MAX_SAL)]

# Dropear filas donde las columnas especificadas sean nulas
filtered_data = filtered_data.dropna(subset=['plataformas','frameworks','databases','qa_testing'])

# Dada la disparidad de registros, llevo a "otros" aquellos registros con pocos registros
# Lista de categorías válidas
generos = ['Hombre Cis', 'Mujer Cis']

# Reemplazar valores no válidos por "Otros"
filtered_data['genero'] = filtered_data['genero'].apply(lambda x: 'Otro' if x not in generos else x)
filtered_data['genero'] = filtered_data['genero'].replace({
    "Hombre Cis": "Hombre",
    "Mujer Cis": "Mujer",
    "Otro": "Otro"
})

# Normalizar categorias experiencia
filtered_data['experiencia'] = pd.to_numeric(filtered_data['experiencia'], errors='coerce')

# Función para categorizar
def categorizar_experiencia(anos):
    if 1 <= anos <= 4:
        return "1_a_4"
    elif 5 <= anos <= 9:
        return "5_a_9"
    else:
        return "10_mas"

# Aplicar la función y crear la nueva columna
filtered_data['rango_experiencia'] = filtered_data['experiencia'].apply(categorizar_experiencia)

# Normalizar trabajo_de
top = filtered_data['trabajo_de'].value_counts().head(10).index.tolist()
# Filtrar el DataFrame para quedarnos solo con los registros de los 20 roles
filtered_data = filtered_data[filtered_data['trabajo_de'].isin(top)]

# Normalizar salario_bruto
filtered_data['salario_bruto'] = pd.to_numeric(filtered_data['salario_bruto'], errors='coerce')

#[('Linux', 827), ('Docker', 696), ('Amazon Web Services', 512), ('Windows Server', 510), ('Azure', 479), ('Google Cloud Platform', 310), ('VMWare', 275), ('Kubernetes', 253), ('SAP', 120), ('Firebase', 118)]

# Listas de términos para sistemas operativos, contenedores y cloud
sisop_terms = ['linux', 'windows server']
container_terms = ['docker', 'kubernetes']
cloud_terms = ['amazon web services', 'azure', 'google cloud platform', 'firebase']
virtualization_terms = ['vmware']

# Crear las nuevas columnas
filtered_data['plataformas_sisop'] = filtered_data['plataformas'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in sisop_terms) else 0
)

filtered_data['plataformas_container'] = filtered_data['plataformas'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in container_terms) else 0
)

filtered_data['plataformas_cloud'] = filtered_data['plataformas'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in cloud_terms) else 0
)

filtered_data['plataformas_virtualization'] = filtered_data['plataformas'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in virtualization_terms) else 0
)

# [('SQL', 998), ('Javascript', 813), ('HTML', 633), ('Python', 578), ('CSS', 432), ('TypeScript', 405), ('Java', 338), ('Bash/Shell', 319), ('PHP', 288), ('.NET', 251), ('C#', 200), ('VBA', 58), ('Go', 52)]

# Listas de términos para lenguajes web, software y sistemas
dev_front_terms = ['javascript', 'typescript', 'html', 'css']
dev_back_terms = ['sql','python', '.net', 'c#', 'go', 'java', 'php']
dev_desktop_terms = ['.net', 'vba', 'c#']
dev_scripting_terms = ['bash/shell']

# Crear las nuevas columnas
filtered_data['lenguajes_dev_web_front'] = filtered_data['lenguajes'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in dev_front_terms) else 0
)

filtered_data['lenguajes_dev_web_back'] = filtered_data['lenguajes'].apply(
    lambda x: 1 if (
        any(term in str(x).lower() for term in dev_back_terms) or
        ('java' in str(x).lower() and (str(x).strip().lower() == 'java' or str(x).lower().endswith('java,')))
    ) else 0
)

filtered_data['lenguajes_dev_desktop_app'] = filtered_data['lenguajes'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in dev_desktop_terms) else 0
)

filtered_data['lenguajes_dev_scripting'] = filtered_data['lenguajes'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in dev_scripting_terms) else 0
)

#[('Node.js', 417), ('React.js', 380), ('Bootstrap', 301), ('.NET Core', 227), ('Angular', 223), ('jQuery', 219), ('Next.js', 160), ('Spring', 154), ('WordPress', 150), ('Laravel', 103), ('Vue.js', 96), ('Django', 90), ('Hibernate', 85), ('Flask', 73)]

# Listas de términos para el front-end y back-end
front_terms = ['react.js', 'bootstrap', 'jquery', 'angular', 'next.js','vue.js']
back_terms = ['node.js', '.net core', 'spring', 'hibernate','laravel','django','hibernate','flask']
webmaster_terms = ['wordpress']

# Crear las nuevas columnas
filtered_data['framework_front'] = filtered_data['frameworks'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in front_terms) else 0
)

filtered_data['framework_back'] = filtered_data['frameworks'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in back_terms) else 0
)

filtered_data['framework_webmaster'] = filtered_data['frameworks'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in webmaster_terms) else 0
)

# ('MySQL', 685), ('Microsoft SQL Server', 619), ('PostgreSQL', 461), ('MongoDB', 290), ('MariaDB', 256), ('Oracle', 240), ('Microsoft Azure (Tables', 148), ('CosmosDB', 148), ('SQL', 148), ('SQLite', 144), ('Redis', 130), ('ElasticSearch', 101)
# Definir los términos para bases de datos SQL y NoSQL
sql_terms = ['mysql', 'microsoft sql server', 'postgresql', 'oracle', 'mariadb','sqlite','sql']
nosql_terms = ['mongodb', 'microsoft azure (tables', 'cosmosdb', 'elasticsearch', 'redis']

# Crear las columnas db_sql y db_nosql
filtered_data['databases_sql'] = filtered_data['databases'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in sql_terms) else 0
)

filtered_data['databases_nosql'] = filtered_data['databases'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in nosql_terms) else 0
)

# [('Postman', 435), ('Jest', 159), ('JUnit', 159), ('Selenium', 104), ('Cypress', 91), ('SoapUI', 81), ('Visual Studio Coded UI', 58), ('PHPUnit', 58), ('Cucumber', 47), ('Xunit', 28)]

# Definir los términos para las pruebas de QA
api_terms = ['postman','soapui']
unit_terms = ['junit', 'phpunit', 'jest', 'cucumber','xunit']
auto_terms = ['selenium', 'cypress', 'visual studio coded ui']

# Crear las columnas qa_api, qa_unit y qa_auto
filtered_data['qa_testing_api'] = filtered_data['qa_testing'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in api_terms) else 0
)

filtered_data['qa_testing_unit'] = filtered_data['qa_testing'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in unit_terms) else 0
)

filtered_data['qa_testing_auto'] = filtered_data['qa_testing'].apply(
    lambda x: 1 if any(term in str(x).lower() for term in auto_terms) else 0
)

df_modificado = filtered_data.copy()

label_encoders_text = {
    'trabajo_de': filtered_data['trabajo_de'].unique(),
    'dedicacion': filtered_data['dedicacion'].unique(),
    'seniority': filtered_data['seniority'].unique(),
    'rango_experiencia': filtered_data['rango_experiencia'].unique(),
    'genero': filtered_data['genero'].unique(),
}

label_encoders = {
    'trabajo_de': LabelEncoder(),
    'dedicacion': LabelEncoder(),
    'seniority': LabelEncoder(),
    'rango_experiencia': LabelEncoder(),
    'genero': LabelEncoder(),
}

for column, encoder in label_encoders.items():
    df_modificado[column] = encoder.fit_transform(filtered_data[column])
    mapping_df = pd.DataFrame({column: label_encoders[column].classes_, 'encoding': range(len(label_encoders[column].classes_))})
    filepath = 'static/models/' + column + '.csv'
    mapping_df.to_csv(filepath, index=False)

columns_categoricas = ['experiencia','plataformas','lenguajes','frameworks','databases','qa_testing']

df_modificado.drop(columns=columns_categoricas, inplace=True)

TARGET = label_encoders['trabajo_de'].transform(["Developer"])[0]
# Calcular el número de filas a eliminar para trabajo_de = TARGET
num_filas_a_eliminar = int(len(df_modificado[df_modificado['trabajo_de'] == TARGET]) * 0.4)

# Eliminar filas aleatorias para trabajo_de = TARGET
filas_a_eliminar = df_modificado[df_modificado['trabajo_de'] == TARGET].sample(n=num_filas_a_eliminar, random_state=1)
df_modificado = df_modificado.drop(filas_a_eliminar.index)

# Creamos y entrenamos un modelo de Regresión Lineal para predecir los salarios.
X = df_modificado.drop(columns=['salario_bruto'])  # Variables predictoras
y = df_modificado['salario_bruto']  # Variable objetivo

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Crear y ajustar el modelo de regresión lineal para salario_bruto
modelo = LinearRegression()
modelo.fit(X_train, y_train)

#Guardo el modelo
joblib.dump(modelo, 'static/models/salary_prediction/salary_prediction_linear_regression.pkl')
