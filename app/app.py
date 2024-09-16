import streamlit as st
import datetime
import plotly.graph_objects as go
import yfinance as yf
import requests

from utils.database import init_db, get_stock_data, fetch_and_save_dividends, save_dividend_data
from utils.indicators import add_indicators
from plots.plot_functions import plot_graph
from utils.assets import FII_LIST, STOCK_LIST

NEWS_API_KEY = '03c157bae35443e2911d2f8b34323ae6'


# Função para exportar os dados como CSV
def export_data(data, filename="data.csv", key=None):
    csv = data.to_csv().encode('utf-8')
    st.download_button("Exportar Dados para CSV", csv, file_name=filename, mime="text/csv", key=key)


# Função para exibir tabelas formatadas (preços ou dividendos)
def display_table(data, title, filename, column_format=None, key=None):
    st.subheader(title)
    if column_format:
        data_display = data.copy()
        for col, fmt in column_format.items():
            data_display[col] = data_display[col].apply(fmt)
        st.dataframe(data_display)
    else:
        st.dataframe(data)

    export_data(data, filename, key=key)


# Função para exibir o valor de mercado
def display_market_value(ticker_code):
    ticker = yf.Ticker(ticker_code)
    try:
        market_info = ticker.get_info()
        market_cap = market_info.get('marketCap', None)
        st.subheader(f"Valor de Mercado de {ticker_code}")
        st.write(f"R${market_cap:,.2f}" if market_cap else "Informação de valor de mercado não disponível.")
    except Exception:
        st.error(f"Erro ao buscar valor de mercado para {ticker_code}. Por favor, tente novamente mais tarde.")


# Função para buscar notícias financeiras
def fetch_financial_news(asset_code):
    url = f"https://newsapi.org/v2/everything?q={asset_code}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("articles", [])
    return []


# Função utilitária para processar análise e visualização de ativos
def analyze_asset(ticker_code, start_date, end_date, interval, sma_period, ema_period, conn):
    data = get_stock_data(ticker_code, start_date, end_date, interval, conn)
    if data is not None:
        data = add_indicators(data, sma_period, ema_period)
        display_table(data, f"Dados de Preço de {ticker_code}", f"{ticker_code}_prices.csv", 
                      column_format={'Open': lambda x: f'R${x:,.2f}', 'High': lambda x: f'R${x:,.2f}', 
                                     'Low': lambda x: f'R${x:,.2f}', 'Close': lambda x: f'R${x:,.2f}'}, 
                      key=f"price_table_{ticker_code}")
        plot_graph(data, f'{ticker_code} - Variação de Preço', 'Preço (R$)', 'Candle', sma=sma_period, ema=ema_period)

        dividends = fetch_and_save_dividends(conn, ticker_code)
        if dividends is not None:
            display_table(dividends, f"Histórico de Dividendos de {ticker_code}", f"{ticker_code}_dividends.csv",
                          key=f"dividends_table_{ticker_code}")
        display_market_value(ticker_code)


# Função principal
def main():
    conn = init_db()  # Inicializa o banco de dados
    st.title("Analisador de FIIs e Ações - Acompanhamento Completo")

    # Criação das abas
    tab1, tab2, tab3 = st.tabs(["Análise Individual", "Comparação", "Notícias e Relatórios"])

    # Aba 1: Análise Individual
    with tab1:
        st.sidebar.title("Configurações de Visualização para Análise")
        asset_type = st.sidebar.selectbox("Escolha o tipo de ativo", ["FIIs", "Ações"], key="selectbox1")
        asset_list = FII_LIST if asset_type == "FIIs" else STOCK_LIST

        ticker_code_input = st.selectbox(f"Selecione o {asset_type[:-1]} para Análise", asset_list, key="selectbox2")
        plot_type = st.sidebar.radio("Escolha o Tipo de Gráfico", ["Candle", "Linha"], key="plot_type")
        interval = st.sidebar.selectbox("Escolha o Intervalo de Tempo", ["1d", "1h", "5m"], key="interval")
        sma_period = st.sidebar.number_input("Período da SMA (Média Móvel Simples)", min_value=5, max_value=200, step=1, value=20, key="sma_period")
        ema_period = st.sidebar.number_input("Período da EMA (Média Móvel Exponencial)", min_value=5, max_value=200, step=1, value=20, key="ema_period")
        start_date = st.sidebar.date_input("Data de Início", datetime.date(2022, 1, 1), key="start_date")
        end_date = st.sidebar.date_input("Data de Fim", datetime.date.today(), key="end_date")

        if st.button("Analisar", key="analyze_button"):
            analyze_asset(ticker_code_input, start_date, end_date, interval, sma_period, ema_period, conn)

    # Aba 2: Comparação
    with tab2:
        st.sidebar.title("Configurações de Visualização para Comparação")
        asset_type_comparison = st.sidebar.selectbox("Escolha o tipo de ativo para Comparação", ["FIIs", "Ações"], key="selectbox_comparison")
        asset_list_comparison = FII_LIST if asset_type_comparison == "FIIs" else STOCK_LIST
        selected_assets = st.multiselect(f"Selecione os {asset_type_comparison} para Comparação", asset_list_comparison, key="select_assets")

        if st.button("Comparar", key="compare_button"):
            data_dict = {}
            for asset_code in selected_assets:
                data = get_stock_data(asset_code, start_date, end_date, interval, conn)
                if data is not None:
                    data_dict[asset_code] = data

            if data_dict:
                fig = go.Figure()
                for asset, data in data_dict.items():
                    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=f'Preço {asset}'))
                fig.update_layout(title="Comparação de Preços", xaxis_title='Data', yaxis_title='Preço (R$)')
                st.plotly_chart(fig)

                # Exibir dividendos e valor de mercado para cada ativo
                for asset_code in selected_assets:
                    dividends = fetch_and_save_dividends(conn, asset_code)
                    display_table(dividends, f"Histórico de Dividendos de {asset_code}", f"{asset_code}_dividends.csv",
                                  key=f"dividends_table_{asset_code}")
                    display_market_value(asset_code)

    # Aba 3: Notícias e Relatórios
    with tab3:
        st.sidebar.title("Configurações de Notícias e Relatórios")
        
        # Permitir escolher entre FIIs e Ações para notícias
        asset_type_news = st.sidebar.selectbox("Escolha o tipo de ativo para ver notícias", ["FIIs", "Ações"], key="selectbox_news")
        asset_list_news = FII_LIST if asset_type_news == "FIIs" else STOCK_LIST
        fii_news_code = st.sidebar.selectbox(f"Escolha o {asset_type_news[:-1]} para ver notícias", asset_list_news, key="select_news_asset")

        if st.button("Buscar Notícias", key="news_button"):
            news = fetch_financial_news(fii_news_code)
            if news:
                st.subheader(f"Notícias Recentes sobre {fii_news_code}")
                for article in news:
                    st.markdown(f"**{article['title']}**")
                    st.markdown(f"*Fonte: {article['source']['name']} - {article['publishedAt']}*")
                    st.markdown(f"{article['description']}")
                    st.markdown(f"[Leia mais]({article['url']})")
            else:
                st.warning(f"Não foram encontradas notícias recentes para {fii_news_code}.")

if __name__ == "__main__":
    main()