import streamlit as st
import datetime
from utils.database import get_stock_data
from utils.indicators import add_indicators
from plots.plot_functions import plot_graph
from utils.helpers import display_table, display_market_value, display_dividends  # Certifique-se de importar a função correta
from utils.assets import FII_LIST, STOCK_LIST

def render_analysis_tab(conn):
    # Título da seção na barra lateral
    st.sidebar.title("Configurações de Visualização para Análise")

    # Escolha do tipo de ativo (FIIs ou Ações)
    asset_type = st.sidebar.selectbox("Escolha o tipo de ativo", ["FIIs", "Ações"], key="selectbox1")
    asset_list = FII_LIST if asset_type == "FIIs" else STOCK_LIST

    # Seleção do ativo específico (por ticker)
    ticker_code_input = st.selectbox(f"Selecione o {asset_type[:-1]} para Análise", asset_list, key="selectbox2")

    # Configurações de gráficos e indicadores
    plot_type = st.sidebar.radio("Escolha o Tipo de Gráfico", ["Candle", "Linha"], key="plot_type")
    interval = st.sidebar.selectbox("Escolha o Intervalo de Tempo", ["1d", "1h", "5m"], key="interval")
    sma_period = st.sidebar.number_input("Período da SMA (Média Móvel Simples)", min_value=5, max_value=200, step=1, value=20, key="sma_period")
    ema_period = st.sidebar.number_input("Período da EMA (Média Móvel Exponencial)", min_value=5, max_value=200, step=1, value=20, key="ema_period")

    # Configurações de data (data de início e data de fim)
    start_date = st.sidebar.date_input("Data de Início", value=datetime.date(2022, 1, 1), key="start_date")
    end_date = st.sidebar.date_input("Data de Fim", value=datetime.date.today(), key="end_date")

    # Botão para iniciar a análise
    if st.button("Analisar", key="analyze_button"):
        # Buscar os dados do ativo para o período selecionado
        data = get_stock_data(ticker_code_input, start_date, end_date, interval, conn)

        if data is not None:
            # Adicionar indicadores (SMA e EMA) aos dados
            data = add_indicators(data, sma_period, ema_period)

            # Exibir tabela de preços formatada
            display_table(
                data, 
                f"Dados de Preço de {ticker_code_input}", 
                f"{ticker_code_input}_prices.csv", 
                column_format={
                    'Abertura': lambda x: f'R${x:,.2f}', 
                    'Máxima': lambda x: f'R${x:,.2f}', 
                    'Mínima': lambda x: f'R${x:,.2f}', 
                    'Fechamento': lambda x: f'R${x:,.2f}'
                }, 
                key=f"price_table_{ticker_code_input}"
            )

            # Exibir gráfico de preços
            plot_graph(data, f'{ticker_code_input} - Variação de Preço', 'Preço (R$)', plot_type, sma=sma_period, ema=ema_period)

            # Exibir dividendos (se disponíveis)
            display_dividends(ticker_code_input, conn)

            # Exibir o valor de mercado do ativo
            display_market_value(ticker_code_input)
        else:
            st.error(f"Não foi possível carregar os dados para {ticker_code_input}. Verifique o ticker ou tente novamente mais tarde.")
