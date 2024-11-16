import sqlite3
import pandas as pd
import yfinance as yf
import logging
import streamlit as st
import requests
from datetime import datetime, timedelta

# Chave da API Alpha Vantage e caminho do banco de dados obtidos do secrets
ALPHA_VANTAGE_API_KEY = st.secrets["alpha_vantage"]["api_key"]
DATABASE_PATH = st.secrets["database"]["path"]

# Inicializa o banco de dados e cria as tabelas se não existirem
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # Tabela de dados de ações
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

    conn.commit()
    return conn

# Salva dados de ações no banco de dados
def save_stock_data(conn, ticker, data):
    c = conn.cursor()
    for index, row in data.iterrows():
        date_str = index.strftime('%Y-%m-%d')
        c.execute('''
            INSERT OR IGNORE INTO stock_data (ticker, date, abertura, maxima, minima, fechamento, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ticker, date_str, row.get('Open'), row.get('High'), row.get('Low'), row.get('Close'), row.get('Volume')))
    conn.commit()

# Salva dividendos no banco de dados
def save_dividend_data(conn, ticker, dividends):
    c = conn.cursor()
    for index, value in dividends.items():
        date_str = index.strftime('%Y-%m-%d')
        c.execute('''
            INSERT OR IGNORE INTO dividend_data (ticker, date, dividend)
            VALUES (?, ?, ?)
        ''', (ticker, date_str, value))
    conn.commit()

# Carrega dados de ações do banco de dados
def load_stock_data(conn, ticker, start_date, end_date):
    c = conn.cursor()
    c.execute('''
        SELECT date, abertura, maxima, minima, fechamento, volume
        FROM stock_data
        WHERE ticker = ? AND date BETWEEN ? AND ?
    ''', (ticker, start_date, end_date))
    rows = c.fetchall()
    if rows:
        df = pd.DataFrame(rows, columns=['Data', 'Abertura', 'Máxima', 'Mínima', 'Fechamento', 'Volume'])
        df.set_index('Data', inplace=True)
        df.index = pd.to_datetime(df.index)
        return df
    return None

# Carrega dividendos do banco de dados
def load_dividend_data(conn, ticker):
    c = conn.cursor()
    c.execute('''
        SELECT date, dividend FROM dividend_data WHERE ticker = ?
    ''', (ticker,))
    rows = c.fetchall()
    if rows:
        return pd.DataFrame(rows, columns=['Data', 'Dividendos']).set_index('Data')
    return None

# Verifica se os dados de ações estão desatualizados
def is_data_outdated(conn, ticker):
    c = conn.cursor()
    c.execute('''
        SELECT MAX(date) FROM stock_data WHERE ticker = ?
    ''', (ticker,))
    last_date = c.fetchone()[0]
    if last_date:
        last_date_dt = datetime.strptime(last_date, '%Y-%m-%d')
        return (datetime.today() - last_date_dt).days > 0
    return True

# Busca e salva dividendos usando yfinance
def fetch_and_save_dividends(conn, ticker):
    ticker_data = yf.Ticker(ticker)
    dividends = ticker_data.dividends
    if not dividends.empty:
        save_dividend_data(conn, ticker, dividends)
        return dividends
    return None

# Busca valor de mercado usando Alpha Vantage
def get_market_value_alpha_vantage(ticker_code):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker_code}&apikey={ALPHA_VANTAGE_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data.get('MarketCapitalization', 0))
    except requests.RequestException as e:
        logging.error(f"Erro ao buscar valor de mercado pela Alpha Vantage: {str(e)}")
        return None

# Exibe valor de mercado, com fallback para Alpha Vantage
def display_market_value(ticker_code):
    ticker = yf.Ticker(ticker_code)
    try:
        market_info = ticker.info
        market_cap = market_info.get('marketCap', None)
        st.subheader(f"Valor de Mercado de {ticker_code}")
        if market_cap:
            st.write(f"R${market_cap:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        else:
            st.warning("Valor de mercado não disponível. Tentando Alpha Vantage...")
            market_cap_alpha = get_market_value_alpha_vantage(ticker_code)
            if market_cap_alpha:
                st.write(f"R${market_cap_alpha:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            else:
                st.warning("Não foi possível obter o valor de mercado.")
    except Exception as e:
        st.error(f"Erro ao buscar valor de mercado: {str(e)}")

# Carrega ou busca dados de ações e salva se necessário
def get_stock_data(ticker, start_date, end_date, interval, conn):
    data = load_stock_data(conn, ticker, start_date, end_date)
    if data is None or is_data_outdated(conn, ticker):
        ticker_data = yf.Ticker(ticker)
        hist_data = ticker_data.history(start=start_date, end=end_date, interval=interval)
        if not hist_data.empty:
            save_stock_data(conn, ticker, hist_data)
            return hist_data
    return data
