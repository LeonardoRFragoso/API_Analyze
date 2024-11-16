import streamlit as st
import datetime
from utils.database import get_stock_data
from utils.indicators import add_indicators
from plots.plot_functions import plot_graph
from utils.helpers import display_table, display_market_value, display_dividends
from utils.assets import FII_LIST, STOCK_LIST

# Função para buscar dados com cache, ignorando a conexão diretamente
@st.cache_data
def cached_stock_data(ticker_code, start_date, end_date, interval):
    """
    Função cacheável para buscar dados do ativo, ignorando a conexão no cache.
    """
    return ticker_code, start_date, end_date, interval

# Função para renderizar a aba de análise
def render_analysis_tab(conn):
    """
    Renderiza a aba de análise de FIIs ou ações no Streamlit.

    Args:
        conn: Conexão com o banco de dados para buscar dados do ativo.
    """
    st.sidebar.title("Configurações de Visualização para Análise")

    # Escolha do tipo de ativo (FIIs ou Ações)
    asset_type = st.sidebar.selectbox("Escolha o tipo de ativo", ["FIIs", "Ações"], key="selectbox1")
    asset_list = FII_LIST if asset_type == "FIIs" else STOCK_LIST

    # Seleção do ativo específico (por ticker)
    ticker_code_input = st.sidebar.selectbox(f"Selecione o {asset_type[:-1]} para Análise", asset_list, key="selectbox2")

    # Configurações de gráficos e indicadores
    plot_type = st.sidebar.radio("Escolha o Tipo de Gráfico", ["Candle", "Linha"], key="plot_type")
    interval = st.sidebar.selectbox("Escolha o Intervalo de Tempo", ["1d", "1h", "5m"], key="interval")
    sma_period = st.sidebar.number_input("Período da SMA (Média Móvel Simples)", min_value=5, max_value=200, step=1, value=20, key="sma_period")
    ema_period = st.sidebar.number_input("Período da EMA (Média Móvel Exponencial)", min_value=5, max_value=200, step=1, value=20, key="ema_period")

    # Configurações de data (data de início e data de fim)
    start_date = st.sidebar.date_input("Data de Início", value=datetime.date(2022, 1, 1), key="start_date")
    end_date = st.sidebar.date_input("Data de Fim", value=datetime.date.today(), key="end_date")

    # Verificar se a data de início é válida
    if start_date > end_date:
        st.error("Erro: A data de início não pode ser maior que a data de fim.")
        return

    # Botão para iniciar a análise
    if st.button("Analisar", key="analyze_button"):
        st.info(f"Carregando dados para {ticker_code_input}. Por favor, aguarde...")

        try:
            # Obter argumentos para a função cacheada
            ticker_code, start_date_cached, end_date_cached, interval_cached = cached_stock_data(
                ticker_code_input, start_date, end_date, interval
            )

            # Buscar os dados do ativo para o período selecionado
            data = get_stock_data(ticker_code, start_date_cached, end_date_cached, interval_cached, conn)

            if data is None or data.empty:
                st.warning(f"Não foram encontrados dados para {ticker_code_input} no intervalo selecionado.")
                return

            # Verificar se as colunas esperadas estão no DataFrame
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                st.error(f"Os dados retornados não possuem as colunas esperadas: {', '.join(missing_columns)}")
                return

            # Adicionar indicadores (SMA e EMA) aos dados
            data = add_indicators(data, sma_period=sma_period, ema_period=ema_period)

            # Ordenar os dados em ordem decrescente de data
            data = data.sort_index(ascending=False)

            # Exibir tabela de preços formatada
            st.info("Gerando tabela de preços...")
            with st.expander("Ver Dados Detalhados"):
                display_table(
                    data,
                    title=f"Dados de Preço de {ticker_code_input}",
                    filename=f"{ticker_code_input}_prices.csv",
                    column_format={
                        'Abertura': lambda x: f'R${x:,.2f}',
                        'Máxima': lambda x: f'R${x:,.2f}',
                        'Mínima': lambda x: f'R${x:,.2f}',
                        'Fechamento': lambda x: f'R${x:,.2f}'
                    },
                    key=f"price_table_{ticker_code_input}"
                )

            # Exibir gráfico de preços
            st.info("Gerando gráfico de preços...")
            plot_graph(
                data,
                title=f'{ticker_code_input} - Variação de Preço',
                y_label='Preço (R$)',
                graph_type=plot_type,
                sma=sma_period,
                ema=ema_period
            )

            # Exibir dividendos (se disponíveis)
            st.info("Buscando dados de dividendos...")
            display_dividends(ticker_code_input, conn)

            # Exibir o valor de mercado do ativo
            st.info("Buscando valor de mercado...")
            display_market_value(ticker_code_input)

        except Exception as e:
            st.error(f"Ocorreu um erro ao carregar os dados: {str(e)}")
            st.error("Verifique se as configurações estão corretas ou tente novamente mais tarde.")
