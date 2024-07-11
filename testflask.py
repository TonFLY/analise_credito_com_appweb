import requests  # Biblioteca para fazer requisições HTTP
import yaml       # Biblioteca para ler arquivos YAML

# Carregamento da configuração da API a partir do arquivo config.yaml
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file) 
    url = config['url_api']['url']  # Obtém a URL da API do arquivo de configuração

# Dados novos a serem enviados para a API (em formato de dicionário)
dados_novos = {
    'profissao': ['Advogado', 'Médico', 'Dentista', 'Contador'],
    'tempoprofissao': [39, 37, 16, 0],
    'renda': [20860.0, 5000, 20000, 7000],
    'tiporesidencia': ['Alugada', 'Própria', 'Própria', 'Alugada'],
    'escolaridade': ['Ens.Fundamental', 'Pós ou Mais', 'Superior', 'Ens.Fundamental'],
    'score': ['Baixo', 'Baixo', 'Muito Bom', 'Muito Bom'],
    'idade': [36, 25, 19, 24],
    'dependentes': [0, 0, 4, 2],
    'estadocivil': ['Viúvo', 'Casado', 'Casado', 'Solteiro'],
    'produto': ['DoubleDuty', 'SpeedFury', 'ElegantCruise', 'TrailConqueror'],
    'valorsolicitado': [139244.0, 100000, 50000, 200000],
    'valortotalbem': [320000.0, 200000, 200000, 300000],
    'proporcaosolicitadototal': [2.2, 50, 200, 40]  # Esta coluna parece ter valores incorretos, pois a proporção não pode ser maior que 1
}

# Envio dos dados para a API usando uma requisição POST
response = requests.post(url, json=dados_novos) 

# Verificação da resposta da API
if response.status_code == 200:  # Código 200 indica sucesso
    print("Previsões recebidas:")
    predictions = response.json()  # Obtém as previsões (em formato JSON) da resposta
    print(predictions)
else:
    print("Erro ao fazer a previsão:", response.status_code)  # Imprime o código de erro em caso de falha
