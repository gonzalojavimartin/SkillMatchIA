import pandas as pd

def get_technologies():
    dataset = pd.read_csv('static/models/technologies.csv')
    list_techs = dataset['tech_terms'].tolist()
    list_techs = [term.lower() for term in list_techs]
    return list_techs