import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime

# Inicializa o banco de dados e cria tabelas se não existirem
def init_db():
    conn = sqlite3.connect("app/database/financial_data.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_data (
            ticker TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            UNIQUE(ticker, date)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS dividend_data (
            ticker TEXT,
            date TEXT,
            dividend REAL,
            UNIQUE(ticker, date)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_history (
            user_id TEXT,
            ticker TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

# Salva os dados de ações no banco de dados
def save_stock_data(conn, ticker, data):
    c = conn.cursor()
    for index, row in data.iterrows():
        date_str = index.strftime('%Y-%m-%d')
        c.execute('''
            INSERT OR IGNORE INTO stock_data (ticker, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ticker, date_str, row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
    conn.commit()

# Salva os dividendos no banco de dados
def save_dividend_data(conn, ticker, dividends):
    c = conn.cursor()
    for index, value in dividends.items():
        date_str = index.strftime('%Y-%m-%d')
        c.execute('''
            INSERT OR IGNORE INTO dividend_data (ticker, date, dividend)
            VALUES (?, ?, ?)
        ''', (ticker, date_str, value))
    conn.commit()

# Carrega os dados de ações do banco de dados
def load_stock_data(conn, ticker, start_date, end_date):
    c = conn.cursor()
    c.execute('''
        SELECT date, open, high, low, close, volume FROM stock_data
        WHERE ticker = ? AND date BETWEEN ? AND ?
    ''', (ticker, start_date, end_date))
    rows = c.fetchall()
    if rows:
        df = pd.DataFrame(rows, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df.set_index('Date', inplace=True)
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

# Busca e salva os dividendos usando yfinance
def fetch_and_save_dividends(conn, ticker):
    ticker_data = yf.Ticker(ticker)
    dividends = ticker_data.dividends
    if not dividends.empty:
        save_dividend_data(conn, ticker, dividends)
        return dividends
    return None

# Carrega ou busca os dados de ações e salva se necessário
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
