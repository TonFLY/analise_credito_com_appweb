import streamlit as st  # Framework para criação de interfaces web
import requests          # Biblioteca para fazer requisições HTTP
import yaml             # Biblioteca para ler arquivos YAML

# Título da aplicação
st.title('Avaliação de Crédito')  

# Carregamento da configuração da API (URL) a partir do arquivo config.yaml
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    url = config['url_api']['url']

# Listas de opções para os campos de entrada (selectboxes)
profissoes = ['Advogado', 'Arquiteto', 'Cientista de Dados', 'Contador', 'Dentista', 'Empresário', 'Engenheiro', 'Médico', 'Programador']
tipos_residencia = ['Alugada', 'Outros', 'Própria']
escolaridades = ['Ens.Fundamental', 'Ens.Médio', 'Pós ou Mais', 'Superior']
scores = ['Baixo', 'Bom', 'Justo', 'Muito Bom']
estados_civis = ['Casado', 'Divorciado', 'Solteiro', 'Viúvo']
produtos = ['AgileXplorer', 'DoubleDuty', 'EcoPrestige', 'ElegantCruise', 'SpeedFury', 'TrailConqueror', 'VoyageRoamer', 'WorkMaster']

# Criação do formulário para entrada dos dados
with st.form(key='prediction_form'):  
    # Campos de entrada do formulário (selectboxes e number_inputs)
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
    valor_solicitado = st.number_input('Valor solicitado', min_value=0.0, value=0.0, step=1000.0)
    valor_total_bem = st.number_input('Valor total do bem', min_value=0.0, value=0.0, step=1000.0)
    
    # Botão para submeter o formulário
    submit_button = st.form_submit_button(label='Consultar')  

# Verifica se o botão foi pressionado
if submit_button:  
    # Cria um dicionário com os dados inseridos no formulário
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
        'proporcaosolicitadototal': [valor_solicitado / valor_total_bem]  # Calcula a proporção correta
    }

    # Envia os dados para a API usando uma requisição POST
    response = requests.post(url, json=dados_novos)  

    # Verifica a resposta da API
    if response.status_code == 200:  # Sucesso
        predictions = response.json()
        probabilidade = predictions[0][0] * 100  # Converte a probabilidade para porcentagem
        classe = "Bom" if probabilidade > 50 else "Ruim"  # Determina a classe com base na probabilidade
        st.success(f"Probabilidade: {probabilidade:.2f}%")  # Exibe a probabilidade em verde
        st.success(f"Classe: {classe}")  # Exibe a classe em verde
    else:  # Erro
        st.error(f"Erro ao fazer a previsão: {response.status_code}")  # Exibe o erro em vermelho
