import requests

NEWS_API_KEY = '03c157bae35443e2911d2f8b34323ae6'  # Substitua pela sua chave da API

# Função para buscar notícias financeiras
def fetch_financial_news(fii_code, start_date=None, end_date=None):
    """
    Busca notícias relacionadas ao código do FII ou ação utilizando a NewsAPI.
    
    :param fii_code: Código do FII ou Ação para buscar notícias.
    :param start_date: Data de início opcional (não utilizado diretamente na NewsAPI).
    :param end_date: Data de fim opcional (não utilizado diretamente na NewsAPI).
    :return: Lista de artigos encontrados ou lista vazia se não houver resultados.
    """
    url = f"https://newsapi.org/v2/everything?q={fii_code}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        return []
