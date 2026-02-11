import streamlit as st
import pandas as pd
import requests

# Configurações da página
st.set_page_config(page_title='Finanças', page_icon=':moneybag:')

# ============================================================================
# CONSTANTES
# ============================================================================

SELIC_API_URL = 'https://www.bcb.gov.br/api/servico/sitebcb/historicotaxasjuros'

# ============================================================================
# FUNÇÕES DE DADOS
# ============================================================================

@st.cache_data(ttl='1day')
def get_selic() -> pd.DataFrame:
    """
    Busca o histórico da taxa Selic através da API do Banco Central do Brasil.
    
    Realiza o tratamento das datas de vigência e preenche vigências em aberto
    com a data atual. Utiliza cache de 1 dia para otimizar performance.

    Returns:
        pd.DataFrame: DataFrame contendo datas de vigência (início e fim) e a Meta Selic.
                      Retorna DataFrame vazio em caso de erro.
    """ 
    try:
        resp = requests.get(SELIC_API_URL, timeout=5)
        resp.raise_for_status()
        df = pd.DataFrame(resp.json()['conteudo'])
    except requests.exceptions.Timeout:
        st.error('⚠️ Timeout ao conectar com o Banco Central (5s)')
        return pd.DataFrame()
    except requests.exceptions.HTTPError as e:
        st.error(f'❌ Erro HTTP ao conectar com o Banco Central: {e}')
        return pd.DataFrame()
    except Exception as e:
        st.error(f'❌ Erro inesperado ao conectar com o Banco Central: {e}')
        return pd.DataFrame()

    try:
        # Conversão de strings para data
        df['DataInicioVigencia'] = pd.to_datetime(df['DataInicioVigencia']).dt.date
        df['DataFimVigencia'] = pd.to_datetime(df['DataFimVigencia']).dt.date
        
        # Preenche datas nulas (vigência atual) com a data de hoje
        df['DataFimVigencia'] = df['DataFimVigencia'].fillna(
            pd.Timestamp.now().date()
        )
    except Exception as e:
        st.error(f'❌ Erro ao processar dados da Selic: {e}')
        return pd.DataFrame()

    return df

def calc_general_stats(df):
    """
    Calcula estatísticas de evolução patrimonial baseadas no histórico fornecido.
    
    Args:
        df (pd.DataFrame): DataFrame original (colunas: Data, Instituição, Valor).
        
    Returns:
        pd.DataFrame: DataFrame consolidado por data com métricas de média móvel e evolução.
    """
    # Agrupa por data para ter o patrimônio total do mês
    df_consolidado = df.groupby(by='Data')[['Valor']].sum()

    # Cria coluna defasada (lag) para comparar com mês anterior
    df_consolidado['lag_1'] = df_consolidado['Valor'].shift(1)

    # Cálculo da variação absoluta mensal
    df_consolidado['Variação Mensal (R$)'] = (
        df_consolidado['Valor'] - df_consolidado['lag_1']
    )

    # Variação relativa mensal (%)
    df_consolidado['Variação Mensal (%)'] = (
        df_consolidado['Valor'] / df_consolidado['lag_1'] - 1
    )

    # Médias móveis da diferença absoluta
    for window in [6, 12, 24]:
        df_consolidado[f'Tendência {window}M (R$)'] = (
            df_consolidado['Variação Mensal (R$)'].rolling(window).mean()
        )

    for window in [6, 12, 24]:
        df_consolidado[f'Acúmulo {window}M (R$)'] = (
            df_consolidado['Valor'].rolling(window).apply(
                lambda x: x[-1] - x[0]
            )
        )
    
    for window in [6, 12, 24]:
        df_consolidado[f'Crescimento {window}M (%)'] = (
            df_consolidado['Valor'].rolling(window).apply(
                lambda x: (x[-1] / x[0] - 1)
            )
        )

    # Remove coluna auxiliar
    df_consolidado = df_consolidado.drop('lag_1', axis=1)

    return df_consolidado

