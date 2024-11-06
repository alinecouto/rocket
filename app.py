
#importando bibliotecas

from urllib.error import URLError
import pandas as pd
import streamlit as st
import numpy as np
import pulp as pu
from datetime import datetime
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.express as px
import altair as alt

#configurando o titulo da janela
st.set_page_config(page_title="Equipe Rocket", page_icon="👁")

#Top 5 Filiais valor de venda, Top Cidades, Top 10 clientes, Top 10 categorias
st.title('Equipe Rocket')
df_mercado = pd.read_csv("supermarket_sales.csv", sep=";", decimal=",", encoding="ISO-8859-1")



def mostrar_dados(data):
   
    df_mercado = pd.read_csv("supermarket_sales.csv", sep=";")
    return df_mercado.set_index("City")

try:
    df_mercado = mostrar_dados(df_mercado)
    City = st.multiselect(
        "Selecione Cidade", list(df_mercado.index), ["Yangon","Naypyitaw","Mandalay"]
    )
    if not City:
        st.error("Por favor selecione a cidade.")
    else:
        data = df_mercado.loc[City]       
        st.write("### Dados ", data.sort_index())

        data = data.T.reset_index()
        data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "Total", "value": "Total de vendas (R$)"}
        )
       
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
        % e.reason)
    
def top_5_cidades_vendas(data):
    # Garantindo que 'Total' é numérico
    df_mercado['Total'] =  df_mercado['Total'].str.replace('.', '').str.replace(',', '.')
    df_mercado['Total'] = pd.to_numeric(df_mercado['Total'], errors='coerce')

    # Agrupando os dados por cidade e somando as vendas
    vendas_por_cidade = df_mercado.groupby('City')['Total'].sum().reset_index()
    
    # Ordenando e selecionando as top 5 cidades
    top_cidades = vendas_por_cidade.sort_values(by='Total', ascending=False).head(5)

    # Formatando a coluna Total para o formato em reais
    top_cidades['Total'] = top_cidades['Total'].apply(lambda x: f'R$ {x:,.2f}' if pd.notnull(x) else 'R$ 0,00')

    # Exibindo os resultados
    st.write("### Ranking de Cidades por Vendas")
    #st.write(top_cidades)
    
    # Criando gráfico
    chart = (
        alt.Chart(top_cidades)
        .mark_bar()
        .encode(
            x=alt.X('City', sort='-y', title='Cidade'),
            y=alt.Y('Total', title='Total de Vendas (R$)'),
            tooltip=['City', 'Total']
        )
        .properties(width=600, height=400)
    )
    
    st.altair_chart(chart, use_container_width=True)


