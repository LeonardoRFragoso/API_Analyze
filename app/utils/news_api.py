import datetime
import requests
import streamlit as st  # Importa o `streamlit` para acessar os segredos

# Pega a chave da API diretamente dos segredos no Streamlit Cloud
NEWS_API_KEY = st.secrets["news"]["api_key"]

# Função para buscar notícias financeiras
def fetch_financial_news(fii_code, start_date=None, end_date=None):
    """
    Busca notícias relacionadas ao código do FII ou ação utilizando a NewsAPI.
    
    :param fii_code: Código do FII ou Ação para buscar notícias.
    :param start_date: Data de início opcional (não utilizado diretamente na NewsAPI).
    :param end_date: Data de fim opcional (não utilizado diretamente na NewsAPI).
    :return: Lista de artigos encontrados ou lista vazia se não houver resultados.
    """
    # Monta a URL da API
    url = f"https://newsapi.org/v2/everything?q={fii_code}&apiKey={NEWS_API_KEY}"

    # Se as datas forem fornecidas, adiciona os parâmetros de data na URL
    if start_date and end_date:
        url += f"&from={start_date}&to={end_date}"

    try:
        # Faz a requisição GET à API
        response = requests.get(url)
        response.raise_for_status()  # Lança exceção para status de erro (4xx, 5xx)
        
        # Retorna os artigos encontrados, se houver
        articles = response.json().get("articles", [])
        return articles
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Erros HTTP (404, 500, etc.)
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Error connecting to the API: {conn_err}")  # Erros de conexão
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error: {timeout_err}")  # Erros de timeout
    except requests.exceptions.RequestException as req_err:
        print(f"General error: {req_err}")  # Outros erros relacionados ao request
    
    return []