def get_column_config():
    """Retorna configuração de formatação de colunas para estatísticas."""
    return {
    'Valor' : st.column_config.NumberColumn(
    label='Valor', format='R$ %.2f'),
    'Variação Mensal (R$)' : st.column_config.NumberColumn(
        label='Variação Mensal (R$)', format='R$ %.2f',
        help='Quanto em reais o patrimônio cresceu ou diminuiu em relação ao mês anterior'),
    'Variação Mensal (%)' : st.column_config.NumberColumn(
        label='Variação Mensal (%)', format='percent',
        help='Percentual de crescimento ou queda do patrimônio comparado ao mês anterior'),
    'Tendência 6M (R$' : st.column_config.NumberColumn(
        label='Tendência 6M (R$)', format='R$ %.2f',
        help='Média da variação dos últimos 6 meses'),
    'Tendência 12M (R$' : st.column_config.NumberColumn(
        label='Tendência 12M (R$)', format='R$ %.2f',
        help='Média da variação dos últimos 12 meses'),
    'Tendência 24M (R$' : st.column_config.NumberColumn(
        label='Tendência 24M (R$)', format='R$ %.2f',
        help='Média da variação dos últimos 24 meses'),
    'Acúmulo 6M (R$)' : st.column_config.NumberColumn(
        label='Acúmulo 6M (R$)', format='R$ %.2f',
        help='Total acumulado de ganho/perda nos últimos 6 meses'),
    'Acúmulo 12M (R$)' : st.column_config.NumberColumn(
        label='Acúmulo 12M (R$)', format='R$ %.2f',
        help='Total acumulado de ganho/perda nos últimos 12 meses'),
    'Acúmulo 24M (R$)' : st.column_config.NumberColumn(
        label='Acúmulo 24M (R$)', format='R$ %.2f',
        help='Total acumulado de ganho/perda nos últimos 24 meses'),
    'Crescimento 6M (%)' : st.column_config.NumberColumn(
        label='Crescimento 6M (%)', format='percent',
        help='ercentual total de crescimento nos últimos 6 meses'),
    'Crescimento 12M (%)' : st.column_config.NumberColumn(
        label='Crescimento 12M (%)', format='percent',
        help='ercentual total de crescimento nos últimos 12 meses'),
    'Crescimento 24M (%)' : st.column_config.NumberColumn(
        label='Crescimento 24M (%)', format='percent',
        help='Percentual total de crescimento nos últimos 24 meses')
    }

def get_column_config_metas():
    """Retorna configuração de formatação de colunas para metas."""
    return {
        'Meta' : st.column_config.NumberColumn(
            label='Meta',
            format='R$ %.2f'),
        'Valor' : st.column_config.NumberColumn(
            label='Realizado',
            format='R$ %.2f'),
        'Diferença' : st.column_config.NumberColumn(
            label='Diferença',
            format='R$ %.2f',
            help='Realizado / Meta Mensal'),
        'Ating. (%)' : st.column_config.NumberColumn(
            label='Ating. (%)',
            format='percent'),
        'Ating. Ano (%)' : st.column_config.NumberColumn(
            label='Ating. Ano (%)',
            format='percent'),
        'Ating. Previsto (%)' : st.column_config.NumberColumn(
            label='Ating. Previsto (%)',
            format='percent',
            help='Meta Mensal / Patrimônio estimado pós-meta')
    }

def main_metas():
    col1, col2 = st.columns(2)

    # Input de data com validação
    data_inicio_meta = col1.date_input(label='Inicío de Meta', max_value=df_stats.index.max())

    # Encontra a data mais próxima válida
    data_filtrada = df_stats.index[df_stats.index <= data_inicio_meta][-1]

    custos_fixos = col1.number_input('Custos Fixos', min_value=0., format='%.2f')
    salario_bruto = col2.number_input('Salário Bruto', min_value=0., format='%.2f')
    salario_liquido = col2.number_input('Salário Líquido', min_value=0., format='%.2f')

    valor_inicio = df_stats.loc[data_filtrada]['Valor']
    col1.markdown(f'**Patrimômio no início da meta**: R$ {valor_inicio:.2f}')

    # Obtém Selic
    selic_gov = get_selic()
    filtro_selic_data = (selic_gov['DataInicioVigencia'] < data_inicio_meta) & (selic_gov['DataFimVigencia'] > data_inicio_meta)
    selic_default = selic_gov[filtro_selic_data]['MetaSelic'].iloc[0]

    selic = st.number_input('Selic', min_value=0., value=selic_default, format='%.2f')
    selic_ano = selic / 100
    selic_mes = (selic_ano + 1) ** (1/12) - 1

    rendimento_ano = valor_inicio * selic_ano
    rendimento_mes = valor_inicio * selic_mes

    col1_pot, col2_pot = st.columns(2)

    mensal = salario_liquido - custos_fixos + valor_inicio * selic_mes

    with col1_pot.container(border=True):
        st.markdown(f'''**Potencial Arrecadação Mês**:\n\n R$ {mensal:.2f}''', help=f'{salario_liquido:.2f} + ( -{custos_fixos:.2f} ) + {rendimento_mes:.2f}')

    anual = 12 * (salario_liquido - custos_fixos) + valor_inicio * selic_mes

    with col2_pot.container(border=True):
        st.markdown(f'''**Potencial Arrecadação Ano**:\n\n R$ {anual:.2f}''', help=f'12 * ( {salario_liquido:.2f} + ( -{custos_fixos:.2f} ) ) + {rendimento_ano:.2f}')

    with st.container(border=True):
        col1_meta, col2_meta = st.columns(2)
        with col1_meta:
            meta_estipulada = st.number_input('Meta Estipulada', min_value=0., format='%.2f', value=anual)

        with col2_meta:
            patrimonio_final = meta_estipulada + valor_inicio
            st.markdown(f'Patrimônio estimado pós-meta:\n\n R$ {patrimonio_final:.2f}')
    return data_inicio_meta, valor_inicio, meta_estipulada, patrimonio_final

