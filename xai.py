import pandas as pd
from datetime import datetime
import numpy as np
import random as python_random
import joblib

from sklearn.preprocessing import StandardScaler,LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
import tensorflow as tf

from utils import *
import const

#reprodutividade
seed = 41
np.random.seed(seed)
python_random.seed(seed)
tf.random.set_seed(seed)

#dados brutos
df = fetch_data_from_db(const.consulta_sql)

#conversão de tipo
df['idade'] = df['idade'].astype(int)
df['valorsolicitado'] = df['valorsolicitado'].astype(float)
df['valortotalbem'] = df['valortotalbem'].astype(float)

#Tratamento de Nulos
substitui_nulos(df)

#Trata Erros de Digitação
profissoes_validas = ['Advogado', 'Arquiteto', 'Cientista de Dados', 'Contador','Dentista','Empresário',
                                       'Engenheiro','Médico','Programador']
corrigir_erros_digitacao(df, 'profissao', profissoes_validas)

#Trata Outliers
df = tratar_outliers(df, 'tempoprofissao', 0, 70)
df = tratar_outliers(df, 'idade', 0, 110)

#Feature Engineering
df['proporcaosolicitadototal'] = df['valorsolicitado'] / df['valortotalbem']
df['proporcaosolicitadototal'] = df['proporcaosolicitadototal'].astype(float)

# Dividindo Dados
X = df.drop('classe', axis=1)
y = df['classe']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, 
                                                    random_state=seed)
# Normalização
X_test = save_scalers(X_test, ['tempoprofissao','renda','idade',
                               'dependentes','valorsolicitado','valortotalbem','proporcaosolicitadototal'])
X_train = save_scalers(X_train, ['tempoprofissao','renda','idade',
                                 'dependentes','valorsolicitado','valortotalbem','proporcaosolicitadototal'])

#Codificação
mapeamento = {'ruim': 0, 'bom': 1}
y_train = np.array([mapeamento[item] for item in y_train])
y_test = np.array([mapeamento[item] for item in y_test])
X_train = save_encoders(X_train, ['profissao', 'tiporesidencia', 
                                  'escolaridade','score','estadocivil','produto'])
X_test = save_encoders(X_test, ['profissao', 'tiporesidencia', 
                                'escolaridade','score','estadocivil','produto'])

'''
# Seleção de Atributos
model = RandomForestClassifier()
# Instancia o RFE
selector = RFE(model, n_features_to_select=10, step=1)
selector = selector.fit(X_train, y_train)
# Transforma os dados
X_train = selector.transform(X_train)
X_test = selector.transform(X_test)
joblib.dump(selector, './objects/selector.joblib')'''

model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
# Configurando o otimizador
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
# Compilando o modelo
model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

# Treinamento do modelo 
model.fit(
    X_train,
    y_train,
    validation_split=0.2,  # Usa 20% dos dados para validação
    epochs=500,  # Número máximo de épocas
    batch_size=10,
    verbose=1
)
model.save('meu_modelo.keras')

# Previsões
y_pred = model.predict(X_test)
y_pred = (y_pred > 0.5).astype(int)  

# Avaliando o modelo
print("Avaliação do Modelo nos Dados de Teste:")
model.evaluate(X_test, y_test)

# Métricas de classificação
print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred))

# Função de Previsão Ajustada para LIME
def model_predict(data_asarray):
    data_asframe = pd.DataFrame(data_asarray, columns=X_train.columns)
    data_asframe = save_scalers(data_asframe, ['tempoprofissao', 'renda', 'idade', 'dependentes', 'valorsolicitado', 'valortotalbem', 'proporcaosolicitadototal'])
    data_asframe = save_encoders(data_asframe, ['profissao', 'tiporesidencia', 'escolaridade', 'score', 'estadocivil', 'produto'])
    predictions = model.predict(data_asframe)
    return np.hstack((1-predictions, predictions))

import lime
import lime.lime_tabular

# cria explainer
explainer = lime.lime_tabular.LimeTabularExplainer(X_train.values, 
                feature_names=X_train.columns, class_names=['ruim', 'bom'], mode='classification')
exp = explainer.explain_instance(X_test.values[1], model_predict, num_features=10)
#gera html
exp.save_to_file('lime_explanation.html')

print('\nImprimindo os recursos e seus pesos para Bom')
if 1 in exp.local_exp:
    for feature, weight in exp.local_exp[1]:
        print(f"{feature}: {weight}")

print("\nAcessar os valores das features e seus pesos para Bom")
feature_importances = exp.as_list(label=1)
for feature, weight in feature_importances:
    print(f"{feature}: {weight}")
        

