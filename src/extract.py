from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

cookies = {
    'COOKIE_SUPPORT': 'true',
    '_ga': 'GA1.1.834207745.1773926834',
    '_gcl_au': '1.1.1067580283.1773926836',
    'tt.u': '0100007FB4F9BB696A06475A025C110C',
    'CONSENT_TYPE_FUNCTIONAL': 'false',
    'CONSENT_TYPE_PERFORMANCE': 'false',
    'CONSENT_TYPE_PERSONALIZATION': 'false',
    'CONSENT_TYPE_NECESSARY': 'true',
    'USER_CONSENT_CONFIGURED': 'true',
    'LFR_SESSION_STATE_20103': '1774306450343',
    '_clck': 'hx9ukg%5E2%5Eg4l%5E0%5E2269',
    'tt_c_vmt': '1774306451',
    'tt_c_c': 'direct',
    'tt_c_s': 'direct',
    'tt_c_m': 'direct',
    '_ttuu.s': '1774306451512',
    'tt.nprf': '',
    '_clsk': 'sjgd5v%5E1774306451849%5E1%5E1%5Eq.clarity.ms%2Fcollect',
    '_ga_G03L3SWZMG': 'GS2.1.s1774306450$o8$g1$t1774306733$j60$l0$h1993391523',
    'JSESSIONID': 'EC0D5EB7AE38C48F97C42E909BA0E3D0',
    'SERVER_ID': '11d6df3cc3106d9b',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    # 'cookie': 'COOKIE_SUPPORT=true; _ga=GA1.1.834207745.1773926834; _gcl_au=1.1.1067580283.1773926836; tt.u=0100007FB4F9BB696A06475A025C110C; CONSENT_TYPE_FUNCTIONAL=false; CONSENT_TYPE_PERFORMANCE=false; CONSENT_TYPE_PERSONALIZATION=false; CONSENT_TYPE_NECESSARY=true; USER_CONSENT_CONFIGURED=true; LFR_SESSION_STATE_20103=1774306450343; _clck=hx9ukg%5E2%5Eg4l%5E0%5E2269; tt_c_vmt=1774306451; tt_c_c=direct; tt_c_s=direct; tt_c_m=direct; _ttuu.s=1774306451512; tt.nprf=; _clsk=sjgd5v%5E1774306451849%5E1%5E1%5Eq.clarity.ms%2Fcollect; _ga_G03L3SWZMG=GS2.1.s1774306450$o8$g1$t1774306733$j60$l0$h1993391523; JSESSIONID=EC0D5EB7AE38C48F97C42E909BA0E3D0; SERVER_ID=11d6df3cc3106d9b',
}

def criar_sessao():
    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

session = criar_sessao()

