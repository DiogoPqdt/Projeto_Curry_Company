# Importando as Bibliotecas
import pandas as pd
from datetime import datetime
import re
import numpy as np
import plotly.express as px
import folium 
import haversine as hs
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

#-------------------------------------------
# FUNÇÕES
#-------------------------------------------

def top_delivers(df1, top_asc):
    cols = ['City', 'Delivery_person_ID','Time_taken(min)']
    df_aux = (df1.loc[:, cols].groupby(by=['City', 'Delivery_person_ID'])
                              .mean()
                              .round(2)
                              .sort_values(by='Time_taken(min)', ascending=top_asc)
                              .reset_index())
    df_aux1 = df_aux[df_aux['City'] == 'Metropolitian'].head(10)
    df_aux2 = df_aux[df_aux['City'] == 'Urban'].head(10)
    df_aux3 = df_aux[df_aux['City'] == 'Semi-Urban'].head(10)
    df3 = pd.concat([df_aux1, df_aux2, df_aux3])
    df3 = df3.reset_index(drop=True)
    return df3

def clean_code(df1):
    # 1. convertando a coluna Age de texto para numero
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # 2. convertando a coluna Ratings de texto para numero decimal ( float )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # 3. convertando a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # Criando a coluna semana do ano
    df1['week_of_year'] = df1['Order_Date'].apply(lambda x: x.strftime('%U'))

    # 4. convertendo multiple_deliveries de texto para numero inteiro ( int )
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    ## 5. Removendo os espacos dentro de strings/texto/object
    #df1 = df1.reset_index( drop=True )
    #for i in range( len( df1 ) ):
    #  df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()


    # 6. Removendo os espacos dentro de strings/texto/object

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 7. Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)']  = df1['Time_taken(min)'].astype( int )
    
    return df1

# Lendo o arquivo CSV
df = pd.read_csv('dataset\train.csv')

# Limpando o Dataframe
df1 = clean_code(df)

#-------------------------------------------
#               CONFIGURANDO A PÁGINA
#-------------------------------------------

st.set_page_config(
   page_title="Cury Company",
   page_icon="🧊",
   layout="wide",
   initial_sidebar_state="expanded")

#-------------------------------------------
#               SIDEBAR
#-------------------------------------------

# Colocando uma LOGO no sidebar
image = Image.open('logo.png')
st.sidebar.image( image, width=200)

# Preparando estrutura do Sidebar
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Selecione uma data limite')
data_slider = st.sidebar.slider(
             'Até qual valor?',
             value= pd.datetime(2022, 4, 13),
             min_value=pd.datetime(2022, 2, 11),
             max_value=pd.datetime(2022, 4, 6),
             format= 'DD-MM-YYYY'
)
st.sidebar.markdown("""---""")
traffic_option = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam']
)
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_option)
df1 = df1.loc[linhas_selecionadas, :]

#-------------------------------------------
#               LAYOUT
#-------------------------------------------

st.header('Marketplace - Visão Entregadores')
tab1, tab2, tab3 = st.tabs(['Visão Geral', '_', '_'])

with tab1:
    with st.container():
        st.markdown('## Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)
        with col2:
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)

        with col3:
            melhor_veiculo = df1['Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor_veiculo)

            
        with col4:
            pior_veiculo = df1['Vehicle_condition'].min()
            col4.metric('Pior Condição', pior_veiculo)

    with st.container():
        st.markdown('''___''')
        st.markdown('## Avaliações')
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.markdown('##### Avaliações Médias por Entregador')
            cols = ['Delivery_person_ID', 'Delivery_person_Ratings']
            df_aux = (df1.loc[:, cols].groupby(by=['Delivery_person_ID']).mean()
                                      .reset_index()
                                      .round(2))
            st.dataframe(df_aux)
            
        with col2:
            st.markdown('##### Avaliação Média por Trânsito')
            cols = ['Delivery_person_Ratings', 'Road_traffic_density']
            df_aux = (df1.loc[:, cols].groupby(by=['Road_traffic_density'])
                                      .agg({'Delivery_person_Ratings' : ['mean' , 'std']}))
            df_aux.columns = ['Ratings_mean', 'Ratings_std']
            df_aux.reset_index(inplace=True)
            st.dataframe(df_aux)
            
            st.markdown('##### Avaliação Média por Clima')
            cols = ['Weatherconditions', 'Delivery_person_Ratings']

            df_aux = (df1.loc[:, cols].groupby(by=['Weatherconditions'])
                                      .agg({'Delivery_person_Ratings' : ['mean', 'std']}))
            df_aux.columns = ['Ratings_mean', 'Reatings_std']
            df_aux.reset_index(inplace=True)
            st.dataframe(df_aux)

            
    with st.container():
        st.markdown('''___''')
        st.markdown('## Velocidade de Entrega')
        
        col1, col2 = st.columns(2, gap='large')
        
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc = False)
            st.dataframe(df3)
                       
        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df3 = top_delivers(df1, top_asc = True)
            st.dataframe(df3)