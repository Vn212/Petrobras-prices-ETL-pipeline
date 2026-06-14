import pandas as pd
import os

parquet_path = os.path.join("src", "precos_combustiveis.parquet")
csv_path = "precos_combustiveis.csv"

if os.path.exists(parquet_path):
    df = pd.read_parquet(parquet_path)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print("Sucesso!")
else:
    print("Erro: Arquivo Parquet nao encontrado.")
