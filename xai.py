# Importações
import pandas as pd                 # Manipulação de dados
from datetime import datetime       # Manipulação de datas (não utilizada neste código)
import numpy as np                  # Operações numéricas
import random as python_random      # Geração de números aleatórios
import joblib                       # Serialização de objetos Python (para salvar modelos)

from sklearn.preprocessing import StandardScaler, LabelEncoder  # Pré-processamento
from sklearn.model_selection import train_test_split           # Divisão dos dados
from sklearn.metrics import classification_report, confusion_matrix  # Avaliação do modelo
from sklearn.ensemble import RandomForestClassifier             # Modelo Random Forest (não usado aqui)
# from sklearn.feature_selection import RFE                       # Seleção de características (comentado)
import tensorflow as tf                                       # Framework de Deep Learning
import lime                                                   # Explicabilidade do modelo (LIME)
import lime.lime_tabular

from utils import *                 # Funções auxiliares personalizadas
import const                       # Constantes (provavelmente a consulta SQL)

# Reprodutibilidade (garantindo que os resultados sejam consistentes)
seed = 41  # Alterado para 41
np.random.seed(seed)
python_random.seed(seed)
tf.random.set_seed(seed)

# Carregamento dos dados brutos do banco de dados
df = fetch_data_from_db(const.consulta_sql)

# Conversão de tipos de dados e tratamento de nulos e erros de digitação
df['idade'] = df['idade'].astype(int)
df['valorsolicitado'] = df['valorsolicitado'].astype(float)
df['valortotalbem'] = df['valortotalbem'].astype(float)
substitui_nulos(df)

profissoes_validas = ['Advogado', 'Arquiteto', 'Cientista de Dados', 'Contador', 'Dentista', 'Empresário', 'Engenheiro', 'Médico', 'Programador']
corrigir_erros_digitacao(df, 'profissao', profissoes_validas)

# Tratamento de outliers
df = tratar_outliers(df, 'tempoprofissao', 0, 70)
df = tratar_outliers(df, 'idade', 0, 110)

# Feature Engineering
df['proporcaosolicitadototal'] = df['valorsolicitado'] / df['valortotalbem']
df['proporcaosolicitadototal'] = df['proporcaosolicitadototal'].astype(float)

# Divisão dos dados
X = df.drop('classe', axis=1)
y = df['classe']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)

# Normalização e Codificação (salvando transformadores)
X_test = save_scalers(X_test, ['tempoprofissao','renda','idade', 'dependentes','valorsolicitado','valortotalbem','proporcaosolicitadototal'])
X_train = save_scalers(X_train, ['tempoprofissao','renda','idade', 'dependentes','valorsolicitado','valortotalbem','proporcaosolicitadototal'])

mapeamento = {'ruim': 0, 'bom': 1}
y_train = np.array([mapeamento[item] for item in y_train])
y_test = np.array([mapeamento[item] for item in y_test])
X_train = save_encoders(X_train, ['profissao', 'tiporesidencia', 'escolaridade','score','estadocivil','produto'])
X_test = save_encoders(X_test, ['profissao', 'tiporesidencia', 'escolaridade','score','estadocivil','produto'])

# Criação e Treinamento do Modelo Keras (sem RFE)
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(1, activation='sigmoid')  
])
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, validation_split=0.2, epochs=500, batch_size=10, verbose=1)
model.save('meu_modelo.keras')


# Previsões e Avaliação
y_pred = model.predict(X_test)
y_pred = (y_pred > 0.5).astype(int)
print("Avaliação do Modelo nos Dados de Teste:")
model.evaluate(X_test, y_test)
print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred))

# Função para Previsões com Pré-processamento (para LIME)
def model_predict(data_asarray):  
    data_asframe = pd.DataFrame(data_asarray, columns=X_train.columns)  
    data_asframe = load_scalers(data_asframe, ['tempoprofissao', 'renda', 'idade', 'dependentes', 'valorsolicitado', 'valortotalbem', 'proporcaosolicitadototal'])
    data_asframe = load_encoders(data_asframe, ['profissao', 'tiporesidencia', 'escolaridade', 'score', 'estadocivil', 'produto'])
    predictions = model.predict(data_asframe)
    return np.hstack((1-predictions, predictions))  # Retorna probabilidades para ambas as classes

# Explicabilidade com LIME
explainer = lime.lime_tabular.LimeTabularExplainer(
    X_train.values, 
    feature_names=X_train.columns, 
    class_names=['ruim', 'bom'], 
    mode='classification'
)

# Explicação para a primeira instância do conjunto de teste (você pode mudar o índice)
exp = explainer.explain_instance(X_test.values[1], model_predict, num_features=10)
exp.save_to_file('lime_explanation.html')  # Salva a explicação em um arquivo HTML

# Exibindo os pesos das features para a classe 'bom'
print('\nRecursos e seus pesos para a classe "Bom":')
for feature, weight in exp.as_list(label=1):  # 1 representa a classe 'bom'
    print(f"{feature}: {weight}")
