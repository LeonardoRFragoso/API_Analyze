import streamlit as st
import yfinance as yf
import pandas as pd

# Utilitário para formatação
def format_currency(value):
    """
    Formata um número para moeda brasileira (R$).
    """
    if value is None or value == 'N/A':
        return 'N/A'
    return f"R${value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Função genérica para exibir tabelas
def display_table(data, title, index_name=None, column_name=None, format_func=None):
    """
    Exibe uma tabela formatada com título e opções de formatação.
    """
    st.subheader(title)
    if data is None or data.empty:
        st.warning("Nenhum dado disponível")
    else:
        if format_func:
            data = data.applymap(format_func)
        if index_name:
            data.index.name = index_name
        if column_name:
            data.columns = [column_name]
        st.dataframe(data)

# Exibe dados de preço formatados
def display_price_table(data):
    """
    Exibe uma tabela de dados de preço formatados.
    """
    if data is not None:
        formatted_data = data.copy()
        for col in ['Open', 'High', 'Low', 'Close']:
            formatted_data[col] = formatted_data[col].apply(format_currency)
        display_table(formatted_data, "Tabela de Preços", index_name="Data")

# Exibe tabela de dividendos
def display_dividends_table(dividends, ticker_code):
    """
    Exibe o histórico de dividendos formatados.
    """
    if dividends is None or dividends.empty:
        st.warning(f"Nenhum dado de dividendos disponível para {ticker_code}")
    else:
        display_table(
            dividends,
            f"Histórico de Dividendos de {ticker_code}",
            index_name="Data",
            column_name="Dividendos (R$)",
            format_func=format_currency
        )

# Busca e exibe o valor de mercado
def display_market_value(ticker_code):
    """
    Exibe o valor de mercado de um ativo, com fallback em caso de dados ausentes.
    """
    try:
        ticker = yf.Ticker(ticker_code)
        market_info = ticker.info
        market_cap = market_info.get('marketCap', None)
        st.subheader(f"Valor de Mercado de {ticker_code}")
        if market_cap:
            st.write(f"Valor de Mercado: {format_currency(market_cap)}")
        else:
            st.warning("Valor de mercado não disponível.")
    except Exception as e:
        st.error(f"Erro ao buscar o valor de mercado para {ticker_code}: {str(e)}")

# Exibe gráficos de preço
def display_price_chart(data):
    """
    Exibe um gráfico de preços com dados de fechamento.
    """
    if data is not None and not data.empty:
        st.line_chart(data['Close'])
    else:
        st.warning("Nenhum dado de preços disponível para o gráfico.")

# Função para download dos dados como CSV
def download_data_as_csv(data, filename):
    """
    Permite o download dos dados exibidos em formato CSV.
    """
    csv = data.to_csv(index=False)
    st.download_button(
        label="Baixar como CSV",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

# Função principal
def main():
    st.title("Análise de Mercado")
    st.sidebar.header("Configurações")

    # Seletor de ativo
    ticker_code = st.sidebar.text_input("Código do ativo", value="PETR4.SA")

    # Seletor de intervalo de datas
    start_date = st.sidebar.date_input("Data de Início", value=pd.Timestamp('2022-01-01'))
    end_date = st.sidebar.date_input("Data de Fim", value=pd.Timestamp.today())

    # Carrega dados do Yahoo Finance
    try:
        ticker = yf.Ticker(ticker_code)
        historical_data = ticker.history(start=start_date, end=end_date)
        dividends = ticker.dividends

        # Exibe os dados
        st.header(f"Análise para {ticker_code}")
        display_market_value(ticker_code)
        display_price_chart(historical_data)
        display_price_table(historical_data)
        display_dividends_table(dividends, ticker_code)

        # Download dos dados
        st.subheader("Download dos Dados")
        if not historical_data.empty:
            download_data_as_csv(historical_data, f"{ticker_code}_precos.csv")
        if not dividends.empty:
            download_data_as_csv(dividends, f"{ticker_code}_dividendos.csv")
    except Exception as e:
        st.error(f"Erro ao carregar dados para {ticker_code}: {str(e)}")

if __name__ == "__main__":
    main()
