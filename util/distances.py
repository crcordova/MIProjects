import requests
import pandas as pd

def get_distance_matrix(cities):
    # Hacer una solicitud a la API con la lista de ciudades

    # Verificar si la solicitud fue exitosa
    if response.status_code != 200:
        raise Exception(f'Error with request: {response.content}')

    # Parsear la respuesta a una lista de filas
    rows = response.json()['choices'][0]['text'].strip().split('\n')[2:-2]
    rows = [row.strip().split() for row in rows]

    # Crear el DataFrame a partir de la lista de filas
    df = pd.DataFrame(data=rows[1:], columns=rows[0])
    df.index = rows[0]
    df = df.astype(int)
    return df
