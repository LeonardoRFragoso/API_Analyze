import sqlite3
import pandas as pd
import yfinance as yf
import logging
import streamlit as st
import requests
import os
from datetime import datetime

# Chave da API Alpha Vantage e caminho do banco de dados obtidos do secrets
ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage"]["api_key"]
DATABASE_PATH = st.secrets["database"]["path"]

# Inicializa o banco de dados e cria as tabelas se não existirem
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Tabela de dados de ações (nomes de colunas em português)
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_data (
            ticker TEXT,
            date TEXT,
            abertura REAL,
            maxima REAL,
            minima REAL,
            fechamento REAL,
            volume INTEGER,
            UNIQUE(ticker, date)
        )
    ''')

    # Tabela de dividendos
    c.execute('''
        CREATE TABLE IF NOT EXISTS dividend_data (
            ticker TEXT,
            date TEXT,
            dividend REAL,
            UNIQUE(ticker, date)
        )
    ''')

    # Tabela de histórico de usuários
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_history (
            user_id TEXT,
            ticker TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de notícias financeiras
    c.execute('''
        CREATE TABLE IF NOT EXISTS financial_news (
            ticker TEXT,
            title TEXT,
            description TEXT,
            url TEXT,
            published_at TEXT,
            source_name TEXT
        )
    ''')

    # Tabela de relatórios financeiros (poderá ser utilizada futuramente)
    c.execute('''
        CREATE TABLE IF NOT EXISTS financial_reports (
            ticker TEXT,
            report_date TEXT,
            report_data TEXT
        )
    ''')

    conn.commit()
    return conn

# Função para salvar dados de ações no banco de dados (usando nomes de colunas em português)
def save_stock_data(conn, ticker, data):
    c = conn.cursor()
    for index, row in data.iterrows():
        date_str = index.strftime('%Y-%m-%d')
        c.execute('''
            INSERT OR IGNORE INTO stock_data (ticker, date, abertura, maxima, minima, fechamento, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ticker, date_str, row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
    conn.commit()

# Função para salvar dividendos no banco de dados
def save_dividend_data(conn, ticker, dividends):
    c = conn.cursor()
    for index, value in dividends.items():
        date_str = index.strftime('%Y-%m-%d')
        c.execute('''
            INSERT OR IGNORE INTO dividend_data (ticker, date, dividend)
            VALUES (?, ?, ?)
        ''', (ticker, date_str, value))
    conn.commit()

# Função para salvar notícias financeiras no banco de dados
def save_financial_news(conn, ticker, news_data):
    c = conn.cursor()
    for news in news_data:
        c.execute('''
            INSERT INTO financial_news (ticker, title, description, url, published_at, source_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticker, news['title'], news['description'], news['url'], news['publishedAt'], news['source']['name']))
    conn.commit()

# Carrega os dados de ações do banco de dados (usando nomes de colunas em português)
def load_stock_data(conn, ticker, start_date, end_date):
    c = conn.cursor()
    c.execute('''
        SELECT date, abertura, maxima, minima, fechamento, volume FROM stock_data
        WHERE ticker = ? AND date BETWEEN ? AND ?
    ''', (ticker, start_date, end_date))
    rows = c.fetchall()
    if rows:
        df = pd.DataFrame(rows, columns=['Data', 'Abertura', 'Máxima', 'Mínima', 'Fechamento', 'Volume'])
        df.set_index('Data', inplace=True)
        return df
    return None

# Carrega os dividendos do banco de dados
def load_dividend_data(conn, ticker):
    c = conn.cursor()
    c.execute('''
        SELECT date, dividend FROM dividend_data
        WHERE ticker = ?
    ''', (ticker,))
    rows = c.fetchall()
    if rows:
        return pd.Series({row[0]: row[1] for row in rows})
    return None

# Carrega as notícias financeiras do banco de dados
def load_financial_news(conn, ticker):
    c = conn.cursor()
    c.execute('''
        SELECT title, description, url, published_at, source_name FROM financial_news
        WHERE ticker = ?
        ORDER BY published_at DESC
    ''', (ticker,))
    rows = c.fetchall()
    if rows:
        news_list = []
        for row in rows:
            news_item = {
                'title': row[0],
                'description': row[1],
                'url': row[2],
                'publishedAt': row[3],
                'source': {'name': row[4]}
            }
            news_list.append(news_item)
        return news_list
    return []

# Verifica se os dados de ações estão desatualizados
def is_data_outdated(conn, ticker):
    c = conn.cursor()
    c.execute('''
        SELECT MAX(date) FROM stock_data WHERE ticker = ?
    ''', (ticker,))
    last_date = c.fetchone()[0]
    if last_date:
        return (datetime.today() - datetime.strptime(last_date, '%Y-%m-%d')).days > 0
    return True

# Busca e salva dividendos usando yfinance
def fetch_and_save_dividends(_conn, ticker):
    logging.info(f"Fetching dividends for ticker: {ticker}")
    
    ticker_data = yf.Ticker(ticker)
    dividends = ticker_data.dividends
    
    logging.info(f"Dividends data shape for {ticker}: {dividends.shape}")
    logging.info(f"Dividends data preview for {ticker}: \n{dividends.head()}")
    
    if not dividends.empty:
        logging.info(f"Dividends found for {ticker}: {dividends.shape[0]} records")
        save_dividend_data(_conn, ticker, dividends)
        return dividends
    else:
        logging.warning(f"No dividends found for {ticker}")
    
    return None

# Fallback para buscar valor de mercado usando a Alpha Vantage
def get_market_value_alpha_vantage(ticker_code):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker_code}&apikey={ALPHA_VANTAGE_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data.get('MarketCapitalization', 0))  # Obter o valor de capitalização de mercado
    except Exception as e:
        st.error(f"Erro ao buscar valor de mercado pela Alpha Vantage para {ticker_code}. {str(e)}")
        return None

# Função que busca o valor de mercado e faz fallback para Alpha Vantage
def display_market_value(ticker_code):
    ticker = yf.Ticker(ticker_code)
    try:
        # Recuperar informações do ativo
        market_info = ticker.info
        st.subheader(f"Valor de Mercado de {ticker_code}")

        # Verifica se marketCap está disponível
        market_cap = market_info.get('marketCap', None)
        if market_cap:
            # Formatar o valor de mercado para moeda brasileira
            formatted_market_cap = f"R${market_cap:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            st.write(f"Valor de Mercado: {formatted_market_cap}")
        else:
            st.warning(f"Valor de mercado não disponível pelo Yahoo Finance para {ticker_code}. Tentando Alpha Vantage...")
            # Fallback para Alpha Vantage
            market_cap_alpha = get_market_value_alpha_vantage(ticker_code)
            if market_cap_alpha:
                formatted_market_cap_alpha = f"R${market_cap_alpha:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                st.write(f"Valor de Mercado (Alpha Vantage): {formatted_market_cap_alpha}")
            else:
                st.error(f"Dados não disponíveis para o ativo {ticker_code}.")
    except Exception as e:
        st.error(f"Erro ao buscar valor de mercado para {ticker_code}: {str(e)}")


# Carrega ou busca os dados de ações e salva se necessário (colunas em português)
def get_stock_data(ticker, start_date, end_date, interval, conn):
    data = load_stock_data(conn, ticker, start_date, end_date)
    if data is None or is_data_outdated(conn, ticker):
        ticker_data = yf.Ticker(ticker)
        hist_data = ticker_data.history(start=start_date, end=end_date, interval=interval)
        if not hist_data.empty:
            save_stock_data(conn, ticker, hist_data)
            return hist_data
        else:
            return None
    else:
        return data
