import streamlit as st
import yfinance as yf
import pandas as pd

# Utilitário para formatação de valores
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
        st.dataframe(data, use_container_width=True)

# Exibe tabela de preços formatados
def display_price_table(data):
    """
    Exibe uma tabela de dados de preços formatados.
    """
    if data is not None and not data.empty:
        formatted_data = data.copy()
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in formatted_data.columns:
                formatted_data[col] = formatted_data[col].apply(format_currency)
        display_table(formatted_data, "Tabela de Preços", index_name="Data")

# Exibe tabela de dividendos
def display_dividends_table(dividends, ticker_code):
    """
    Exibe o histórico de dividendos formatados.
    """
    if dividends is None or dividends.empty:
        st.warning(f"Nenhum dado de dividendos disponível para {ticker_code}.")
    else:
        formatted_dividends = dividends.reset_index()
        formatted_dividends.columns = ['Data', 'Dividendos']
        formatted_dividends['Data'] = pd.to_datetime(formatted_dividends['Data']).dt.strftime('%d/%m/%Y')
        formatted_dividends['Dividendos'] = formatted_dividends['Dividendos'].apply(format_currency)
        display_table(
            formatted_dividends,
            f"Histórico de Dividendos de {ticker_code}",
            index_name="Data",
            column_name="Dividendos (R$)"
        )

# Busca e exibe o valor de mercado
def display_market_value(ticker_code):
    """
    Exibe o valor de mercado de um ativo.
    """
    try:
        ticker = yf.Ticker(ticker_code)
        market_cap = ticker.info.get('marketCap', None)
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
    if data is not None and 'Close' in data.columns:
        st.line_chart(data['Close'])
    else:
        st.warning("Nenhum dado de preços disponível para o gráfico.")

# Função para download dos dados como CSV
def download_data_as_csv(data, filename):
    """
    Permite o download dos dados exibidos em formato CSV.
    """
    csv = data.to_csv(index=True).encode('utf-8')
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

    if start_date > end_date:
        st.error("A data de início não pode ser maior que a data de fim.")
        return

    # Carrega dados do Yahoo Finance
    try:
        ticker = yf.Ticker(ticker_code)
        historical_data = ticker.history(start=start_date, end=end_date)
        dividends = ticker.dividends

        st.header(f"Análise para {ticker_code}")
        display_market_value(ticker_code)

        # Exibe gráfico de preços e tabela
        if not historical_data.empty:
            display_price_chart(historical_data)
            display_price_table(historical_data)
            download_data_as_csv(historical_data, f"{ticker_code}_precos.csv")
        else:
            st.warning("Nenhum dado de preço disponível para o intervalo selecionado.")

        # Exibe tabela de dividendos
        if not dividends.empty:
            display_dividends_table(dividends, ticker_code)
            download_data_as_csv(dividends.reset_index(), f"{ticker_code}_dividendos.csv")
        else:
            st.warning("Nenhum dado de dividendos disponível para o intervalo selecionado.")
    except Exception as e:
        st.error(f"Erro ao carregar dados para {ticker_code}: {str(e)}")

if __name__ == "__main__":
    main()
