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

#-------------------------------------
# FUNÇÕES
#-------------------------------------
def country_maps(df1):
    cols = [ 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude' ]
    df_aux = (df1.loc[:,cols]
                 .groupby(by='Road_traffic_density')
                 .agg({'Delivery_location_latitude' : 'median' , 'Delivery_location_longitude' : 'median'})
                 .sort_values(by= 'Delivery_location_longitude')
                 .reset_index())
    # Create a map centered on Kolkata, India
    m = folium.Map(location=[18.653934, 76.012847], zoom_start=7)
    # Add a marker for each earthquake
    for index, row in df_aux.iterrows():
        folium.Marker(
            location=[row['Delivery_location_latitude'], row['Delivery_location_longitude']],
            popup=row['Road_traffic_density'],
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
    # Display the map
    folium_static(m, width=1024, height=600) 

def order_share_by_week(df1):
    cols = ['week_of_year' ,'Delivery_person_ID', 'ID' ]
    df_aux = (df1.loc[:, cols]
                .groupby(by='week_of_year')
                .agg({'Delivery_person_ID' : 'nunique', 'ID' : 'count'})
                .reset_index())
    df_aux['pedidos_por_entregador'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux ,
                  x='week_of_year' , 
                  y='pedidos_por_entregador' )
    return fig

def order_by_week(df1):
    cols = ['week_of_year', 'ID']
    df_aux = (df1.loc[:, cols]
                 .groupby('week_of_year')
                 .count()
                 .reset_index())
    df_aux.columns = ['week_of_year', 'pedidos_por_semana']
    fig = px.line(df_aux ,
                  x='week_of_year' , 
                  y='pedidos_por_semana' )
    return fig

def traffic_order_city(df1):
    cols = ['City', 'Type_of_vehicle', 'ID']
    df_aux = (df1.loc[:, cols]
                 .groupby(by=['City', 'Type_of_vehicle'])
                 .count()
                 .reset_index())
    #df_aux = df_aux[df_aux['City'] != 'NaN']
    fig = px.scatter(df_aux, x='City',
                     y='Type_of_vehicle',
                     size='ID',
                     color='City')
    return fig

def traffic_order_share(df1):
    cols = ['Road_traffic_density', 'ID']
    df_aux = df1.loc[:, cols].groupby(by=['Road_traffic_density']).count().reset_index()
    #df_aux = df_aux[df_aux['Road_traffic_density'] != 'NaN ']
    df_aux['percent_traffic'] = (df_aux['ID'] / df_aux['ID'].sum()) * 100
    fig = px.pie(df_aux, values= 'percent_traffic' , names= 'Road_traffic_density')
    return fig

def order_metric():
    st.markdown('# Order By Day')
    cols = ['Order_Date', 'ID']
    df_aux = df1.loc[:, cols].groupby(by=['Order_Date']).count().reset_index()
    df_aux.columns = ['Order_Date', 'qtde_entregas']
    fig =px.bar(df_aux, x='Order_Date' ,y='qtde_entregas')
    return fig

def clean_code(df1):
    """ Está função tem a responsabilidade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica )
        
        Input: Dataframe
        Output: Dataframe
    
    """
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

#----------------------------Início da estrutura lógica dos códigos---------------------------


# Lendo o arquivo CSV
df = pd.read_csv(r'dataset\train.csv')

# Limpando o arquivo
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
#image_path = r'C:\Users\majdiogo\OneDrive\Pessoal\2. Data Science\Comunidade_DS\repos\repos\ftc_programacao_python\imagens\logo.png'
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
st.header('Marketplace - Visão Cliente')

# Criando Abas 
tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container(): # Primeira linha
        fig = order_metric()
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container(): # Segunda linha
        col1, col2 = st.columns(2, gap = "large")
        with col1:
            st.markdown('### Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)


        with col2:
            st.markdown('### Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('### Order By Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('### Order Share By Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
        

    
with tab3:
    st.markdown('### Country Maps')
    country_maps(df1)
    
    
