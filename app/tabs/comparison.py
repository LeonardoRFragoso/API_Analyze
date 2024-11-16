import streamlit as st
import datetime
from utils.helpers import display_table, display_market_value, display_dividends
from utils.database import get_stock_data
import plotly.graph_objects as go
from utils.assets import FII_LIST, STOCK_LIST

# Função para buscar dados com cache
@st.cache_data
def cached_stock_data(asset_code, start_date, end_date, interval):
    """
    Função cacheável para buscar dados de um ativo.

    Args:
        asset_code (str): Código do ativo.
        start_date (datetime.date): Data de início.
        end_date (datetime.date): Data de fim.
        interval (str): Intervalo de tempo.

    Returns:
        pd.DataFrame: Dados do ativo.
    """
    return asset_code, start_date, end_date, interval

def render_comparison_tab(conn):
    """
    Renderiza a aba de comparação de ativos no Streamlit.

    Args:
        conn: Conexão com o banco de dados para buscar dados do ativo.
    """
    st.sidebar.title("Configurações de Visualização para Comparação")

    # Escolha do tipo de ativo (FIIs ou Ações)
    asset_type_comparison = st.sidebar.selectbox(
        "Escolha o tipo de ativo para Comparação", ["FIIs", "Ações"], key="selectbox_comparison_type"
    )
    asset_list_comparison = FII_LIST if asset_type_comparison == "FIIs" else STOCK_LIST

    # Seleção dos ativos a serem comparados
    selected_assets = st.multiselect(
        f"Selecione os {asset_type_comparison} para Comparação",
        asset_list_comparison,
        key="multiselect_assets_comparison"
    )

    # Configurações de intervalo de tempo e datas
    interval = st.sidebar.selectbox(
        "Escolha o Intervalo de Tempo", ["1d", "1h", "5m"], key="selectbox_interval_comparison"
    )
    start_date = st.sidebar.date_input(
        "Data de Início", value=datetime.date(2022, 1, 1), key="start_date_comparison"
    )
    end_date = st.sidebar.date_input(
        "Data de Fim", value=datetime.date.today(), key="end_date_comparison"
    )

    # Verificar se a data de início é menor que a data de fim
    if start_date > end_date:
        st.error("Erro: A Data de Início não pode ser maior que a Data de Fim.")
        return

    # Botão para iniciar a comparação
    if st.button("Comparar", key="compare_button_comparison"):
        if not selected_assets:
            st.warning("Selecione ao menos um ativo para comparação.")
            return

        st.info("Carregando dados, por favor aguarde...")

        data_dict = {}
        errored_assets = []

        # Buscar os dados de cada ativo selecionado
        for asset_code in selected_assets:
            try:
                # Obter parâmetros da função cacheada
                cached_code, cached_start, cached_end, cached_interval = cached_stock_data(
                    asset_code, start_date, end_date, interval
                )

                # Buscar dados reais com a conexão ao banco de dados
                data = get_stock_data(cached_code, cached_start, cached_end, cached_interval, conn)

                if data is not None and not data.empty:
                    # Ordenar os dados por data em ordem decrescente
                    data = data.sort_index(ascending=False)
                    data_dict[asset_code] = data
                else:
                    errored_assets.append(asset_code)
            except Exception as e:
                st.error(f"Erro ao carregar os dados de {asset_code}: {str(e)}")
                errored_assets.append(asset_code)

        # Exibir mensagens para ativos com erros
        if errored_assets:
            st.warning(f"Os seguintes ativos não possuem dados ou ocorreram erros: {', '.join(errored_assets)}")

        # Se os dados foram obtidos com sucesso, exibe o gráfico
        if data_dict:
            fig = go.Figure()

            # Adicionar uma linha para cada ativo selecionado
            for asset, data in data_dict.items():
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    mode='lines',
                    name=f'Preço {asset}',
                    hovertemplate=f"%{{x}}<br>Preço: R$%{{y:,.2f}}<extra>{asset}</extra>"
                ))

            fig.update_layout(
                title="Comparação de Preços",
                xaxis_title="Data",
                yaxis_title="Preço (R$)",
                xaxis_rangeslider_visible=False,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Exibir dividendos e valor de mercado para cada ativo comparado
            for asset_code in selected_assets:
                st.subheader(f"Dados de {asset_code}")
                with st.expander("Histórico de Dividendos"):
                    display_dividends(asset_code, conn)
                with st.expander("Valor de Mercado"):
                    display_market_value(asset_code)
        else:
            st.warning("Nenhum dado foi encontrado para os ativos selecionados.")
