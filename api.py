# Importações de bibliotecas e módulos necessários
from flask import Flask, request, jsonify  # Framework web para criação de APIs
from tensorflow.keras.models import load_model  # Carregamento de modelos Keras
import pandas as pd  # Manipulação de dados em DataFrames
import joblib  # Carregamento de objetos serializados (no caso, o seletor de features)
from utils import *  # Importação de funções auxiliares (pré-processamento)

# Criação da instância do aplicativo Flask
app = Flask(__name__)  

# Carregamento do modelo Keras treinado
model = load_model('meu_modelo.keras')  

# Carregamento do seletor de features (pré-treinado)
selector_carregado = joblib.load('./objects/selector.joblib')  

# Definição da rota '/predict' para receber requisições POST
@app.route('/predict', methods=['POST'])  
def predict():
    # Obtém os dados JSON da requisição
    input_data = request.get_json()  
    
    # Converte os dados em um DataFrame Pandas
    df = pd.DataFrame(input_data)  

    # Aplica escalonamento (normalização/padronização) às colunas numéricas
    df = load_scalers(df, ['tempoprofissao', 'renda', 'idade', 'dependentes', 
                            'valorsolicitado', 'valortotalbem', 'proporcaosolicitadototal'])  
    
    # Aplica codificação (one-hot encoding, label encoding, etc.) às colunas categóricas
    df = load_encoders(df, ['profissao', 'tiporesidencia', 'escolaridade', 'score', 
                            'estadocivil', 'produto'])  
    
    # Seleciona as features mais importantes
    df = selector_carregado.transform(df)  

    # Realiza a previsão usando o modelo
    predictions = model.predict(df)  

    # Retorna as previsões como JSON
    return jsonify(predictions.tolist())  

# Verifica se o script está sendo executado diretamente
if __name__ == '__main__':  
    # Inicia o servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=True)  
    # host='0.0.0.0' permite acesso de qualquer IP
    # port=5000 define a porta
    # debug=True ativa o modo de depuração
