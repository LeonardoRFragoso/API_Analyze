import plotly.graph_objs as go
import streamlit as st

def plot_graph(data, title, y_label, graph_type="Candle", sma=None, ema=None):
    """
    Plota gráficos de preços com suporte a SMA e EMA, usando Plotly.

    Args:
        data (pd.DataFrame): Dados de preços.
        title (str): Título do gráfico.
        y_label (str): Rótulo do eixo Y.
        graph_type (str, optional): Tipo de gráfico ("Candle" ou "Linha"). Padrão: "Candle".
        sma (int, optional): Período da SMA (se presente nos dados). Padrão: None.
        ema (int, optional): Período da EMA (se presente nos dados). Padrão: None.
    """
    fig = go.Figure()

    # Verificar se as colunas estão em inglês ou português
    if 'Open' in data.columns:
        open_col, high_col, low_col, close_col = 'Open', 'High', 'Low', 'Close'
    elif 'Abertura' in data.columns:
        open_col, high_col, low_col, close_col = 'Abertura', 'Máxima', 'Mínima', 'Fechamento'
    else:
        st.error("Colunas essenciais ausentes no DataFrame.")
        return

    # Adicionar o gráfico de Candlestick ou Linha
    if graph_type == "Candle":
        fig.add_trace(go.Candlestick(
            x=data.index, 
            open=data[open_col], 
            high=data[high_col], 
            low=data[low_col], 
            close=data[close_col], 
            name="Candlestick"
        ))
    elif graph_type == "Linha":
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data[close_col], 
            mode='lines', 
            name='Preço Fechamento'
        ))
    else:
        st.error(f"Tipo de gráfico inválido: {graph_type}")
        return

    # Adicionar SMA e EMA se as colunas estiverem presentes
    if sma is not None and f'SMA_{sma}' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data[f'SMA_{sma}'], 
            mode='lines', 
            name=f'SMA ({sma})'
        ))
    if ema is not None and f'EMA_{ema}' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data[f'EMA_{ema}'], 
            mode='lines', 
            name=f'EMA ({ema})'
        ))

    # Configurar layout do gráfico
    fig.update_layout(
        title=title,
        xaxis_title='Data/Hora',
        yaxis_title=y_label,  # Usando y_label como no código original
        xaxis_rangeslider_visible=False,
        showlegend=True,
        template='plotly_white'
    )
    
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)
