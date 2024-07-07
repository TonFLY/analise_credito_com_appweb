import streamlit as st
import requests
import yaml

st.title('Avaliação de Crédito')

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    url = config['url_api']['url']

profissoes = ['Advogado', 'Arquiteto', 'Cientista de Dados', 
              'Contador', 'Dentista', 'Empresário', 'Engenheiro', 'Médico', 'Programador']
tipos_residencia = ['Alugada', 'Outros', 'Própria']
escolaridades = ['Ens.Fundamental', 'Ens.Médio', 'PósouMais', 'Superior']
scores = ['Baixo', 'Bom', 'Justo', 'MuitoBom']
estados_civis = ['Casado', 'Divorciado', 'Solteiro', 'Víuvo']
produtos = ['AgileXplorer', 'DoubleDuty', 'EcoPrestige', 'ElegantCruise', 
            'SpeedFury', 'TrailConqueror', 'VoyageRoamer', 'WorkMaster']


with st.form(key='prediction_form'):
    profissao = st.selectbox('Profissão', profissoes)
    tempo_profissao = st.number_input('Tempo na profissão (em anos)', min_value=0, value=0, step=1)
    renda = st.number_input('Renda mensal', min_value=0.0, value=0.0, step=1000.0)
    tipo_residencia = st.selectbox('Tipo de residência', tipos_residencia)
    escolaridade = st.selectbox('Escolaridade', escolaridades)
    score = st.selectbox('Score', scores)
    idade = st.number_input('Idade', min_value=18, max_value=110, value=25, step=1)
    dependentes = st.number_input('Dependentes', min_value=0, value=0, step=1)
    estado_civil = st.selectbox('Estado Civil', estados_civis)
    produto = st.selectbox('Produto', produtos)
    valor_solicitado = st.number_input('Valor solicitado', min_value=0.0, 
                                       value=0.0, step=1000.0)
    valor_total_bem = st.number_input('Valor total do bem', min_value=0.0, 
                                      value=0.0, step=1000.0)

    submit_button = st.form_submit_button(label='Consultar')

if submit_button:
    dados_novos = {
        'profissao': [profissao],
        'tempoprofissao': [tempo_profissao],
        'renda': [renda],
        'tiporesidencia': [tipo_residencia],
        'escolaridade': [escolaridade],
        'score': [score],
        'idade': [idade],
        'dependentes': [dependentes],
        'estadocivil': [estado_civil],
        'produto': [produto],
        'valorsolicitado': [valor_solicitado],
        'valortotalbem': [valor_total_bem],
        'proporcaosolicitadototal': [valor_total_bem / valor_solicitado]
    }

    
    response = requests.post(url, json=dados_novos)
    if response.status_code == 200:
        predictions = response.json()
        probabilidade = predictions[0][0] * 100  # Convertendo para porcentagem
        classe = "Bom" if probabilidade > 50 else "Ruim"
        st.success(f"Probabilidade: {probabilidade:.2f}%")
        st.success(f"Classe: {classe}")
    else:
        st.error(f"Erro ao fazer a previsão: {response.status_code}")
        

    



