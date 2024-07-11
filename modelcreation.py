# Importações
import pandas as pd                 # Manipulação de dados
from datetime import datetime       # Manipulação de datas
import numpy as np                  # Operações numéricas
import random as python_random      # Geração de números aleatórios
import joblib                       # Serialização de objetos Python (para salvar modelos)

from sklearn.preprocessing import StandardScaler, LabelEncoder  # Pré-processamento
from sklearn.model_selection import train_test_split           # Divisão dos dados
from sklearn.metrics import classification_report, confusion_matrix  # Avaliação do modelo
from sklearn.ensemble import RandomForestClassifier             # Modelo Random Forest
from sklearn.feature_selection import RFE                       # Seleção de características
import tensorflow as tf                                       # Framework de Deep Learning

from utils import *                 # Funções auxiliares personalizadas
import const                       # Constantes (provavelmente a consulta SQL)

# Reprodutibilidade (garantindo que os resultados sejam consistentes)
seed = 42
np.random.seed(seed)
python_random.seed(seed)
tf.random.set_seed(seed)

# Carregamento dos dados brutos do banco de dados
df = fetch_data_from_db(const.consulta_sql)

# Conversão de tipos de dados (para garantir que estejam corretos)
df['idade'] = df['idade'].astype(int)
df['valorsolicitado'] = df['valorsolicitado'].astype(float)
df['valortotalbem'] = df['valortotalbem'].astype(float)

# Tratamento de valores nulos (substituição por valores adequados)
substitui_nulos(df)

# Correção de erros de digitação em uma coluna específica
profissoes_validas = ['Advogado', 'Arquiteto', 'Cientista de Dados', 'Contador', 'Dentista', 'Empresário', 'Engenheiro', 'Médico', 'Programador']
corrigir_erros_digitacao(df, 'profissao', profissoes_validas)

# Tratamento de outliers (valores extremos) em colunas numéricas
df = tratar_outliers(df, 'tempoprofissao', 0, 70)
df = tratar_outliers(df, 'idade', 0, 110)

# Feature Engineering (criação de novas características a partir das existentes)
df['proporcaosolicitadototal'] = df['valorsolicitado'] / df['valortotalbem']
df['proporcaosolicitadototal'] = df['proporcaosolicitadototal'].astype(float)

# Divisão dos dados em conjuntos de treino e teste
X = df.drop('classe', axis=1)  # Características (entradas)
y = df['classe']              # Rótulos (saídas)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)

# Normalização (escalonamento) das características numéricas
X_test = save_scalers(X_test, ['tempoprofissao', 'renda', 'idade', 'dependentes', 'valorsolicitado', 'valortotalbem', 'proporcaosolicitadototal'])
X_train = save_scalers(X_train, ['tempoprofissao', 'renda', 'idade', 'dependentes', 'valorsolicitado', 'valortotalbem', 'proporcaosolicitadototal'])

# Codificação dos rótulos (convertendo de 'ruim' e 'bom' para 0 e 1)
mapeamento = {'ruim': 0, 'bom': 1}
y_train = np.array([mapeamento[item] for item in y_train])
y_test = np.array([mapeamento[item] for item in y_test])

# Codificação das características categóricas
X_train = save_encoders(X_train, ['profissao', 'tiporesidencia', 'escolaridade', 'score', 'estadocivil', 'produto'])
X_test = save_encoders(X_test, ['profissao', 'tiporesidencia', 'escolaridade', 'score', 'estadocivil', 'produto'])

# Seleção de Atributos (usando Recursive Feature Elimination)
model = RandomForestClassifier()
selector = RFE(model, n_features_to_select=10, step=1)  # Seleciona as 10 melhores características
selector = selector.fit(X_train, y_train)
X_train = selector.transform(X_train)
X_test = selector.transform(X_test)
joblib.dump(selector, './objects/selector.joblib')  # Salva o seletor para uso posterior

# Criação do modelo de rede neural (Keras)
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),  # Camada densa com 128 neurônios e ativação ReLU
    tf.keras.layers.Dropout(0.3),                                                    # Dropout para evitar overfitting
    tf.keras.layers.Dense(64, activation='relu'),                                   # Camada densa com 64 neurônios e ativação ReLU
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(1, activation='sigmoid')                                  # Camada de saída com ativação sigmoide para classificação binária
])

# Configuração do otimizador e compilação do modelo
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

# Treinamento do modelo
model.fit(X_train, y_train, validation_split=0.3, epochs=500, batch_size=10, verbose=1)

# Salvando o modelo treinado
model.save('meu_modelo.keras')

# Previsões nos dados de teste
y_pred = model.predict(X_test)
y_pred = (y_pred > 0.5).astype(int)  # Convertendo probabilidades em classes (0 ou 1)

# Avaliação do modelo
print("Avaliação do Modelo nos Dados de Teste:")
model.evaluate(X_test, y_test)

# Métricas de classificação (precisão, recall, f1-score, etc.)
print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred))
