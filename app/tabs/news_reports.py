import streamlit as st
from utils.news_api import fetch_financial_news
from utils.assets import FII_LIST, STOCK_LIST
from utils.helpers import display_financial_statements
import datetime

def render_news_reports_tab(conn):
    """
    Renderiza a aba de Notícias e Relatórios Financeiros no Streamlit.

    Args:
        conn: Conexão com o banco de dados (não utilizado diretamente nesta aba, mas pode ser usado no futuro).
    """
    st.sidebar.title("Configurações de Notícias e Relatórios")

    # Seleção do tipo de ativo e lista correspondente
    asset_type_news = st.sidebar.selectbox(
        "Escolha o tipo de ativo para ver notícias", ["FIIs", "Ações"]
    )
    asset_list_news = FII_LIST if asset_type_news == "FIIs" else STOCK_LIST

    # Seleção do ativo
    asset_code = st.sidebar.selectbox(
        f"Escolha o {asset_type_news[:-1]} para ver notícias", asset_list_news
    )

    # Seleção da data de início para busca de notícias
    start_date_news = st.sidebar.date_input(
        "Data de Início", value=datetime.date.today()
    )

    # Botão para buscar notícias
    if st.button("Buscar Notícias"):
        st.info(f"Buscando notícias para {asset_code} desde {start_date_news}. Por favor, aguarde...")

        try:
            news = fetch_financial_news(asset_code, start_date_news)

            if news:
                st.subheader(f"Notícias Recentes sobre {asset_code}")
                for article in news:
                    st.markdown(f"### {article['title']}")
                    st.markdown(f"*Fonte: {article['source']['name']}*")
                    st.markdown(f"**Publicado em:** {article['publishedAt'][:10]}")
                    st.markdown(f"{article['description']}")
                    st.markdown(f"[Leia mais]({article['url']})")
                    if 'urlToImage' in article and article['urlToImage']:
                        st.image(article['urlToImage'], use_column_width=True)
                    st.markdown("---")
            else:
                st.warning(f"Não foram encontradas notícias recentes para {asset_code} desde {start_date_news}.")

        except Exception as e:
            st.error(f"Ocorreu um erro ao buscar notícias: {e}")

    # Botão para buscar relatórios financeiros
    if st.button("Buscar Relatórios Financeiros"):
        st.info(f"Buscando relatórios financeiros para {asset_code}. Por favor, aguarde...")

        try:
            st.subheader(f"Relatórios Financeiros de {asset_code}")
            display_financial_statements(asset_code)
        except Exception as e:
            st.error(f"Ocorreu um erro ao buscar relatórios financeiros: {e}")
