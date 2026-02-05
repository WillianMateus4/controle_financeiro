import streamlit as st
import pandas as pd

# Configurações da página
st.set_page_config(page_title='Finanças', page_icon=':moneybag:')

st.markdown("""
    # Boas-vindas!
""")

# Widget de upload de dados
file_upload = st.file_uploader(label='Escolha um arquivo', type='csv')

# Verifica se algum arquivo foi feito upload
if file_upload:

    # Leitura dos dados
    df = pd.read_csv(file_upload)
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y').dt.date

    

    # Exibição dos dados no App
    exp1 = st.expander('Dados Brutos')
    columns_fmt = {'Valor': st.column_config.NumberColumn('Valor', format='R$ %.2f')}
    exp1.dataframe(df, hide_index=True, column_config=columns_fmt)

    # Visão Instituição
    exp2 = st.expander('Instituições')
    df_instituicao = df.pivot_table(index='Data', columns='Instituição', values='Valor')

    # Abas para diferentes visualizações
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


        # date = st.date_input(
        #     'Data para Distribuição',
        #     min_value=df_instituicao.index.min(),
        #     max_value=df_instituicao.index.max())

        # if date not in df_instituicao.index:
        #     st.warning('Entre com uma data válida!')
        # else:
        #     st.bar_chart(df_instituicao.loc[date])