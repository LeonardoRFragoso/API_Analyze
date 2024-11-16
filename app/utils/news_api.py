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
        start_date (datetime.date | str, optional): Data de início como objeto datetime.date ou string.
        end_date (datetime.date | str, optional): Data de fim como objeto datetime.date ou string.

    Returns:
        list: Lista de dicionários contendo os artigos encontrados ou uma lista vazia.
    """
    if not fii_code:
        raise ValueError("O parâmetro 'fii_code' é obrigatório.")
    
    # Garantir que as datas estão no formato correto
    def format_date(date):
        if isinstance(date, datetime.date):
            return date.strftime("%Y-%m-%d")
        elif isinstance(date, str):
            try:
                datetime.datetime.strptime(date, "%Y-%m-%d")
                return date
            except ValueError:
                raise ValueError("A data deve estar no formato 'YYYY-MM-DD' ou ser um objeto datetime.date.")
        return None

    start_date_str = format_date(start_date)
    end_date_str = format_date(end_date)

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
            st.warning(f"Nenhum artigo encontrado para o código '{fii_code}'.")
            return []

    except requests.exceptions.RequestException as req_err:
        st.error(f"Erro ao buscar notícias: {req_err}")
    
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
        if article.get('url'):
            st.write(f"[Leia mais]({article.get('url')})")
        if article.get('urlToImage'):
            st.image(article['urlToImage'], use_column_width=True)
        st.markdown("---")
