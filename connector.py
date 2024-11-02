from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import OperationalError

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    # Conecte-se ao banco
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("Conexão com o banco de dados bem-sucedida!")
except OperationalError as e:
    print("Erro ao conectar ao banco de dados:", e)