import streamlit as st
from utils.news_api import fetch_financial_news
from utils.assets import FII_LIST, STOCK_LIST
from utils.helpers import display_financial_statements
import datetime  # Importar datetime para lidar com datas

def render_news_reports_tab(conn):
    st.sidebar.title("Configurações de Notícias e Relatórios")
    
    # Selecionar tipo de ativo e lista de ativos
    asset_type_news = st.sidebar.selectbox("Escolha o tipo de ativo para ver notícias", ["FIIs", "Ações"])
    asset_list_news = FII_LIST if asset_type_news == "FIIs" else STOCK_LIST
    
    # Selecionar ativo específico
    asset_code = st.sidebar.selectbox(f"Escolha o {asset_type_news[:-1]} para ver notícias", asset_list_news)
    
    # Data de início para as notícias, padrão para a data de hoje
    start_date_news = st.sidebar.date_input("Data de Início", value=datetime.date.today())  # Agora usa a data atual como padrão

    # Botão para buscar notícias
    if st.button("Buscar Notícias"):
        news = fetch_financial_news(asset_code, start_date_news)
        if news:
            st.subheader(f"Notícias Recentes sobre {asset_code}")
            for article in news:
                st.markdown(f"**{article['title']}**")
                st.markdown(f"*Fonte: {article['source']['name']} - {article['publishedAt']}*")
                st.markdown(f"{article['description']}")
                st.markdown(f"[Leia mais]({article['url']})")
        else:
            st.warning(f"Não foram encontradas notícias recentes para {asset_code} desde {start_date_news}.")

    # Botão para buscar relatórios financeiros
    if st.button("Buscar Relatórios Financeiros"):
        st.subheader(f"Relatórios Financeiros de {asset_code}")
        display_financial_statements(asset_code)  # Função para exibir os relatórios financeiros
