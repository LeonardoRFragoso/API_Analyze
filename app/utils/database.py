import sqlite3
import pandas as pd
import yfinance as yf
import logging
import streamlit as st
from datetime import datetime

# Inicializa o banco de dados e cria as tabelas se não existirem
def init_db():
    conn = sqlite3.connect("app/database/financial_data.db")
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
@st.cache_data(show_spinner=True)
def fetch_and_save_dividends(conn, ticker):
    logging.info(f"Fetching dividends for ticker: {ticker}")
    
    ticker_data = yf.Ticker(ticker)
    dividends = ticker_data.dividends
    
    if not dividends.empty:
        logging.info(f"Dividends found for {ticker}: {dividends.shape[0]} records")
        save_dividend_data(conn, ticker, dividends)
        return dividends
    else:
        logging.warning(f"No dividends found for {ticker}")
    
    return None

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
