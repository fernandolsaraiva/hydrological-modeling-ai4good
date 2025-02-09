""""This script inserts the critical levels to the database."""

import json
import os

import psycopg2

data = {
    "Ribeirão dos Couros - Piraporinha Casa Grande": {
        "ATENÇÃO": 761.54,
        "ALERTA": 761.94,
        "EMERGENCIA": 762.34,
        "EXTRAVAZAMENTO": 762.74
    },
    "Ribeirão dos Couros - Mercedes Paulicéia": {
        "ATENÇÃO": 752.02,
        "ALERTA": 752.42,
        "EMERGENCIA": 752.82,
        "EXTRAVAZAMENTO": 753.22
    },
    "Ribeirão dos Couros - Ford": {
        "ATENÇÃO": 3.82,
        "ALERTA": 4.82,
        "EMERGENCIA": 5.81,
        "EXTRAVAZAMENTO": 6.82
    },
    "Rio Tamanduateí - Vila Santa Cecilia": {
        "ATENÇÃO": 756.65,
        "ALERTA": 757.15,
        "EMERGENCIA": 757.65,
        "EXTRAVAZAMENTO": 758.15
    },
    "Ribeirão dos Meninos - Volks Demarch": {
        "ATENÇÃO": 773.4,
        "ALERTA": 773.8,
        "EMERGENCIA": 774.2,
        "EXTRAVAZAMENTO": 774.6
    },
    "Ribeirão Vermelho - Anhanguera": {
        "ATENÇÃO": 1.93,
        "ALERTA": 2.33,
        "EMERGENCIA": 2.73,
        "EXTRAVAZAMENTO": 3.13
    },
    "Rio Tamanduateí - Montante AT -09 Guamiranga": {
        "ATENÇÃO": 1000,
        "ALERTA": 1001,
        "EMERGENCIA": 1002,
        "EXTRAVAZAMENTO": 3
    },
    "Rio Tamanduateí - Jusante AT -09 Guamiranga": {
        "ATENÇÃO": 1000,
        "ALERTA": 1001,
        "EMERGENCIA": 1002,
        "EXTRAVAZAMENTO": 3
    },
    "Rio Tamanduateí - Prosperidade": {
        "ATENÇÃO": 2.95,
        "ALERTA": 3.55,
        "EMERGENCIA": 4.15,
        "EXTRAVAZAMENTO": 4.75
    },
    "Rio Aricanduva - Foz": {
        "ATENÇÃO": 4.35,
        "ALERTA": 4.95,
        "EMERGENCIA": 5.55,
        "EXTRAVAZAMENTO": 6.15
    },
    "Ribeirão dos Couros - Jd Taboão": {
        "ATENÇÃO": 741.05,
        "ALERTA": 741.41,
        "EMERGENCIA": 742.78,
        "EXTRAVAZAMENTO": 742.14
    },
    "Córrego Oratório - Vila Prudente": {
        "ATENÇÃO": 737.7,
        "ALERTA": 738.0,
        "EMERGENCIA": 738.3,
        "EXTRAVAZAMENTO": 738.6
    },
    "Rio Tamanduateí - Vd. Pacheco Chaves": {
        "ATENÇÃO": 726.2,
        "ALERTA": 726.9,
        "EMERGENCIA": 727.6,
        "EXTRAVAZAMENTO": 728.3
    },
    "Rio Tamanduateí - Mercado Municipal": {
        "ATENÇÃO": 6.09,
        "ALERTA": 6.89,
        "EMERGENCIA": 7.69,
        "EXTRAVAZAMENTO": 8.49
    },
    "Córrego Água Espraiada - Cabeceira": {
        "ATENÇÃO": 1.8,
        "ALERTA": 2.25,
        "EMERGENCIA": 2.7,
        "EXTRAVAZAMENTO": 3.15
    },
    "Córrego Ipiranga - Pç. Leonor Kaupa": {
        "ATENÇÃO": 730.75,
        "ALERTA": 731.2,
        "EMERGENCIA": 731.65,
        "EXTRAVAZAMENTO": 732.0
    },
    "Córrego Moinho Velho - R. Dois de Julho": {
        "ATENÇÃO": 1000,
        "ALERTA": 1001,
        "EMERGENCIA": 1002,
        "EXTRAVAZAMENTO": 3
    }
}

if __name__ == "__main__":
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    for station_name, critical_levels in data.items():
        print('Inserting critical levels for', station_name)
        cursor.execute("""
            UPDATE station.station_flu
            SET critical_levels = %s
            WHERE name = %s
        """, (json.dumps(critical_levels, ensure_ascii=False), station_name))

    conn.commit()
    cursor.close()
    conn.close()
