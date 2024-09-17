
# Analisador de FIIs e Ações - Acompanhamento Completo

## Descrição do Projeto

Este projeto é uma aplicação modular desenvolvida com **Streamlit**, **yFinance** e outras bibliotecas, que permite o acompanhamento detalhado de FIIs e Ações da B3. A plataforma oferece análise individual de ativos, comparação entre múltiplos ativos, visualização de notícias financeiras e relatórios financeiros, além de gráficos interativos com indicadores técnicos.

### Principais Funcionalidades:

- **Análise Individual de FIIs e Ações**:
    - Exibição de gráficos de preço com opções de Candle ou Linha.
    - Indicadores técnicos: **SMA (Média Móvel Simples)** e **EMA (Média Móvel Exponencial)**.
    - Histórico de dividendos formatados em R$.
    - Exibição do valor de mercado do ativo.
    - Acesso a relatórios financeiros (DRE, Balanço Patrimonial, Fluxo de Caixa).

- **Comparação de Múltiplos Ativos**:
    - Exibição de gráficos comparativos de preço entre diferentes FIIs e Ações.
    - Visualização de dividendos e valor de mercado para cada ativo comparado.

- **Notícias Financeiras**:
    - Busca de notícias financeiras atualizadas para FIIs e Ações através da integração com a **NewsAPI**.

- **Relatórios Financeiros**:
    - Exibição de relatórios financeiros completos, incluindo DRE (Demonstrativo de Resultados), Balanço Patrimonial e Fluxo de Caixa.

### Organização do Projeto:

O projeto foi modularizado para facilitar a manutenção, com as funcionalidades divididas em diferentes diretórios e arquivos:

- **`app/`**: Contém toda a lógica da aplicação.
  - **`tabs/`**: Cada aba da aplicação foi dividida em arquivos independentes:
    - `analysis.py`: Aba de análise individual de ativos.
    - `comparison.py`: Aba de comparação entre múltiplos ativos.
    - `news_reports.py`: Aba de notícias e relatórios financeiros.
  - **`utils/`**: Funções auxiliares e utilitárias:
    - `database.py`: Gerenciamento de banco de dados (SQLite).
    - `helpers.py`: Funções de suporte como exibição de tabelas e formatação de dados.
    - `news_api.py`: Integração com a **NewsAPI** para busca de notícias financeiras.
  - **`plots/`**: Funções responsáveis pela plotagem dos gráficos.
  - **`database/`**: Scripts relacionados ao banco de dados.

### Estrutura do Projeto:

```bash
financial_project/
│
├── app/
│   ├── tabs/
│   ├── utils/
│   ├── plots/
│   ├── database/
│   └── app.py        # Arquivo principal da aplicação
├── tests/
└── README.md
```

### Pré-requisitos

- **Python 3.9+**
- **Streamlit**: `pip install streamlit`
- **yFinance**: `pip install yfinance`
- **SQLite** (incluso no Python)
- **NewsAPI**: Para buscar notícias financeiras, é necessário obter uma chave de API em [newsapi.org](https://newsapi.org/).

### Como Executar o Projeto:

1. Clone o repositório:

    ```bash
    git clone https://github.com/LeonardoRFragoso/API_Analyze
    cd financial_project
    ```

2. Instale as dependências necessárias:

    ```bash
    pip install -r requirements.txt
    ```

3. Crie um arquivo `.env` para armazenar sua chave da **NewsAPI** ou utilize o `secrets.toml` caso esteja utilizando o Streamlit Cloud:

    ```
    NEWS_API_KEY=your_news_api_key_here
    ```

4. Execute a aplicação Streamlit:

    ```bash
    streamlit run app/app.py
    ```

5. Acesse a aplicação no navegador no endereço [localhost:8501](http://localhost:8501).

### Modularização

O projeto foi modularizado de forma que cada aba da aplicação tem sua própria responsabilidade:
- **Análise Individual**: Mostra os gráficos e dados de um ativo específico.
- **Comparação de Ativos**: Permite a comparação visual entre múltiplos ativos.
- **Notícias e Relatórios**: Mostra notícias financeiras e relatórios financeiros completos.

### Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request com melhorias e correções.

### Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

Desenvolvido por Leonardo Fragoso