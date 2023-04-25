import streamlit as st 
from PIL import Image

st.set_page_config(
   page_title="Home",
   page_icon="🧊",
   initial_sidebar_state="expanded")

# Colocando uma LOGO no sidebar
#image_path = r'C:\Users\majdiogo\OneDrive\Pessoal\2. Data Science\Comunidade_DS\repos\repos\ftc_programacao_python\Ciclo_05'
image = Image.open('logo.png')
st.sidebar.image( image, width=200)

# Iníco da Barra Lateral
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: métricas gerais de comportamento.
        - Visão Tática: indicadores semanais de crescimento.
        - Visão Geográfica: inshights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
    - Time de Data Science no Discord
        - #DiogoPqdt
    
    """
)