def mostrar_vendas_por_genero(data):
   
    # Convertendo os gêneros para minúsculas
    data['Gender'] = data['Gender'].str.lower()

    # Garantindo que 'Total' é numérico e corrigindo formato com replace
    data['Total'] = data['Total'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
    data['Total'] = pd.to_numeric(data['Total'], errors='coerce')
    #data['Total'] = data['Total'].apply(lambda x: f'R$ {x:,.2f}')
    # Gerando dataset de agrupamento de gênero com a soma das vendas
    gender_sales = data.groupby('Gender')['Total'].sum().reset_index()

    # Definindo as cores
    color_map = alt.Scale(domain=['male', 'female'],
                          range=['blue', 'red'])

    # Gráfico do total de vendas por gênero usando Altair
    st.divider()
    st.subheader("Total de Vendas por Gênero")

    chart = alt.Chart(gender_sales).mark_bar().encode(
        x='Gender',
        y=alt.Y('Total'),
        color=alt.condition(
            alt.datum.Gender == 'male',  # Se gênero for 'male'
            alt.value('blue'),            # Cor azul
            alt.value('red')              # Senão, vermelho
        )
    ).properties()

    st.altair_chart(chart, use_container_width=True)

# def exibir_agrupamento_geracao(data):

#     """
#         Exibe o gráfico de agrupamento por geração

#         Parâmetros:
#             data: DataFrame referente ao CSV carregado

#     """

#     #gerando dataset de agrupamento de geração
#     generation_counts = data['generation'].value_counts().rename_axis('generation').reset_index(name='counts')
#     generation_counts.set_index('generation', inplace=True)

#     #Gráfico do número de pessoas por geração (horizontal)
#     st.divider()
#     st.subheader("Número de pessoas por geração")
#     st.bar_chart(generation_counts['counts'], color= "#ffaa00",x_label="Geração",y_label="Quantidade", horizontal=True)

# def exibir_media_educacao_genero(data):
    
#     """
#         Exibe o gráfico de média de educação por gênero

#         Parâmetros:
#             data: DataFrame referente ao CSV carregado

#     """
    

#     #gerando dataset de agrupamento de média de anos de educação por gênero
#     gender_education_mean = data.groupby('gender')['years_of_education'].mean().reset_index(name='means')
#     gender_education_mean.set_index('gender', inplace=True)

#     #Gráfico da média de anos trabalhados
#     st.divider()
#     st.subheader("Média de anos trabalhados")
#     st.bar_chart(gender_education_mean['means'], color= "#00aa00",x_label="Geração",y_label="Média de anos trabalhados")

# def exibir_distribuicao_status_emprego(data):

#     """
#         Exibe a distribuição de status de emprego

#         Parâmetros:
#             data: DataFrame referente ao CSV carregado

#     """

#     #gerando dataset de estado atual de emprego
#     job_counts = data['employment_status'].value_counts().rename_axis('employment_status').reset_index(name='counts')
#     job_counts.set_index('employment_status', inplace=True)

#     #Gráfico de pizza do Status de Emprego no Streamlit com o Plotly
#     st.divider()
#     st.subheader("Distribuição do Status de Emprego")

#     fig = px.pie(job_counts, values='counts', names=job_counts.index)
#     st.plotly_chart(fig)

# def histograma_geral_idades(data):
    
#     """
#         Exibe o histograma geral de idades

#         Parâmetros:
#             data: DataFrame referente ao CSV carregado

#     """

#     # Criar faixas etárias
#     data['age_group'] = pd.cut(data['age'], bins=[0, 18, 30, 45, 60, 100], labels=['0-18', '19-30', '31-45', '46-60', '61+'])

#     #distribuição geral por idade
#     age_group_counts = data['age_group'].value_counts().sort_index()

#     #Mostra o histograma geral de idades
#     st.divider()
#     st.subheader("Distribuição por Idade")
#     # Criando o gráfico de barras agrupadas
#     fig_grouped_age = px.bar(age_group_counts,
#                         labels={"value": "Número de Pessoas", "variable": "Idade"}, 
#                         barmode='stack')

#     fig_grouped_age.update_layout(
#         xaxis_title="Idades"
#     )

#     st.plotly_chart(fig_grouped_age)


# def histograma_geral_generos(data):

#     """
#         Exibe o histograma geral de gêneros

#         Parâmetros:
#             data: DataFrame referente ao CSV carregado

#     """

#     #distribuição por gênero e por idade
#     age_gender_distribution = data.groupby(['age_group', 'gender'], observed=True).size().unstack(fill_value=0)

#     #Mostra o histograma geral de idades agrupado por gênero
#     st.divider()
#     st.subheader("Distribuição por Idade e Gênero")
#     # Criando o gráfico de barras agrupadas
#     fig_grouped_gen = px.bar(age_gender_distribution,
#                         labels={"value": "Número de Pessoas", "variable": "Idade"}, 
#                         barmode='group')

#     fig_grouped_gen.update_layout(
#         xaxis_title="Idades"
#     )

#     st.plotly_chart(fig_grouped_gen)






#abre o arquivo manualmente


#exceção tratada para quando não tem carga de arquivo CSV  (para não dar erro no pdoc)
try:
    file = 'supermarket_sales.csv'
    data = pd.read_csv(file, sep=";", decimal=",", encoding="ISO-8859-1")
    st.session_state["dataset"] = data

except FileNotFoundError:
    st.info("Por favor, faça o upload de um arquivo CSV para visualizar o mapa.")



#exibir_tabela_dados(data)


#exceção tratada para quando não tem carga de arquivo CSV  (para não dar erro no pdoc)
if "dataset" in st.session_state:

    mostrar_dados(st.session_state["dataset"])

    top_5_cidades_vendas(st.session_state["dataset"])
    mostrar_vendas_por_genero(st.session_state["dataset"])

   