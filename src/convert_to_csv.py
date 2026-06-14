import pandas as pd
import os

# Caminho dentro do container
parquet_path = "/opt/airflow/src/precos_combustiveis.parquet"
csv_path = "/opt/airflow/src/precos_combustiveis.csv"

if os.path.exists(parquet_path):
    df = pd.read_parquet(parquet_path)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print("Sucesso!")
else:
    print(f"Erro: Arquivo {parquet_path} nao encontrado.")
