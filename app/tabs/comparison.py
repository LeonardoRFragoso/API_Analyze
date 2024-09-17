import streamlit as st
import datetime
from utils.helpers import display_table, display_market_value, display_dividends
from utils.database import get_stock_data
import plotly.graph_objects as go
from utils.assets import FII_LIST, STOCK_LIST

def render_comparison_tab(conn):
    st.sidebar.title("Configurações de Visualização para Comparação")
    
    # Seleção do tipo de ativo (FIIs ou Ações)
    asset_type_comparison = st.sidebar.selectbox("Escolha o tipo de ativo para Comparação", ["FIIs", "Ações"], key="selectbox_comparison_type")
    asset_list_comparison = FII_LIST if asset_type_comparison == "FIIs" else STOCK_LIST
    
    # Seleção dos ativos a serem comparados
    selected_assets = st.multiselect(f"Selecione os {asset_type_comparison} para Comparação", asset_list_comparison, key="multiselect_assets_comparison")
    
    # Configurações de intervalo de tempo e datas
    interval = st.sidebar.selectbox("Escolha o Intervalo de Tempo", ["1d", "1h", "5m"], key="selectbox_interval_comparison")
    start_date = st.sidebar.date_input("Data de Início", value=datetime.date(2022, 1, 1), key="start_date_comparison")
    end_date = st.sidebar.date_input("Data de Fim", value=datetime.date.today(), key="end_date_comparison")

    # Verificar se a data de início é menor que a data de fim
    if start_date > end_date:
        st.error("Erro: A Data de Início não pode ser maior que a Data de Fim.")
        return

    # Botão para iniciar a comparação
    if st.button("Comparar", key="compare_button_comparison"):
        if not selected_assets:
            st.warning("Selecione ao menos um ativo para comparação.")
            return

        data_dict = {}

        # Buscar os dados de cada ativo selecionado
        for asset_code in selected_assets:
            data = get_stock_data(asset_code, start_date, end_date, interval, conn)
            if data is not None:
                data_dict[asset_code] = data
            else:
                st.warning(f"Dados não disponíveis para o ativo {asset_code}")

        # Se os dados foram obtidos com sucesso, exibe o gráfico
        if data_dict:
            fig = go.Figure()

            # Adicionar uma linha para cada ativo selecionado
            for asset, data in data_dict.items():
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=f'Preço {asset}'))
            
            fig.update_layout(
                title="Comparação de Preços",
                xaxis_title='Data',
                yaxis_title='Preço (R$)',
                xaxis_rangeslider_visible=False
            )
            st.plotly_chart(fig)

            # Exibir dividendos e valor de mercado para cada ativo comparado
            for asset_code in selected_assets:
                st.subheader(f"Dados de {asset_code}")
                display_dividends(asset_code, conn)
                display_market_value(asset_code)
        else:
            st.warning("Nenhum dado foi encontrado para os ativos selecionados.")
