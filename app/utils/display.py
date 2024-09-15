import streamlit as st
import yfinance as yf

def display_price_table(data, key=None):
    data_display = data.copy()
    for col in ['Open', 'High', 'Low', 'Close']:
        data_display[col] = data_display[col].apply(lambda x: f'R${x:,.2f}')
    st.write("Dados de Preço")
    st.dataframe(data_display)

def display_dividends_table(dividends, ticker_code, key=None):
    if dividends is None or dividends.empty:
        st.warning(f"Nenhum dado de dividendos disponível para {ticker_code}")
    else:
        st.subheader(f"Histórico de Dividendos de {ticker_code}")
        dividends_formatted = dividends.apply(lambda x: f'R${x:,.2f}')
        dividends_formatted.index.name = 'Data'
        dividends_formatted.name = 'Dividendos por Cota (R$)'
        st.dataframe(dividends_formatted)

def display_market_value(ticker_code):
    ticker = yf.Ticker(ticker_code)
    market_info = ticker.info
    market_cap = market_info.get('marketCap', 'N/A')
    st.subheader(f"Valor de Mercado de {ticker_code}")
    if market_cap != 'N/A':
        st.write(f"R${market_cap:,.2f}")
    else:
        st.write("Não disponível")
