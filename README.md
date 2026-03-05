# 📊 Dashboard de Controle Financeiro

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.54+-ff4b4b?style=flat&logo=streamlit)

Este projeto é uma aplicação web desenvolvida em Python com **Streamlit** para
análise de evolução do patrimônio e projeção de metas financeiras.

> **📊 Aplicação Online:** [Clique aqui para acessar a aplicação em execução](https://controlefinanceiro-v01.streamlit.app/)

## 🎯 Funcionalidades

* **Upload de Arquivo:** upload de dados financeiros em formato CSV.
* **Análise por Instituição:** Visualização de saldo por instituição financeira ao longo do tempo.
* **Estatísticas de Evolução:** Cálculo automático de crescimento absoluto e relativo (6, 12 e 24 meses).
* **Projeção de Metas:** Simulador de metas financeiras que cruza dados de salário, custos fixos e rendimento atrelado à Selic (dados reais do Banco Central).

## 🛠️ Tecnologias Utilizadas

* Python 3.x
* Streamlit (Interface)
* Pandas (Manipulação de dados)
* Requests (Consumo de API do Banco Central)


## 📂 Estrutura de Dados (CSV)

Para o correto funcionamento, o arquivo de entrada deve ser um **CSV** (separado por vírgulas) contendo registros mensais.

**Importante:** Os registros devem ser **mensais** (apenas uma linha por mês para cada instituição) para garantir a precisão dos cálculos de evolução.

| Data       | Instituição | Valor   |
| :---       | :---        | :---    |
| 07/01/2026 | Nubank      | 1500,00 |
| 07/01/2026 | Caixa       | 5000,00 |
| 06/02/2026 | Nubank      | 2100,00 |
| 06/02/2026 | Caixa       | 4700,00 |

<br>

> **🔗 Modelo de Dados:**
> Para facilitar, utilize este [Modelo de Planilha Google](https://docs.google.com/spreadsheets/d/1ZzRwoiSAASS-IX-Vdb4rqfG1fEnfOtWrnHX5mIm0dfg/edit?usp=sharing).

> *Instrução: Preencha a planilha e faça o download em **Arquivo > Fazer download > Valores separados por vírgula (.csv)**.*

## Integrações

* **API do Banco Central do Brasil:** Utilizada para obter o histórico da taxa Selic e auxiliar nos cálculos de rendimento das metas.

## 👤 Autor

**Willian Mateus** | *Data Analyst & BI*

 ℹ️ Para saber mais sobre mim, ver meus outros projetos ou entrar em contato, visite meu [Perfil do GitHub](https://github.com/WillianMateus4).
