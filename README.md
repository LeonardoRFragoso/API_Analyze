
# Analisador de FIIs e Ações - Acompanhamento Completo

## Descrição do Projeto

Este projeto é uma aplicação completa desenvolvida com **Streamlit** e **yFinance** que permite o acompanhamento detalhado de FIIs e Ações da B3. O objetivo é fornecer uma plataforma de análise que exibe gráficos de preço, dividendos e indicadores técnicos, como médias móveis, além de permitir a comparação entre diferentes ativos.

### Principais Funcionalidades:

- **Análise individual** de FIIs e Ações:
    - Exibição de dados de preço
    - Gráficos de Candle ou Linha com indicadores (SMA e EMA)
    - Histórico de dividendos
    - Valor de mercado

- **Comparação de múltiplos ativos**:
    - Exibição de gráficos comparativos entre diferentes FIIs e Ações
    - Exibição de dividendos para cada ativo

### Organização do Projeto:

O projeto foi organizado seguindo boas práticas, separando suas funcionalidades em diferentes diretórios e arquivos:

- **`app/`**: Contém a lógica principal da aplicação.
  - **`static/`**: Arquivos estáticos, como CSS ou JS (futuro).
  - **`templates/`**: Templates HTML ou partes de UI.
  - **`database/`**: Scripts de banco de dados e gerenciamento de dados.
  - **`utils/`**: Funções utilitárias e helpers usados pela aplicação.
  - **`plots/`**: Funções específicas para plotagem de gráficos.

- **`tests/`**: Testes unitários e de integração para a aplicação.
  
- **`docs/`**: Documentação do projeto e API.

### Estrutura do Projeto:

```bash
financial_project/
│
├── app/
│   ├── static/
│   ├── templates/
│   ├── database/
│   ├── utils/
│   ├── plots/
│   └── main.py        # Arquivo principal da aplicação
├── tests/
├── docs/
└── README.md
```

### Pré-requisitos

- **Python 3.9+**
- **Streamlit**: `pip install streamlit`
- **yFinance**: `pip install yfinance`
- **SQLite** (já incluso no Python)

### Como executar o projeto:

1. Clone o repositório:

    ```bash
    git clone https://github.com/LeonardoRFragoso/API_Analyze
    cd financial_project
    ```

2. Instale as dependências necessárias:

    ```bash
    pip install -r requirements.txt
    ```

3. Execute a aplicação Streamlit:

    ```bash
    streamlit run app/main.py
    ```

4. Acesse a aplicação no navegador no endereço [localhost:8501](http://localhost:8501).

### Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request com melhorias.

### Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

Desenvolvido por Leonardo Fragoso
