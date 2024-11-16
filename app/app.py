import streamlit as st
from utils.database import init_db
from tabs.analysis import render_analysis_tab
from tabs.comparison import render_comparison_tab
from tabs.news_reports import render_news_reports_tab

def main():
    """
    Função principal que inicializa o aplicativo Streamlit para análise de FIIs e Ações.
    """
    # Tenta inicializar o banco de dados
    try:
        with st.spinner("Inicializando banco de dados..."):
            conn = init_db()
            if conn is None:
                st.error("Erro ao conectar ao banco de dados. Por favor, tente novamente mais tarde.")
                return
    except Exception as e:
        st.error(f"Erro durante a inicialização do banco de dados: {e}")
        return

    # Configuração do título e abas
    st.title("Analisador de FIIs e Ações - Acompanhamento Completo")
    tab1, tab2, tab3 = st.tabs(["Análise Individual", "Comparação", "Notícias e Relatórios"])

    # Renderiza cada aba
    with tab1:
        try:
            render_analysis_tab(conn)
        except Exception as e:
            st.error(f"Erro na aba de Análise Individual: {e}")

    with tab2:
        try:
            render_comparison_tab(conn)
        except Exception as e:
            st.error(f"Erro na aba de Comparação: {e}")

    with tab3:
        try:
            render_news_reports_tab(conn)
        except Exception as e:
            st.error(f"Erro na aba de Notícias e Relatórios: {e}")

if __name__ == "__main__":
    main()
