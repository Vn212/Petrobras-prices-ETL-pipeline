# %%
from pathlib import Path
import pandas as pd
import logging
from numpy import datetime64
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

colunas_remover = [
    'Preço Médio Gasolina',
    'Preço Médio Diesel',
    'Período de coleta'
]

colunas_renomear = {
    'Preço Médio Brasil': 'preco_medio_brasil', 
    'Distribuição': 'distribuicao', 
    'Porcentagem Distribuição': 'porcentagem_distribuicao',
    'Custo do etanol anidro': 'custo_etanol_anidro',
    'Porcentagem Custo do etanol anidro': 'porcentagem_custo_etanol_anidro',
    'Imposto Estadual': 'icms',
    'Porcentagem Imposto Estadual': 'porcentagem_icms',
    'Imposto Federal': 'imposto_federal', 
    'Porcentagem Impostos Federais': 'porcentagem_impostos_federais',
    'Parcela Petrobras': 'parcela_petrobras', 
    'Porcentagem Parcela Petrobras': 'porcentagem_parcela_petrobras', 
    'Biodiesel': 'biodiesel',
    'Porcentagem Biodiesel': 'porcentagem_biodiesel',
    'Porcentagem ICMS': 'porcentagem_icms',
    'ICMS': 'icms',
}

def separar_data(df):

    df["data_inicio"] = None
    df["data_fim"] = None

    if "Período de coleta" not in df.columns:
        return df

    regex_data = r'(\d{2}/\d{2}/\d{4})'

    datas_encontradas = df["Período de coleta"].astype(str).str.findall(regex_data)

    df["data_inicio"] = datas_encontradas.apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    df["data_fim"] = datas_encontradas.apply(
        lambda x: x[1] if isinstance(x, list) and len(x) > 1 else None
    )

    df["data_inicio"] = df["data_inicio"].replace(["None", "nan", "nao encontrado"], None)
    df["data_fim"] = df["data_fim"].replace(["None", "nan", "nao encontrado"], None)

    return df

def juntar_dados(dados) -> pd.DataFrame:
    dfs = []

    for tipo, data in dados.items():
        df = pd.json_normalize(data)
        df = separar_data(df)
        
        df["combustivel"] = tipo
        
        mapa_colunas = {
            "Imposto Estadual": "ICMS",
            "Porcentagem Imposto Estadual": "Porcentagem ICMS",
        }
        df.rename(columns=mapa_colunas, inplace=True)
        
        dfs.append(df)

    df_final = pd.concat(dfs, ignore_index=True)
    logging.info("DataFrames juntados com sucesso.")

    return df_final

def remover_colunas(df, colunas_remover) -> pd.DataFrame:
    logging.info("Removendo colunas...")
    df.drop(columns=colunas_remover, inplace=True, errors='ignore')
    logging.info("Colunas removidas com sucesso.")
    return df

def renomear_colunas(df, colunas_renomear) -> pd.DataFrame:

    logging.info("Renomeando colunas...")

    df.rename(columns=colunas_renomear, inplace=True)

    logging.info("Colunas renomeadas com sucesso.")

    return df

def transformar_float(valor):
    if pd.isna(valor) or str(valor).strip() in ["nao encontrado", ""]:
        return None
    try:
        limpo = str(valor).replace(",", ".").replace("%", "").strip()
        return float(limpo)
    except Exception as e:
        logging.debug(f"Falha ao converter '{valor}' para float: {e}")
        return None

def transformar_datetime(valor):
    if pd.isna(valor):
        return None
    try:
        return pd.to_datetime(valor, format="%d/%m/%Y")
    except:
        return None
      
def tratar_tipos(df) -> pd.DataFrame:
    df["data_inicio"] = df["data_inicio"].apply(transformar_datetime)
    df["data_fim"] = df["data_fim"].apply(transformar_datetime)

    for col in df.columns:
        if col not in ["data_inicio", "data_fim", "combustivel"]:
            df[col] = df[col].apply(transformar_float)
    
    logging.info("Tipos de dados tratados com sucesso.")

    return df

def validar_dados(df: pd.DataFrame):
    logging.info("Validando dados...")

    colunas_criticas = ["Preço Médio Brasil", "Período de coleta"]

    for col in colunas_criticas:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória ausente: {col}")

        if df[col].isnull().all():
            raise ValueError(f"Coluna {col} está totalmente nula")

    logging.info("Validação concluída com sucesso.")

def transformar_dados(dados):
    
    logging.info("Iniciando processo de transformação de dados...")

    df = juntar_dados(dados)
    validar_dados(df)
    df = remover_colunas(df, colunas_remover)
    df = tratar_tipos(df)
    df = renomear_colunas(df, colunas_renomear)
    
    logging.info("Processo de transformação de dados concluído com sucesso.")

    return df