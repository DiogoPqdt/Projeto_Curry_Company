# Importando as Bibliotecas
import pandas as pd
from datetime import datetime
import re
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium 
import haversine as hs
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

#-------------------------------------------
# FUNÇÕES
#-------------------------------------------

def avg_std_time_on_traffic(df1):
    cols = ['City', 'Road_traffic_density', 'Time_taken(min)']
    df_aux = (df1.loc[:, cols].groupby(by=['City', 'Road_traffic_density'])
                              .agg({'Time_taken(min)' : ['mean' , 'std']})
                              .round(2))
    df_aux.columns = ['Time_mean', 'Time_std']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='Time_mean',
                      color='Time_mean', color_continuous_scale='RdBu',
                      color_continuous_midpoint = np.average(df_aux['Time_mean']))
    return fig

def avg_std_time_graph(df1):
    cols= ['City', 'Time_taken(min)']
    df_aux = (df1.loc[:,cols].groupby(by=['City'])
                             .agg({'Time_taken(min)' : ['mean', 'std']})
                             .round(2))
    df_aux.columns = ['Time_mean', 'Time_std']
    df_aux.reset_index(inplace=True)
    fig = go.Figure()
    fig.add_trace( go.Bar(name='Control',
                          x=df_aux['City'],
                          y=df_aux['Time_mean'],
                          error_y=dict(type = 'data',
                                       array = df_aux['Time_std'])))
    fig.update_layout(barmode = 'group')
    return fig

def avg_std_time_delivery(df1, festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
        Input:
            - df: Dataframe com os dados necessários para o cálculo
            - op: tipo de operação que precisa ser calculado
                'avg_time': calcula o tempo médio.
                'std_time': calcula o desvio padrão do tempo.
            - festival: informar se o período é com ou sem festival.
        Output:
            - df : Dataframe com 2 colunas e 1 linha.
    
    """
    cols = ['Festival', 'Time_taken(min)']
    df_aux = (df1.loc[:, cols].groupby(by=['Festival'])
                              .agg({'Time_taken(min)' : ['mean', 'std']}))               
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round( df_aux.loc[df_aux['Festival'] == festival, op], 2)
    return df_aux

def distance(df1, fig):
    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df_aux = df1.loc[:,cols]
        df1['distancia_entrega'] = df_aux.apply(lambda x: hs.haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = df1['distancia_entrega'].mean().round(2)
        return avg_distance
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df_aux = df1.loc[:,cols]
        df1['distancia_entrega'] = df_aux.apply(lambda x: hs.haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        df_aux = df1.loc[:, ['City', 'distancia_entrega']].groupby(by= 'City').mean().reset_index()
        fig = go.Figure( data=[ go.Pie(labels=df_aux['City'], values=df_aux['distancia_entrega'], pull=[0, 0.1,0])])
        return fig

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
df = pd.read_csv('dataset/train.csv')

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
image = Image.open( 'logo.png')
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

st.header('Marketplace - Visão Restaurante')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.markdown('### Overal Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap='large')
        with col1:
            qtd_entregadores_unicos = df1['Delivery_person_ID'].nunique()
            st.metric('Entregadores Únicos', qtd_entregadores_unicos)

        with col2:
            avg_distance = distance(df1, fig=False)
            st.metric('Distância Média das Entregas', avg_distance)

        with col3:
            df_aux = avg_std_time_delivery(df1, festival = 'Yes', op='avg_time')
            st.metric('Tempo Médio de Entrega c/ Festival', df_aux)

        with col4:
            df_aux = avg_std_time_delivery(df1, festival = 'Yes',op='std_time')
            st.metric('Desvio Padrão de Entrega c/ Festival', df_aux)

        with col5:
            df_aux = avg_std_time_delivery(df1, festival = 'No', op='avg_time')
            st.metric('Tempo Médio de Entrega s/ Festival', df_aux)

        with col6:
            df_aux = avg_std_time_delivery(df1, festival = 'No',op='std_time')
            st.metric('Desvio Padrão de Entrega s/ Festival', df_aux)

    with st.container():
        st.markdown('''___''')
        st.markdown('### Tempo Médio de entrega por cidade')
        col1, col2 = st.columns(2, gap='large')
        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            cols = ['City', 'Type_of_order', 'Time_taken(min)']
            df_aux = (df1.loc[:, cols].groupby(by=['City', 'Type_of_order'])
                                      .agg({'Time_taken(min)' : ['mean' , 'std']})
                                      .round(2))
            df_aux.columns = ['Time_mean', 'Time_std']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
            
        
    with st.container():
        st.markdown('''___''')
        st.markdown('### Distribuição do Tempo')
        col1, col2 = st.columns(2, gap='large')
        with col1:
            fig = distance(df1, fig=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
           
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)
                
