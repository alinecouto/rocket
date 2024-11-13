# Importando bibliotecas
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
import unicodedata

# Função para normalizar texto (remover acentuação e caracteres especiais)
def normalizar_texto(texto):
    return ''.join((c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')).lower()

# Configurando o título da janela
st.set_page_config(page_title="Equipe Rocket", page_icon="👁")

# Título da página
st.title('Equipe Rocket')
df_mercado = pd.read_csv("supermarket_sales.csv", sep=";", decimal=",", encoding="ISO-8859-1")

def mostrar_dados(data):
    df_mercado = pd.read_csv("supermarket_sales.csv", sep=";")
    return df_mercado.set_index("Cidade")

try:
    df_mercado = mostrar_dados(df_mercado)
    Cidade = st.multiselect(
        "Selecione Cidade", list(df_mercado.index), ["Sao Paulo", "Guarulhos", "Sao Bernado do Campo"]
    )
    if not Cidade:
        st.error("Por favor, selecione a cidade.")
    else:
        data = df_mercado.loc[Cidade]
        st.write("### Dados ", data.sort_index())

        data = data.T.reset_index()
        data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "Total", "value": "Total de vendas (R$)"}
        )

except URLError as e:
    st.error(f"**Este demo requer acesso à internet.** Erro de conexão: {e.reason}")

