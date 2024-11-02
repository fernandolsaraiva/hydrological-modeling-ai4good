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
    station = 33767 #Posto 33767 é a estação 413 (mercado municipal)
    url_new = f"https://cth.daee.sp.gov.br/sibh/api/v1/measurements/grouped?format=csv&start_date={year_yesterday}-{month_yesterday}-{day_yesterday}%2003%3A00&end_date={year}-{month}-{day}%2002%3A59&group_type=none&transmission_type_ids%5B%5D=1&transmission_type_ids%5B%5D=2&transmission_type_ids%5B%5D=3&transmission_type_ids%5B%5D=4&transmission_type_ids%5B%5D=5&transmission_type_ids%5B%5D=6&station_prefix_ids%5B%5D={station}"
    json_value = getJson(url_new)
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