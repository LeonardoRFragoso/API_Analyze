import streamlit as st
import yfinance as yf
from utils.database import fetch_and_save_dividends
import pandas as pd
import requests

# Chave da API Alpha Vantage
ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage"]["api_key"]

# Função para exibir tabelas com dados de ações ou dividendos
def display_table(data, title, filename, column_format=None, key=None, sort_by_date=True, descending=True, height=400):
    st.subheader(title)

    if data is None or data.empty:
        st.error("Nenhum dado disponível para exibição.")
        return
    
    # Verificar se o índice do DataFrame é uma série temporal e, se for, transformá-lo em uma coluna 'Data'
    if data.index.name == 'Date' or data.index.name == 'Datetime':  # Verificar se o índice é do tipo Date
        data = data.reset_index()  # Transforma o índice 'Date' em uma coluna

    # Redefinir o índice para remover a exibição da coluna de índice anterior
    data = data.reset_index(drop=True)
    
    # Verificar a estrutura das colunas do DataFrame e ajustar os nomes
    expected_columns = data.columns.tolist()
    
    # Mapeamento de nomes esperados (em inglês) para PT-BR
    column_mapping = {
        'Date': 'Data',  # Adicionar o mapeamento para a coluna 'Date'
        'Open': 'Abertura',
        'High': 'Máxima',
        'Low': 'Mínima',
        'Close': 'Fechamento',
        'Volume': 'Volume',
        'Dividends': 'Dividendos',
        'Stock Splits': 'Stock Splits',
        'SMA': 'SMA',
        'EMA': 'EMA'
    }

    # Verificar quais colunas estão no DataFrame e ajustar os nomes apenas das colunas presentes
    columns_to_rename = {col: column_mapping[col] for col in expected_columns if col in column_mapping}

    # Renomear as colunas de acordo com o mapeamento para PT-BR
    data = data.rename(columns=columns_to_rename)

    # Ordenar os dados se a ordenação estiver habilitada e a coluna 'Data' estiver presente
    if sort_by_date and 'Data' in data.columns:
        data['Data'] = pd.to_datetime(data['Data'], errors='coerce', dayfirst=True)  # Garantir que as datas estão no formato correto
        data = data.sort_values(by='Data', ascending=not descending)
        data['Data'] = data['Data'].dt.strftime('%d/%m/%Y')  # Formatar datas para dd/mm/yyyy
    
    # Aplicar a formatação das colunas, se fornecida
    if column_format:
        data_display = data.copy()
        for col, fmt in column_format.items():
            if col in data_display.columns:
                data_display[col] = data_display[col].apply(fmt)
        st.dataframe(data_display, height=height, use_container_width=True)  # Ajustar altura e largura
    else:
        st.dataframe(data, height=height, use_container_width=True)  # Ajustar altura e largura

    # Exportar para CSV com formatação brasileira de moeda
    data_export = data.copy()
    # Formatar as colunas de valor monetário para o formato BRL (R$ xx,xx)
    monetary_columns = ['Abertura', 'Máxima', 'Mínima', 'Fechamento']  # Adicionar as colunas relevantes
    for col in monetary_columns:
        if col in data_export.columns:
            data_export[col] = data_export[col].apply(lambda x: f'R${x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Exportar para CSV
    csv = data_export.to_csv(index=False).encode('utf-8')
    st.download_button("Exportar para CSV", csv, file_name=filename, mime="text/csv", key=key)


# Função para exibir dividendos
def display_dividends(ticker_code, conn):
    dividends = fetch_and_save_dividends(conn, ticker_code)  # Buscar dividendos do banco de dados ou API

    # Verificar se os dividendos foram retornados como Series (em vez de DataFrame)
    if isinstance(dividends, pd.Series):
        dividends = dividends.reset_index()  # Converter Series para DataFrame
        dividends.columns = ['Data', 'Dividendos']  # Renomear as colunas

        # Ajustar a conversão de datas com o parâmetro dayfirst=True e errors='coerce'
        dividends['Data'] = pd.to_datetime(dividends['Data'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')

        # Formatar os valores monetários para R$
        dividends['Dividendos'] = dividends['Dividendos'].apply(lambda x: f'R${x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))

        # Exibir dividendos
        display_table(
            dividends, 
            f"Histórico de Dividendos de {ticker_code}", 
            f"{ticker_code}_dividends.csv", 
            key=f"dividends_table_{ticker_code}",
            sort_by_date=True,  # Ordenar por data
            descending=True,     # Ordenar do mais recente para o mais antigo
            height=400           # Definir altura da tabela de dividendos
        )
    else:
        st.warning(f"Nenhum dado de dividendos disponível para {ticker_code}")

# Função para exibir o valor de mercado de um ativo (com fallback para Alpha Vantage)
def display_market_value(ticker_code):
    ticker = yf.Ticker(ticker_code)
    try:
        market_info = ticker.info  # Tenta acessar as informações financeiras do ativo
        print(f"Yahoo Finance market_info: {market_info}")  # Adiciona print para depuração
        
        market_cap = market_info.get('marketCap', None)  # Tenta obter o valor de mercado
        st.subheader(f"Valor de Mercado de {ticker_code}")
        
        if market_cap:
            st.write(f"R${market_cap:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))  # Exibe o valor de mercado formatado
        else:
            st.warning(f"Informação de valor de mercado não disponível para {ticker_code}.")
            print(f"market_cap ausente para {ticker_code}. Tentando Alpha Vantage...")  # Adiciona print para rastrear fallback
            fallback_to_alpha_vantage(ticker_code)
    except KeyError as ke:
        st.error(f"Chave de dados não encontrada: {str(ke)}")
    except Exception as e:
        if "401" in str(e):
            st.error(f"Erro de autorização ao buscar valor de mercado para {ticker_code}. Verificando Alpha Vantage...")
            fallback_to_alpha_vantage(ticker_code)
        else:
            st.error(f"Erro ao buscar valor de mercado para {ticker_code}. {str(e)}")


# Fallback para Alpha Vantage caso o Yahoo Finance falhe
def fallback_to_alpha_vantage(ticker_code):
    api_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker_code}&apikey={ALPHA_VANTAGE_API_KEY}'
    try:
        response = requests.get(api_url)
        print(f"Alpha Vantage Response: {response.status_code}, {response.json()}")  # Adiciona print para depuração
        
        data = response.json()
        if 'MarketCapitalization' in data:
            market_cap = float(data['MarketCapitalization'])
            st.write(f"R${market_cap:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))  # Exibe o valor de mercado formatado
        else:
            st.warning(f"Alpha Vantage não retornou o valor de mercado para {ticker_code}.")
            print(f"Alpha Vantage MarketCapitalization ausente para {ticker_code}")  # Depuração adicional
    except Exception as e:
        st.error(f"Erro ao buscar valor de mercado via Alpha Vantage: {str(e)}")
        print(f"Erro Alpha Vantage: {e}")  # Depuração adicional


# Função para exibir relatórios financeiros (DRE, balanço patrimonial, fluxo de caixa)
def display_financial_statements(ticker_code):
    ticker = yf.Ticker(ticker_code)

    # Exibir DRE (Demonstrativo de Resultados)
    financials = ticker.financials
    if not financials.empty:
        st.subheader(f"Relatórios Financeiros de {ticker_code}")
        st.dataframe(financials)
        st.download_button("Exportar Dados Financeiros para CSV", financials.to_csv(), file_name=f'{ticker_code}_financials.csv')

    # Exibir balanço patrimonial
    balance_sheet = ticker.balance_sheet
    if not balance_sheet.empty:
        st.subheader(f"Balanço Patrimonial de {ticker_code}")
        st.dataframe(balance_sheet)
        st.download_button("Exportar Balanço Patrimonial para CSV", balance_sheet.to_csv(), file_name=f'{ticker_code}_balance_sheet.csv')

    # Exibir fluxo de caixa
    cashflow = ticker.cashflow
    if not cashflow.empty:
        st.subheader(f"Fluxo de Caixa de {ticker_code}")
        st.dataframe(cashflow)
        st.download_button("Exportar Fluxo de Caixa para CSV", cashflow.to_csv(), file_name=f'{ticker_code}_cashflow.csv')

    # Exibir rendimentos trimestrais
    earnings = ticker.earnings
    if not earnings.empty:
        st.subheader(f"Rendimentos Trimestrais de {ticker_code}")
        st.dataframe(earnings)
        st.download_button("Exportar Rendimentos Trimestrais para CSV", earnings.to_csv(), file_name=f'{ticker_code}_earnings.csv')

    # Exibir recomendações de analistas
    recommendations = ticker.recommendations
    if recommendations is not None and not recommendations.empty:
        st.subheader(f"Recomendações de Analistas para {ticker_code}")
        st.dataframe(recommendations)
        st.download_button("Exportar Recomendações de Analistas para CSV", recommendations.to_csv(), file_name=f'{ticker_code}_recommendations.csv')

    else:
        st.warning(f"Nenhuma recomendação de analistas disponível para {ticker_code}.")
