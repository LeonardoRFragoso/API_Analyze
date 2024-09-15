import plotly.graph_objs as go
import streamlit as st

def plot_graph(data, title, yaxis_title, graph_type="Candle", sma=None, ema=None):
    fig = go.Figure()

    if graph_type == "Candle":
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Candlestick"))
    else:
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Preço Fechamento'))

    if sma is not None and 'SMA' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name=f'SMA {sma}'))
    if ema is not None and 'EMA' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA'], mode='lines', name=f'EMA {ema}'))

    fig.update_layout(title=title, xaxis_title='Data/Hora', yaxis_title=yaxis_title, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig)
