import requests
import csv
import schedule
import time
import logging
import re

from elasticsearch import Elasticsearch
from datetime import datetime

api_key = 'f7cd4c26331bfcf236d32f3f23637524'
units = 'metric'
lang = 'pt_br'
url = 'https://api.openweathermap.org/data/2.5/weather'
coords_file = 'coordenadas_capitais_br.csv'
es_host = 'http://25.63.120.33:9200/'
index = 'teste'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

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
        lat = re.search(r'lat=([-+]?\d*\.\d+|\d+)', url).group(1)
        lon = re.search(r'lon=([-+]?\d*\.\d+|\d+)', url).group(1)

        logging.info("Chamando API para as coordenadas {}, {}".format(lat, lon))

        response = requests.get(url)

        logging.info("Retorno da chama da api para as coordenadas {}, {}: {}".format(lat, lon, response.status_code))

        doc = response.json()
        docs_list.append(doc)

    return docs_list

def add_timestamp_field(docs_list):
    for doc in docs_list:
        doc['timestamp'] = datetime.utcfromtimestamp(doc['dt']).isoformat()

    logging.info("Campo timestamp adicionado aos documentos.")

    return docs_list

def send_to_elasticsearch(es_host, index, docs_list):
    es = Elasticsearch(es_host)

    for doc in docs_list:
        es_response = es.index(index=index, document=doc)
        logging.info("Resposta do elasticsearch: {}".format(es_response['result']))

def exec_task():
    urls = build_urls(url, api_key, units, lang, coords_file)
    docs = call_weather_api(urls)
    add_timestamp_field(docs)
    send_to_elasticsearch(es_host, index, docs)
    logging.info('Processo executado com sucesso.')
    
if __name__ == '__main__':
    schedule.every().hour.at(":05").do(exec_task)
    schedule.every().hour.at(":15").do(exec_task)
    schedule.every().hour.at(":25").do(exec_task)
    schedule.every().hour.at(":35").do(exec_task)
    schedule.every().hour.at(":45").do(exec_task)
    schedule.every().hour.at(":55").do(exec_task)

    while True:
        schedule.run_pending()
        time.sleep(1)