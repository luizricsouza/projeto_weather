import requests
import csv
from elasticsearch import Elasticsearch
from datetime import datetime

api_key = "f7cd4c26331bfcf236d32f3f23637524"
units = "metric"
lang = "pt_br"
url = "https://api.openweathermap.org/data/2.5/weather"
coords_file = 'coordenadas_capitais_br.csv'
es = Elasticsearch("http://25.63.120.33:9200/")

def build_urls(url, api_key, units, lang, coords_file):
    urls_list = []

    with open(coords_file, 'r') as coord_csv:
        csv_content = csv.reader(coord_csv)
        next(csv_content)
        for line in csv_content:
            urls_list.append("{}?lat={}&lon={}&appid={}&units={}&lang={}".format(url, line[1], line[2], api_key, units, lang))

    return urls_list    
    
def call_weather_api(urls_list):
    docs_list = []

    for url in urls_list:
        req = requests.get(url)
        doc = req.json()
        docs_list.append(doc)

    return docs_list

def add_timestamp_field(docs_list):
    for doc in docs_list:
        doc['timestamp'] = datetime.utcfromtimestamp(doc['dt']).isoformat()

    return docs_list

for doc in docs_list:
    es_response = es.index(index="teste", document=doc)
    print(es_response['result'])