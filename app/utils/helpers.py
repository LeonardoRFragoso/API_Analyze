import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from utils.database import fetch_and_save_dividends

# Chave da API Alpha Vantage
ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage"]["api_key"]

# Função genérica para exibir tabelas
def display_table(data, title, filename, column_format=None, sort_by_date=True, descending=True, height=400, key=None):
    """
    Exibe uma tabela formatada e permite download como CSV.

    Args:
        data (pd.DataFrame): Dados para exibição.
        title (str): Título da tabela.
        filename (str): Nome do arquivo para download.
        column_format (dict, optional): Formatação personalizada para colunas.
        sort_by_date (bool, optional): Ordenar os dados pela coluna 'Data'.
        descending (bool, optional): Ordenar em ordem decrescente.
        height (int, optional): Altura da tabela exibida.
        key (str, optional): Chave única para evitar re-renderizações no Streamlit.
    """
    st.subheader(title)

    if data is None or data.empty:
        st.error("Nenhum dado disponível para exibição.")
        return

    # Resetar índice se for DatetimeIndex
    if isinstance(data.index, pd.DatetimeIndex):
        data = data.reset_index()

    # Renomear colunas (de inglês para português, se aplicável)
    column_mapping = {
        'Date': 'Data',
        'Open': 'Abertura',
        'High': 'Máxima',
        'Low': 'Mínima',
        'Close': 'Fechamento',
        'Volume': 'Volume',
        'Dividends': 'Dividendos',
        'Stock Splits': 'Desdobramentos',
    }
    data = data.rename(columns={col: column_mapping.get(col, col) for col in data.columns})

    # Ordenar dados pela coluna 'Data', se solicitado
    if sort_by_date and 'Data' in data.columns:
        data['Data'] = pd.to_datetime(data['Data'], errors='coerce')
        data = data.sort_values(by='Data', ascending=not descending)
        data['Data'] = data['Data'].dt.strftime('%d/%m/%Y')

    # Aplicar formatação personalizada, se especificado
    if column_format:
        for col, fmt in column_format.items():
            if col in data.columns:
                data[col] = data[col].apply(fmt)

    # Exibir a tabela e permitir download em CSV
    st.dataframe(data, height=height, use_container_width=True)
    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button("Exportar para CSV", csv, file_name=filename, mime="text/csv", key=key)

# Função para exibir dividendos
def display_dividends(ticker_code, conn):
    """
    Exibe dividendos de um ativo com suporte para download em CSV.

    Args:
        ticker_code (str): Código do ativo.
        conn: Conexão com o banco de dados.
    """
    dividends = fetch_and_save_dividends(conn, ticker_code)
    if dividends is not None and not dividends.empty:
        dividends = dividends.reset_index()
        dividends.columns = ['Data', 'Dividendos']
        dividends['Data'] = pd.to_datetime(dividends['Data'], errors='coerce').dt.strftime('%d/%m/%Y')
        dividends['Dividendos'] = dividends['Dividendos'].apply(lambda x: f'R${x:,.2f}')
        display_table(
            dividends,
            f"Histórico de Dividendos de {ticker_code}",
            f"{ticker_code}_dividends.csv",
            sort_by_date=True,
            descending=True
        )
    else:
        st.warning(f"Nenhum dado de dividendos disponível para {ticker_code}.")

# Função para exibir valor de mercado
def display_market_value(ticker_code):
    """
    Exibe o valor de mercado do ativo, com fallback para Alpha Vantage.

    Args:
        ticker_code (str): Código do ativo.
    """
    try:
        ticker = yf.Ticker(ticker_code)
        market_info = ticker.info
        market_cap = market_info.get('marketCap', None)
        st.subheader(f"Valor de Mercado de {ticker_code}")

        if market_cap:
            st.write(f"R${market_cap:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        else:
            st.warning(f"Valor de mercado não disponível para {ticker_code}. Tentando Alpha Vantage...")
            fallback_to_alpha_vantage(ticker_code)
    except Exception as e:
        st.error(f"Erro ao buscar valor de mercado para {ticker_code}: {str(e)}")
        fallback_to_alpha_vantage(ticker_code)

# Fallback para Alpha Vantage
def fallback_to_alpha_vantage(ticker_code):
    """
    Faz uma requisição à API Alpha Vantage para obter o valor de mercado.

    Args:
        ticker_code (str): Código do ativo.
    """
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker_code}&apikey={ALPHA_VANTAGE_API_KEY}'
    try:
        response = requests.get(url)
        data = response.json()
        if 'MarketCapitalization' in data:
            market_cap = float(data['MarketCapitalization'])
            st.write(f"R${market_cap:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        else:
            st.warning(f"Alpha Vantage não retornou o valor de mercado para {ticker_code}.")
    except Exception as e:
        st.error(f"Erro ao buscar valor de mercado via Alpha Vantage: {str(e)}")

# Função para exibir relatórios financeiros
def display_financial_statements(ticker_code):
    """
    Exibe relatórios financeiros, como DRE, balanço patrimonial e fluxo de caixa.

    Args:
        ticker_code (str): Código do ativo.
    """
    ticker = yf.Ticker(ticker_code)

    def export_and_display(data, title, filename):
        if data is not None and not data.empty:
            st.subheader(title)
            st.dataframe(data, use_container_width=True)
            csv = data.to_csv().encode('utf-8')
            st.download_button(f"Exportar {title} para CSV", csv, file_name=filename, mime="text/csv")
        else:
            st.warning(f"Nenhum dado disponível para {title}.")

    export_and_display(ticker.financials, f"Relatório Financeiro de {ticker_code}", f"{ticker_code}_financials.csv")
    export_and_display(ticker.balance_sheet, f"Balanço Patrimonial de {ticker_code}", f"{ticker_code}_balance_sheet.csv")
    export_and_display(ticker.cashflow, f"Fluxo de Caixa de {ticker_code}", f"{ticker_code}_cashflow.csv")
    export_and_display(ticker.earnings, f"Rendimentos Trimestrais de {ticker_code}", f"{ticker_code}_earnings.csv")

    recommendations = ticker.recommendations
    if recommendations is not None and not recommendations.empty:
        export_and_display(recommendations, f"Recomendações de Analistas de {ticker_code}", f"{ticker_code}_recommendations.csv")
    else:
        st.warning(f"Nenhuma recomendação de analistas disponível para {ticker_code}.")
