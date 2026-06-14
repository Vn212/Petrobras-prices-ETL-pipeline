from src.extract import main_extract
from src.transform import main_transform
from src.load_data import carregar_dados
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
load_dotenv(env_path)

table_name = 'precos_combustiveis'

def pipeline():
    try:
        logging.info("Iniciando pipeline ETL...")
        
        logging.info("Iniciando etapa de extração dos dados...")
        main_extract()
        
        logging.info("Iniciando etapa de transformação dos dados...")
        df_final = main_transform()
        
        logging.info("Iniciando etapa de carregamento dos dados...")
        carregar_dados(table_name, df_final)
        
        logging.info("Pipeline ETL concluída com sucesso!")

    except Exception as e:
        logging.error(f"Erro na pipeline ETL: {e}")
        import traceback
        traceback.print_exc()

pipeline()