import datetime
import requests
import streamlit as st

# Obtém a chave da API dos segredos do Streamlit
NEWS_API_KEY = st.secrets["news"]["api_key"]

def fetch_financial_news(fii_code, start_date=None, end_date=None):
    """
    Busca notícias relacionadas ao código do FII ou ação utilizando a NewsAPI.

    Args:
        fii_code (str): Código do FII ou ação para buscar notícias.
        start_date (datetime.date, optional): Data de início como objeto datetime.date.
        end_date (datetime.date, optional): Data de fim como objeto datetime.date.

    Returns:
        list: Lista de dicionários contendo os artigos encontrados ou uma lista vazia.
    """
    if not fii_code:
        raise ValueError("O parâmetro 'fii_code' é obrigatório.")
    
    # Converte as datas para strings no formato 'YYYY-MM-DD'
    start_date_str = start_date.strftime("%Y-%m-%d") if start_date else None
    end_date_str = end_date.strftime("%Y-%m-%d") if end_date else None

    # Monta a URL da API
    url = f"https://newsapi.org/v2/everything?q={fii_code}&apiKey={NEWS_API_KEY}"
    if start_date_str:
        url += f"&from={start_date_str}"
    if end_date_str:
        url += f"&to={end_date_str}"
    
    try:
        # Faz a requisição GET à API
        response = requests.get(url, timeout=10)  # Define timeout para evitar requisições travadas
        response.raise_for_status()  # Lança exceção para status de erro (4xx, 5xx)
        
        # Processa a resposta JSON
        data = response.json()
        
        # Valida a presença dos artigos no retorno
        articles = data.get("articles", [])
        if articles:
            return articles
        else:
            st.warning("Nenhum artigo encontrado para o código fornecido.")
            return []

    except requests.exceptions.HTTPError as http_err:
        st.error(f"Erro HTTP: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        st.error(f"Erro de conexão: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        st.error(f"Erro de timeout: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Erro inesperado: {req_err}")
    
    return []

def display_news(articles):
    """
    Exibe notícias formatadas no Streamlit.

    Args:
        articles (list): Lista de dicionários contendo informações dos artigos.
    """
    if not articles:
        st.warning("Nenhuma notícia disponível para exibição.")
        return

    for article in articles:
        # Converte a data do artigo para um formato legível
        published_date = article.get('publishedAt', None)
        if published_date:
            try:
                published_date = datetime.datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%SZ")
                published_date = published_date.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                published_date = "Data inválida"

        st.write(f"### {article.get('title', 'Título não disponível')}")
        st.write(f"**Fonte:** {article.get('source', {}).get('name', 'Desconhecida')}")
        st.write(f"**Publicado em:** {published_date}")
        st.write(f"**Descrição:** {article.get('description', 'Sem descrição disponível.')}")
        st.write(f"[Leia mais]({article.get('url')})")
        st.markdown("---")