def extrair_dados_gasolina(url) -> list:
    response = session.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        logging.error(f"Erro ao acessar a página: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    if soup is None:
        logging.error("Erro ao analisar o conteúdo da página")
        return []
    
    periodo_coleta = soup.find('span', {'data-lfr-editable-id': 'telafinal-textoColeta'})
    preco_medio_gasolina = soup.find('p', id='telafinal-precofinal')

    distribuicao = soup.find('span', id='telafinal-tarifa1-numero')
    custo_etanol_anidro = soup.find('span', id='telafinal-tarifa2-numero')
    icms = soup.find('span', id='telafinal-tarifa3-numero')
    imposto_federal = soup.find('span', id='telafinal-tarifa4-numero')
    parcela_petrobras = soup.find('span', id='telafinal-tarifa5-numero')

    distribuicao_porcentagem = soup.find('span',
        {'data-lfr-editable-id': 'telafinal-tarifa1-porcentagem'})
    custo_etanol_anidro_porcentagem = soup.find('span',
        {'data-lfr-editable-id': 'telafinal-tarifa2-porcentagem'})
    icms_porcentagem = soup.find('span',
        {'data-lfr-editable-id': 'telafinal-tarifa3-porcentagem'})
    imposto_federal_porcentagem = soup.find('span',
        {'data-lfr-editable-id': 'telafinal-tarifa4-porcentagem'})
    parcela_petrobras_porcentagem = soup.find('span',
        {'data-lfr-editable-id': 'telafinal-tarifa5-porcentagem'})

    preco_medio_brasil = soup.find('span', id='preçomedioBrasil')

    lista_dados = {
        "Período de coleta": periodo_coleta.text.strip() if periodo_coleta else None,
        "Preço Médio Brasil": preco_medio_brasil.text.strip() if preco_medio_brasil else None,
        "Preço Médio Gasolina": preco_medio_gasolina.text.strip() if preco_medio_gasolina else None,
        "Distribuição": distribuicao.text.strip() if distribuicao else None,
        "Porcentagem Distribuição": distribuicao_porcentagem.text.strip() if distribuicao_porcentagem else None,
        "Custo do etanol anidro": custo_etanol_anidro.text.strip() if custo_etanol_anidro else None,
        "Porcentagem Custo do etanol anidro": custo_etanol_anidro_porcentagem.text.strip() if custo_etanol_anidro_porcentagem else None,
        "ICMS": icms.text.strip() if icms else None,
        "Porcentagem ICMS": icms_porcentagem.text.strip() if icms_porcentagem else None,
        "Imposto Federal": imposto_federal.text.strip() if imposto_federal else None,
        "Porcentagem Impostos Federais": imposto_federal_porcentagem.text.strip() if imposto_federal_porcentagem else None,
        "Parcela Petrobras": parcela_petrobras.text.strip() if parcela_petrobras else None,
        "Porcentagem Parcela Petrobras": parcela_petrobras_porcentagem.text.strip() if parcela_petrobras_porcentagem else None
    }

    logging.info(f"Dados de Gasolina extraídos")

    return lista_dados

def extrair_dados_diesel(url) -> list:
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f"Erro ao acessar a página: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    if soup is None:
        logging.error("Erro ao analisar o conteúdo da página")
        return []
    
    preco_medio_diesel = soup.find('p', {'data-lfr-editable-id': 'telafinal-precofinal'})
    distribuicao = soup.find('span', {'data-lfr-editable-id': 'tarifa1-numero'})
    distribuicao_porcentagem = soup.find('span', {'data-lfr-editable-id': 'tarifa1-porcentagem'})
    biodiesel = soup.find ('span', {'data-lfr-editable-id': 'tarifa2-numero'})
    biodiesel_porcentagem = soup.find('span', {'data-lfr-editable-id': 'tarifa2-porcentagem'})
    imposto_estadual = soup.find('span', {'data-lfr-editable-id': 'tarifa3-numero'})
    imposto_estadual_porcentagem = soup.find('span', {'data-lfr-editable-id': 'tarifa3-porcentagem'})
    imposto_federais = soup.find('span', {'data-lfr-editable-id': 'tarifa4-numero'})
    imposto_federais_porcentagem = soup.find('span', {'data-lfr-editable-id': 'tarifa4-porcentagem'})
    parcela_petrobras = soup.find('span', {'data-lfr-editable-id': 'tarifa5-numero'})
    parcela_petrobras_porcentagem = soup.find('span', {'data-lfr-editable-id': 'tarifa5-porcentagem'})
    preco_medio_brasil = soup.find('span', {'data-lfr-editable-id': 'preçomedioBrasil'})
    periodo_coleta = soup.find ('span', {'data-lfr-editable-id': 'telafinal-textoColeta'})

    lista_dados = {
        "Período de coleta": periodo_coleta.text.strip() if periodo_coleta else None,
        "Preço Médio Brasil": preco_medio_brasil.text.strip() if preco_medio_brasil else 'nao encontrado',
        "Preço Médio Diesel": preco_medio_diesel.text.strip() if preco_medio_diesel else 'nao encontrado',
        "Distribuição": distribuicao.text.strip() if distribuicao else 'nao encontrado',
        "Porcentagem Distribuição": distribuicao_porcentagem.text.strip() if distribuicao_porcentagem else 'nao encontrado',
        "Biodiesel": biodiesel.text.strip() if biodiesel else 'nao encontrado',
        "Porcentagem Biodiesel": biodiesel_porcentagem.text.strip() if biodiesel_porcentagem else 'nao encontrado',
        "Imposto Estadual": imposto_estadual.text.strip() if imposto_estadual else 'nao encontrado',
        "Porcentagem Imposto Estadual": imposto_estadual_porcentagem.text.strip() if imposto_estadual_porcentagem else 'nao encontrado',
        "Imposto Federal": imposto_federais.text.strip() if imposto_federais else 'nao encontrado',
        "Porcentagem Impostos Federais": imposto_federais_porcentagem.text.strip() if imposto_federais_porcentagem else 'nao encontrado',
        "Parcela Petrobras": parcela_petrobras.text.strip() if parcela_petrobras else 'nao encontrado',
        "Porcentagem Parcela Petrobras": parcela_petrobras_porcentagem.text.strip() if parcela_petrobras_porcentagem else 'nao encontrado',
    }

    logging.info(f"Dados de Diesel extraídos")

    return lista_dados

def extrair_dados_glp(url) -> list:
    
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f"Erro ao acessar a página: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    if soup is None:
        logging.error("Erro ao analisar o conteúdo da página")
        return []
    
    preco_medio_glp= soup.find('p', {'data-lfr-editable-id': 'telafinal-precofinal'})
    distribuicao = soup.find('span', {'data-lfr-editable-id': 'tarifa2-numero'})
    distribuicao_porcentagem = soup.find('span', {'data-lfr-editable-id': 'tarifa2-porcentagem'})
    icms = soup.find ('span', {'data-lfr-editable-id': 'tarifa1-numero'})
    icms_porcentagem = soup.find('span', {'data-lfr-editable-id': 'tarifa1-porcentagem'})
    imposto_federais = soup.find('span', {'data-lfr-editable-id': 'tarifa4-numero'})
    imposto_federais_porcentagem = soup.find('span', {'data-lfr-editable-id': 'tarifa4-porcentagem'})
    parcela_petrobras = soup.find('span', {'data-lfr-editable-id': 'tarifa5-numero'})
    parcela_petrobras_porcentagem = soup.find('span', {'data-lfr-editable-id': 'tarifa5-porcentagem'})
    periodo_coleta = soup.find('span', {'data-lfr-editable-id': 'telafinal-textoColeta'})

    lista_dados = {
        "Período de coleta": periodo_coleta.text.strip() if periodo_coleta else None,
        "Preço Médio Brasil": preco_medio_glp.text.strip() if preco_medio_glp else 'nao encontrado',
        "Distribuição": distribuicao.text.strip() if distribuicao else 'nao encontrado',
        "Porcentagem Distribuição": distribuicao_porcentagem.text.strip() if distribuicao_porcentagem else 'nao encontrado',
        "ICMS": icms.text.strip() if icms else 'nao encontrado',
        "Porcentagem ICMS": icms_porcentagem.text.strip() if icms_porcentagem else 'nao encontrado',
        "Imposto Federal": imposto_federais.text.strip() if imposto_federais else 'nao encontrado',
        "Porcentagem Impostos Federais": imposto_federais_porcentagem.text.strip() if imposto_federais_porcentagem else 'nao encontrado',
        "Parcela Petrobras": parcela_petrobras.text.strip() if parcela_petrobras else 'nao encontrado',
        "Porcentagem Parcela Petrobras": parcela_petrobras_porcentagem.text.strip() if parcela_petrobras_porcentagem else 'nao encontrado',
    }

    logging.info(f"Dados de GLP extraídos")

    return lista_dados

def main_extract():
    
    url_gasolina = 'https://precos.petrobras.com.br/w/gasolina/br'
    url_diesel = 'https://precos.petrobras.com.br/w/diesel/br'
    url_glp =  'https://precos.petrobras.com.br/sele%C3%A7%C3%A3o-de-estados-glp'

    dados_gasolina = extrair_dados_gasolina(url_gasolina)
    time.sleep(10)
    dados_diesel = extrair_dados_diesel(url_diesel)
    time.sleep(10)
    dados_glp = extrair_dados_glp(url_glp)

    dados = {
        "gasolina": dados_gasolina,
        "diesel": dados_diesel,
        "glp": dados_glp
    }

    return dados

if __name__ == "__main__":
    main_extract()
