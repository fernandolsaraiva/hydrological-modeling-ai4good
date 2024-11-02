import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def getJson(url):
    s = requests.Session()
    s.get(url)
    json_value = s.get(url).content.decode("utf-8")
    return json_value

def getDate():
    date = datetime.utcnow() # current date and time
    return date

def getNivel(date):
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    date_yesterday = date-timedelta(days=1)
    year_yesterday = date_yesterday.strftime("%Y")
    month_yesterday = date_yesterday.strftime("%m")
    day_yesterday = date_yesterday.strftime("%d")

    #Posto 33767 é a estação 413
    url = f"http://sibh.daee.sp.gov.br/grafico_nivel_novo.csv?postos[]=33767&periodo={day_yesterday}/{month_yesterday}/{year_yesterday}%20-%20{day}/{month}/{year}&tipo_dados=coleta&formato=1"
    json_value = getJson(url)
    print(json_value)
    # with open(r"/Users/fernandosaraiva/Desktop/ai4good/hydrological-modeling-ai4good/data/Nivel.csv","w") as file:
    #     file.write(json_value + "\n")
    # df = pd.read_csv(r"/Users/fernandosaraiva/Desktop/ai4good/hydrological-modeling-ai4good/data/Nivel.csv")
    # if df.empty:
    #     print('Não há dados disponíveis')
    #     last_level = last_time = json_value = None
    #     return last_level,last_time,json_value
    # last_level = df['valor_leitura_flu'].iloc[-1]
    # last_time = df['intervalo'].iloc[-1]
    # print('Last available river level: ',last_level)
    # print('Last available time: ',last_time)
    # return last_level,last_time,json_value

if __name__ == '__main__':
    date = getDate()    
    getNivel(date)
    #nivel,time,json_value = getNivel(date)
    print('Concluído')