import plotly.graph_objs as go
import streamlit as st

def plot_graph(data, title, yaxis_title, graph_type="Candle", sma=None, ema=None):
    fig = go.Figure()

    # Verificar se as colunas estão em inglês ou português
    if 'Open' in data.columns:
        open_col, high_col, low_col, close_col = 'Open', 'High', 'Low', 'Close'
    elif 'Abertura' in data.columns:
        open_col, high_col, low_col, close_col = 'Abertura', 'Máxima', 'Mínima', 'Fechamento'
    else:
        st.error("Colunas essenciais ausentes no DataFrame.")
        return

    # Ajuste para remover o preenchimento
    if graph_type == "Candle":
        fig.add_trace(go.Candlestick(
            x=data.index, 
            open=data[open_col],   # Nome da coluna dinâmico
            high=data[high_col],   # Nome da coluna dinâmico
            low=data[low_col],     # Nome da coluna dinâmico
            close=data[close_col], # Nome da coluna dinâmico
            name="Candlestick"
        ))
    else:
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data[close_col],   # Nome da coluna dinâmico
            mode='lines', 
            name='Preço Fechamento'
        ))

    # Adicionar SMA e EMA se as colunas estiverem presentes
    if sma is not None and 'SMA' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data['SMA'], 
            mode='lines', 
            name=f'SMA {sma}'
        ))
    if ema is not None and 'EMA' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data['EMA'], 
            mode='lines', 
            name=f'EMA {ema}'
        ))

    # Configurar layout do gráfico
    fig.update_layout(
        title=title, 
        xaxis_title='Data/Hora', 
        yaxis_title=yaxis_title, 
        xaxis_rangeslider_visible=False,  # Remover slider do eixo x
        showlegend=True
    )
    
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)
