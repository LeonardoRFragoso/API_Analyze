import streamlit as st
from utils.database import init_db
from tabs.analysis import render_analysis_tab
from tabs.comparison import render_comparison_tab
from tabs.news_reports import render_news_reports_tab

def main():
    conn = init_db()  # Inicializa o banco de dados
    st.title("Analisador de FIIs e Ações - Acompanhamento Completo")

    tab1, tab2, tab3 = st.tabs(["Análise Individual", "Comparação", "Notícias e Relatórios"])

    with tab1:
        render_analysis_tab(conn)  # Chama a aba de análise

    with tab2:
        render_comparison_tab(conn)  # Chama a aba de comparação

    with tab3:
        render_news_reports_tab(conn)  # Chama a aba de notícias e relatórios

if __name__ == "__main__":
    main()
