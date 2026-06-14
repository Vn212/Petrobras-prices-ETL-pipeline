from datetime import datetime, timedelta
from marshal import load
from airflow.decorators import dag, task
from pathlib import Path
import sys, os
from dotenv import load_dotenv
import pandas as pd

sys.path.append('/opt/airflow')

from src.extract import main_extract
from src.transform import transformar_dados
from src.load_data import carregar_dados

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

@dag(

    dag_id='petrobras_dag',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        #'start_date': datetime(2024, 6, 1),
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    description='DAG para pipeline ETL de preços de combustíveis da Petrobras',
    schedule = '0 8 * * *',  # Executa diariamente às 8h
    start_date=datetime(2026, 4, 9),
    catchup=False,
    tags=['petrobras', 'etl', 'precos_combustiveis']
)

def petrobras_pipeline():

    @task()
    def extract():
        return main_extract()

    @task()
    def transform(dados):
        df = transformar_dados(dados)
        os.makedirs('/opt/airflow/data', exist_ok=True)
        df.to_parquet('/opt/airflow/data/precos_combustiveis.parquet', index=False)

    @task()
    def load():
        df = pd.read_parquet('/opt/airflow/data/precos_combustiveis.parquet')
        table_name = 'precos_combustiveis'
        carregar_dados(table_name, df)

    extract_output = extract()
    transform_output = transform(extract_output)

    transform_output >> load()

petrobras_pipeline()