# Função para análise de receita por linha de produto
def analise_receita_por_produto(data):
    # Garantir que a coluna 'Total' seja tratada como string antes do replace
    data['Total'] = data['Total'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)

    # Convertendo 'Total' para float após a substituição
    data['Total'] = pd.to_numeric(data['Total'], errors='coerce')
    
    # Normalizando os nomes das linhas de produto para evitar problemas com acentuação
    data['Linha de Produto'] = data['Linha de Produto'].apply(normalizar_texto)
    
    # Agrupando por linha de produto e somando as vendas
    receita_por_produto = data.groupby('Linha de Produto')['Total'].sum().reset_index()
    
    # Ordenando por receita em ordem decrescente
    receita_por_produto = receita_por_produto.sort_values(by='Total', ascending=False)
    
    # Exibindo o resultado
    st.write("### Receita por Linha de Produto")
    
    # Criando gráfico
    fig = px.bar(receita_por_produto, x='Linha de Produto', y='Total', title="Receita por Linha de Produto", color='Linha de Produto',
                 labels={'Total': 'Total de Receita (R$)', 'Linha de Produto': 'Linha de Produto'})
    
    # Ajustando a codificação para garantir que caracteres especiais sejam exibidos corretamente
    fig.update_layout(
        title='Receita por Linha de Produto',
        xaxis_title='Linha de Produto',
        yaxis_title='Total de Receita (R$)',
        font=dict(family="Arial, sans-serif", size=12, color="RebeccaPurple")
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Funções auxiliares
def top_5_cidades_vendas(data):
    data = data[data['Cidade'].isin(Cidade)]

    # Tratando os valores de 'Total' para garantir que sejam números
    data['Total'] = data['Total'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    data['Total'] = pd.to_numeric(data['Total'], errors='coerce')
    
    st.write("### Ranking de Cidades por Vendas")

    # Calculando o total geral de vendas
    total_geral = data['Total'].sum()
    total_geral_formatado = f'R$ {total_geral:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    # Exibindo o total geral
    st.write(f"### Total Geral de Vendas: {total_geral_formatado}")
    
    # Agrupando e somando as vendas por cidade
    vendas_por_cidade = data.groupby('Cidade')['Total'].sum().reset_index()
    
    # Selecionando as top 5 cidades com maior total de vendas
    top_cidades = vendas_por_cidade.sort_values(by='Total', ascending=False).head(5)
    top_cidades['Total'] = top_cidades['Total'].apply(lambda x: f'R$ {x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Criando o gráfico de barras com Altair
    chart = (
        alt.Chart(top_cidades)
        .mark_bar()
        .encode(
            x=alt.X('Cidade', sort='-y', title='Cidade'),
            y=alt.Y('Total', title='Total de Vendas (R$)'),
            tooltip=['Cidade', 'Total']
        )
        .properties(width=600, height=400)
    )
    
    st.altair_chart(chart, use_container_width=True)





import plotly.express as px

def mostrar_vendas_por_genero(data):
    data = data[data['Cidade'].isin(Cidade)]

    # Convertendo os gêneros para minúsculas
    data['Genero'] = data['Genero'].str.lower()

    # Tratando os valores de 'Total' para garantir que sejam números
    data['Total'] = data['Total'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    data['Total'] = pd.to_numeric(data['Total'], errors='coerce')

    # Gerando dataset de agrupamento de gênero com a soma das vendas
    gender_sales = data.groupby('Genero')['Total'].sum().reset_index()

    # Ajustando a ordem e as cores para consistência
    gender_sales['Genero'] = gender_sales['Genero'].replace({'masculino': 'Masculino', 'feminino': 'Feminino'})
    
    # Gráfico do total de vendas por gênero usando Plotly
    st.divider()
    st.subheader("Total de Vendas por Gênero")
    
    fig = px.bar(gender_sales, x='Genero', y='Total', title="Total de Vendas por Gênero",
                 labels={'Total': 'Total de Vendas (R$)', 'Genero': 'Gênero'},
                 color='Genero', color_discrete_map={'Masculino': 'blue', 'Feminino': 'red'})
    
    st.plotly_chart(fig, use_container_width=True)



    # 1. Análise de Vendas por Tipo de Cliente
def analise_vendas_por_tipo_cliente(data):
    data = data[data['Cidade'].isin(Cidade)]

    # Garantindo que 'Total' seja numérico
    data['Total'] = data['Total'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    data['Total'] = pd.to_numeric(data['Total'], errors='coerce')

    vendas_por_tipo_cliente = data.groupby('Tipo de Cliente')['Total'].sum().reset_index()
    vendas_por_tipo_cliente = vendas_por_tipo_cliente.sort_values(by='Total', ascending=False)

    st.write("### Vendas por Tipo de Cliente")
    fig = px.bar(vendas_por_tipo_cliente, x='Tipo de Cliente', y='Total', title="Vendas por Tipo de Cliente",  color='Tipo de Cliente',
                 labels={'Total': 'Total de Vendas (R$)', 'Tipo de Cliente': 'Tipo de Cliente'})
    st.plotly_chart(fig, use_container_width=True)

# 2. Análise de Vendas por Forma de Pagamento
def analise_vendas_por_pagamento(data):
    # Garantindo que 'Total' seja numérico
    data['Total'] = data['Total'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    data['Total'] = pd.to_numeric(data['Total'], errors='coerce')

    vendas_por_pagamento = data.groupby('Pagamento')['Total'].sum().reset_index()
    vendas_por_pagamento = vendas_por_pagamento.sort_values(by='Total', ascending=False)

    st.write("### Vendas por Forma de Pagamento")
    fig = px.bar(vendas_por_pagamento, x='Pagamento', y='Total', title="Vendas por Forma de Pagamento", color='Pagamento',
                 labels={'Total': 'Total de Vendas (R$)', 'Pagamento': 'Forma de Pagamento'})
    st.plotly_chart(fig, use_container_width=True)

# 3. Análise de Vendas por Faixa de Rating
def analise_vendas_por_faixa_rating(data):
    data = data[data['Cidade'].isin(Cidade)]

    # Garantindo que 'Total' seja numérico
    data['Total'] = data['Total'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    data['Total'] = pd.to_numeric(data['Total'], errors='coerce')

    # Garantindo que a coluna 'Rating' seja numérica
    data['Rating'] = pd.to_numeric(data['Rating'], errors='coerce')  # Convertendo para numérico

    # Definindo as faixas de Rating e os rótulos
    bins = [4, 5, 8, 10]  # Faixas: 4-5, 6-8, 9-10
    labels = ['4-5', '6-8', '9-10']  # Nomes das faixas
    data['Faixa Rating'] = pd.cut(data['Rating'], bins=bins, labels=labels, right=True)

    # Agrupando as vendas por faixa de rating
    vendas_por_faixa_rating = data.groupby('Faixa Rating')['Total'].sum().reset_index()

    # Ordenando as faixas de rating de forma crescente
    vendas_por_faixa_rating['Faixa Rating'] = pd.Categorical(vendas_por_faixa_rating['Faixa Rating'], categories=labels, ordered=True)
    vendas_por_faixa_rating = vendas_por_faixa_rating.sort_values(by='Faixa Rating')

    st.write("### Vendas por Faixa de Rating")

    # Criando o gráfico
    fig = px.bar(vendas_por_faixa_rating, x='Faixa Rating', y='Total', title="Vendas por Faixa de Rating", color='Faixa Rating',
                 labels={'Total': 'Total de Vendas (R$)', 'Faixa Rating': 'Faixa de Rating'})

    # Passando um 'key' único para o gráfico
    st.plotly_chart(fig, use_container_width=True, key="faixa_rating_vendas")

# Executando as funções
try:
    file = 'supermarket_sales.csv'
    data = pd.read_csv(file, sep=";", decimal=",", encoding="ISO-8859-1")
    st.session_state["dataset"] = data

except FileNotFoundError:
    st.info("Por favor, faça o upload de um arquivo CSV para visualizar os dados.")

if "dataset" in st.session_state:
    mostrar_dados(st.session_state["dataset"])
    top_5_cidades_vendas(st.session_state["dataset"])
    mostrar_vendas_por_genero(st.session_state["dataset"])
    analise_receita_por_produto(st.session_state["dataset"])  
    analise_vendas_por_tipo_cliente(st.session_state["dataset"])  
    analise_vendas_por_pagamento(st.session_state["dataset"])   
    analise_vendas_por_faixa_rating(st.session_state["dataset"])       