# ============================================================================
# PRINCIPAL
# ============================================================================

st.markdown("# Boas-vindas!")
st.markdown("Analise seus dados financeiros e projete suas metas com facilidade.")

# Widget de upload de dados
file_upload = st.file_uploader(label='Escolha um arquivo CSV', type='csv')

# Verifica se algum arquivo foi feito upload
if file_upload:

    # Leitura dos dados
    df = pd.read_csv(file_upload)
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y').dt.date

    # Exibição dos dados no App
    exp1 = st.expander('📊 Dados Brutos')
    columns_fmt = {'Valor': st.column_config.NumberColumn('Valor', format='R$ %.2f')}
    exp1.dataframe(df, hide_index=True, column_config=columns_fmt)

    # Visão Instituição
    exp2 = st.expander('🏦 Instituições')
    df_instituicao = df.pivot_table(index='Data', columns='Instituição', values='Valor')

    # Abas para diferentes visualizaçõesj
    tab_data, tab_history, tab_share = exp2.tabs(['Dados', 'Histórico', 'Distribuição'])

    columns_fmt_instituicao = {
        col: st.column_config.NumberColumn(
            format='R$ %.2f'
        )
        for col in df_instituicao.columns
    }

    # Exibi dados
    with tab_data:
        st.dataframe(df_instituicao, column_config=columns_fmt_instituicao)

    # Exibi histórico
    with tab_history:
        st.line_chart(df_instituicao)

    # Exibi distribuição
    with tab_share:
        date = st.selectbox('Data', options=df_instituicao.index)
        st.bar_chart(df_instituicao.loc[date])

    # ========================================================================
    # SEÇÃO: ESTATÍSTICAS GERAIS
    # ========================================================================
    exp3 = st.expander('📈 Estatísticas Gerais')
    
    df_stats = calc_general_stats(df)

    # Atalhos
    # Shift + End = até o fina da linha
    # Alt + seta para baixo = movimenta as linhas
    # Shift + Alt + i = cursor fica disponível em todas as linhas
    # Ctrl + d = seleciona para baixo todas as partes iguais selecionadas

    tab_stats, tab_abs, tab_rel = exp3.tabs(tabs=['Dados', 'Histórico de Evolução', 'Crescimento Relativo'])

    with tab_stats:
        st.dataframe(data=df_stats, column_config=get_column_config())

    with tab_abs:
        abs_cols = [
            'Variação Mensal (R$)',
            'Tendência 6M (R$)',
            'Tendência 12M (R$)',
            'Tendência 24M (R$)'
        ]
        st.line_chart(df_stats[abs_cols])

    with tab_rel:
        rel_cols = [
            'Variação Mensal (%)',
            'Crescimento 6M (%)',
            'Crescimento 12M (%)',
            'Crescimento 24M (%)'
        ]
        st.line_chart(data=df_stats[rel_cols])

    with st.expander('🎯 Metas'): 
        tab_main, tab_data_meta, tab_graph = st.tabs(tabs=['Configuração', 'Dados', 'Gráficos'])

        with tab_main:
            data_inicio_meta, valor_inicio, meta_estipulada, patrimonio_final = main_metas()

        with tab_data_meta:
            meses = pd.DataFrame({
                'Data Referência': [data_inicio_meta + pd.DateOffset(months=i) for i in range(1, 13)],
                'Meta': (valor_inicio + [round(meta_estipulada/12, 2) * i for i in range(1, 13)])
            })
            
            meses['Data Referência'] = pd.to_datetime(meses['Data Referência']).dt.strftime('%Y-%m')

            df_patrimonio = df_stats.reset_index()[['Data', 'Valor']]
            df_patrimonio['Data Referência'] = pd.to_datetime(df_patrimonio['Data']).dt.strftime('%Y-%m')

            meses = meses.merge(df_patrimonio, how='left', on='Data Referência')

            meses = meses[['Data Referência', 'Meta', 'Valor']] 
            meses['Diferença'] = meses['Valor'] - meses['Meta']
            meses['Ating. (%)'] = meses['Valor'] / meses['Meta']
            meses['Ating. Ano (%)'] = meses['Valor'] / patrimonio_final
            meses['Ating. Previsto (%)'] = meses['Meta'] / patrimonio_final
            meses = meses.set_index('Data Referência')
            st.dataframe(data=meses, column_config=get_column_config_metas())

    with tab_graph:
        st.line_chart(meses[['Ating. Ano (%)', 'Ating. Previsto (%)']])