import re

import numpy as np
import pandas as pd


def get_technologies():
    dataset = pd.read_csv('static/datasets/sysarmy_encuesta_salarial_2024.1.csv')
    column_mapping = {
        'lenguajes_de_programacion_o_tecnologias_que_utilices_en_tu_puesto_actual': "lenguajes_tecnologias",
        'bases_de_datos': "bases_de_datos",
        'plataformas_que_utilizas_en_tu_puesto_actual' : 'plataformas',
        'frameworksherramientas_y_librerias_que_utilices_en_tu_puesto_actual' : 'frameworks',
        'qa_testing' : 'qa_testing'
    }
    dataset = dataset.rename(columns=column_mapping)

    plataformas_dict = {}

    palabras_a_excluir = {
        ' ', '--',
        '.jira service desk .uso de herramienta vnc viewer y remote desktop para conexiones remotas .uso de herramienta advanced host monitor para monitoreo de redes .configuración de impresoras.manejo de active directory',
        '11', 'aadd', 'otro', 'otros', 'arduino o similar', 'cms propio de la empresa', 'crm desarollo interno',
        'electrónica', 'erp de la empresa', 'jarvis(interno de la empresa)',
        'mmmmm', 'ninguna de las anteriores', 'no lo se', 'noc',
        'plataforma de la compañía que funciona sobre aws y gcp', 'plataforma propia de la empresa',
        'plataformas custom de esta empresa',
        'propia de la empresa', 'propietarios', 'relacionados a data',
        'se utiliza azure pero yo actualmente no tengo proyecto', 'software empresarial', 'soluciones hcis philips',
        'un dashboard de la empresa', 'una plataforma hecha por la propia empresa',
        'zoho one y otras apps de zoho: salesiq', 'no aplica al puesto', 'por lo general opensource',
        'ventas productos y servicios', 'estoy en Design'
    }

    # Recorrer la columna y agregar las plataformas a la lista, asegurando que se guarden en su forma original
    dataset['plataformas'].dropna().apply(
        lambda x: [
            plataformas_dict.setdefault(item.strip().lower(), item.strip())
            for item in re.split(r'[;,|/]', str(x))  # Usar re.split para dividir por múltiples separadores
            if len(item.strip()) > 1 and item.strip().lower() not in palabras_a_excluir
        ]
    )

    # Obtener la lista de plataformas únicas en su forma original
    plataformas_lista = list(plataformas_dict.values())
    plataformas_lista.remove('estoy en Design')

    frameworks_dict = {}

    palabras_a_excluir = {
        ' ', 'todo', 'in-house', 'plant applications', 'deja', 'para', 'ninguno',
        'seleccionar', 'solución', 'librerias', 'adelante', 'ninguna', 'aplica',
        'no', 'se', 'sé', 'programador', 'uso', 'otro', 'otros', 'estoy',
        'privado', 'propio', 'creados', 'sgsgsgsgd', '.net framework 4 en adelante', 'estoy en design',
        'framework privado de la empresa', 'framework propio', 'frameworks de go o creados en la compañía',
        'frameworks php y javascript in-house', 'ge plant applications. osi pi.',
        'ktor y vertex para kotlin', 'librerías y frameworks de smalltalk',
        'mi puesto es comercial. vendo un producto desarrollado en la empresa',
        'ninguno de los anteriores', 'ningúna', 'no aplica', 'no aplica al puesto',
        'no deja seleccionar react', 'no lo se', 'no lo sé', 'no soy programador',
        'no uso', 'performarce)', 'solución de workflow', 'son boludos? revisen el formulario'
    }

    # Recorrer la columna y agregar los frameworks/herramientas a la lista, asegurando que se guarden en su forma original
    dataset['frameworks'].dropna().apply(
        lambda x: [
            frameworks_dict.setdefault(item.strip().lower(), item.strip())
            for item in re.split(r'[;,|/]', str(x))  # Usar re.split para dividir por múltiples separadores
            if len(item.strip()) > 1 and item.strip().lower() not in palabras_a_excluir
        ]
    )

    # Obtener la lista de frameworks únicos en su forma original
    frameworks_lista = list(frameworks_dict.values())

    lenguajes = set()

    palabras_a_excluir = {
        ' ', 'el de la propia empresa', 'estoy actualmente haciendo un curso de html con css',
        'estoy en design', 'front (integracion de servicios', 'fsdgsdggd',
        'mi puesto es comercial. vendo un producto desarrollado en la empresa', 'ninguno de los anteriores',
        'no aplica al puesto', 'no aplican', 'no soy programador',
        'otro', 'python muy basico', 'venta dev a medida y productos', 'otros',
        'sql', 'html', 'css', 'Nose'
    }

    # Recorrer la columna y agregar los lenguajes/herramientas a la lista
    dataset['lenguajes_tecnologias'].dropna().apply(
        lambda x: lenguajes.update(set([
            item.strip() for item in re.split(r'[;,|/]', str(x))  # Usar re.split para dividir por múltiples separadores
            if len(item.strip()) > 1 and item.strip().lower() not in palabras_a_excluir
        ]))
    )

    # Convertir el conjunto (set) en una lista y ordenar alfabéticamente
    lenguajes_lista = sorted(list(lenguajes))

    databases = set()

    palabras_a_excluir = {
        ' ', 'api de la companía que interactúa con dbs en aws', 'base de datos nativa de vfp',
        'dgsdgsdgdfdfh', 'la propia de salesforce',
        'ninguna de las anteriores', 'no aplica', 'no lo se con seguridad',
        'no manejo db en este proyecto', 'no sé', 'no uso',
        'sistema de la empresa (fury)', 'sistema interno de la compañía',
        'otro', 'otros', 'mi puesto es comercial. vendo un producto desarrollado en la empresa',
        'usamos kvs(key value store)', 'ninguna de las anteriores', 'no aplica al puesto',
    }

    # Convertir palabras a excluir a minúsculas
    palabras_a_excluir = {palabra.lower() for palabra in palabras_a_excluir}

    # Recorrer la columna y agregar las bases de datos a la lista
    dataset['bases_de_datos'].dropna().apply(
        lambda x: databases.update(set([
            item.strip() for item in re.split(r'[;,|/]', str(x))  # Usar re.split para dividir por múltiples separadores
            if len(item.strip()) > 1 and item.lower() not in palabras_a_excluir
            # Comprobar en minúsculas para exclusión
        ]))
    )

    # Convertir el conjunto (set) en una lista y ordenar alfabéticamente
    databases_lista = sorted(list(databases))
    databases_lista.remove('Ninguna de las anteriores')

    qa = set()

    palabras_a_excluir = {
        ' ', '--', 'de eso se encargan los qas', 'desconozco', 'estoy en design',
        'excel y test manuales. horrible', 'mi puesto es comercial. vendo un producto desarrollado en la empresa',
        'ninguna', 'ningunas', 'ninguno', 'ningúna', 'no aplica al puesto',
        'no aplican', 'no estoy segura', 'no hago testing', 'no se',
        'no soy tester', 'no sé 🤷', 'no usamos', 'no usamos testing',
        'no utilizo', 'otro', 'playwright (alternativa a selenium)',
        'qatesting manual', 'qmetry en jira', 'somos re suicidas....',
        'somos una empresa en la que todo se testea mal',
        'son boludos? revisen el formulario', 'test suite in sap solution manager',
        'testing de golang', 'testing library', 'testing manual',
        'testing-library', 'todo', 'tests para los controladores de salesforce (apex/java)',
        'otro', 'otros', 'ninguna de las anteriores', 'no uso', 'somos una empresa en la que todo se testea mal'
    }

    # Recorrer la columna y agregar los QA a la lista
    dataset['qa_testing'].dropna().apply(
        lambda x: qa.update(set([
            item.strip() for item in re.split(r'[;,|/]', str(x))  # Usar re.split para dividir por múltiples separadores
            if len(item.strip()) > 1 and item.lower() not in palabras_a_excluir and not item.lower().startswith('somos')
            # Comprobar en minúsculas para exclusión y evitar que inicie con "somos"
        ]))
    )

    # Convertir el conjunto (set) en una lista y ordenar alfabéticamente
    qa_lista = sorted(list(qa))
    qa_lista.remove('somos re suicidas....')
    qa_lista.remove('somos una empresa en la que todo se testea mal')

    list_techs = sorted(list(set(plataformas_lista + frameworks_lista + lenguajes_lista + databases_lista + qa_lista)))
    list_techs.remove('Ninguna de las anteriores')

    return list_techs