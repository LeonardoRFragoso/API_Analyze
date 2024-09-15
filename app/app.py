import streamlit as st
import datetime
import plotly.graph_objects as go
from utils.database import init_db, get_stock_data, load_dividend_data, fetch_and_save_dividends, save_dividend_data
from utils.indicators import add_indicators
from plots.plot_functions import plot_graph
from utils.assets import FII_LIST, STOCK_LIST
import yfinance as yf

# Função para exportar os dados como CSV
def export_data(data, filename="data.csv", key=None):
    """Função para exportar dados como CSV com chave única"""
    csv = data.to_csv().encode('utf-8')
    st.download_button("Exportar Dados para CSV", csv, file_name=filename, mime="text/csv", key=key)

# Função para exibir a tabela de preços formatada
def display_price_table(data, key=None):
    """Função para exibir a tabela de preços formatada"""
    data_display = data.copy()
    for col in ['Open', 'High', 'Low', 'Close']:
        data_display[col] = data_display[col].apply(lambda x: f'R${x:,.2f}')
    st.write("Dados de Preço")
    st.dataframe(data_display)
    export_data(data_display, key=key)

# Função para exibir a tabela de dividendos
def display_dividends_table(dividends, ticker_code, key=None):
    if dividends is None or dividends.empty:
        st.warning(f"Nenhum dado de dividendos disponível para {ticker_code}")
    else:
        st.subheader(f"Histórico de Dividendos de {ticker_code}")
        dividends_formatted = dividends.apply(lambda x: f'R${x:,.2f}')
        dividends_formatted.index.name = 'Data'
        dividends_formatted.name = 'Dividendos por Cota (R$)'
        st.dataframe(dividends_formatted)
        export_data(dividends_formatted, filename=f"{ticker_code}_dividends.csv", key=key)

# Função para exibir o valor de mercado
def display_market_value(ticker_code):
    ticker = yf.Ticker(ticker_code)

    try:
        # Buscar informações de mercado (com tratamento de erro)
        market_info = ticker.get_info()
        market_cap = market_info.get('marketCap', None)
        st.subheader(f"Valor de Mercado de {ticker_code}")

        if market_cap:
            st.write(f"R${market_cap:,.2f}")
        else:
            st.write("Informação de valor de mercado não disponível.")
    
    except Exception as e:
        st.error(f"Erro ao buscar valor de mercado: {e}")

# Função para buscar dividendos e salvar no banco
def fetch_and_save_dividends(conn, ticker):
    try:
        ticker_data = yf.Ticker(ticker)
        dividends = ticker_data.dividends
        
        if dividends is not None and not dividends.empty:
            save_dividend_data(conn, ticker, dividends)
            return dividends
        else:
            st.warning(f"Nenhum dado de dividendos disponível para {ticker}.")
            return None
    except Exception as e:
        st.error(f"Erro ao buscar dividendos para {ticker}: {e}")
        return None

# Função principal
def main():
    conn = init_db()  # Inicializa o banco de dados
    st.title("Analisador de FIIs e Ações - Acompanhamento Completo")

    # Criação das abas
    tab1, tab2 = st.tabs(["Análise Individual", "Comparação"])

    with tab1:
        st.sidebar.title("Configurações de Visualização")
        asset_type = st.sidebar.selectbox("Escolha o tipo de ativo", ["FIIs", "Ações"])
        asset_list = FII_LIST if asset_type == "FIIs" else STOCK_LIST

        ticker_code_input = st.selectbox(f"Selecione o {asset_type[:-1]} para Análise", asset_list)
        plot_type = st.sidebar.radio("Escolha o Tipo de Gráfico", ["Candle", "Linha"])
        interval = st.sidebar.selectbox("Escolha o Intervalo de Tempo", ["1d", "1h", "5m"])
        sma_period = st.sidebar.number_input("Período da SMA (Média Móvel Simples)", min_value=5, max_value=200, step=1, value=20)
        ema_period = st.sidebar.number_input("Período da EMA (Média Móvel Exponencial)", min_value=5, max_value=200, step=1, value=20)
        start_date = st.sidebar.date_input("Data de Início", datetime.date(2022, 1, 1))
        end_date = st.sidebar.date_input("Data de Fim", datetime.date.today())

        if st.button("Analisar"):
            data = get_stock_data(ticker_code_input, start_date, end_date, interval, conn)
            if data is not None:
                # Adicionar indicadores técnicos
                data = add_indicators(data, sma_period, ema_period)
                st.subheader(f"Dados de Preço de {ticker_code_input}")
                display_price_table(data, key=f"price_table_{ticker_code_input}")
                plot_graph(data, f'{ticker_code_input} - Variação de Preço', 'Preço (R$)', plot_type, sma=sma_period, ema=ema_period)

                # Buscar dividendos e exibir
                dividends = fetch_and_save_dividends(conn, ticker_code_input)
                display_dividends_table(dividends, ticker_code_input, key=f"dividends_table_{ticker_code_input}")
                
                # Exibir valor de mercado
                display_market_value(ticker_code_input)

    with tab2:
        st.sidebar.title("Configurações de Comparação")
        selected_assets = st.multiselect(f"Selecione os {asset_type} para Comparação", asset_list)

        if st.button("Comparar"):
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
                    display_dividends_table(dividends, asset_code, key=f"dividends_table_{asset_code}")
                    display_market_value(asset_code)

if __name__ == "__main__":
    main()
