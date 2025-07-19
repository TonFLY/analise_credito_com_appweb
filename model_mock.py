"""
Modelo Mock para testes - Simula o comportamento do modelo real
Usado quando TensorFlow não está disponível
"""
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import RFE
import random

# Configuração
seed = 42
np.random.seed(seed)
random.seed(seed)

print("🚀 Iniciando treinamento do modelo MOCK (para testes)")
print("=" * 60)

# Simular dados (já que não temos acesso ao banco)
def create_mock_data():
    """Cria dados sintéticos para teste"""
    n_samples = 1000
    
    profissoes = ['Advogado', 'Médico', 'Engenheiro', 'Contador', 'Programador']
    residencias = ['Própria', 'Alugada', 'Outros']
    escolaridades = ['Superior', 'Pós ou Mais', 'Ens.Médio', 'Ens.Fundamental']
    scores = ['Muito Bom', 'Bom', 'Justo', 'Baixo']
    estados = ['Casado', 'Solteiro', 'Divorciado', 'Viúvo']
    produtos = ['EcoPrestige', 'SpeedFury', 'WorkMaster', 'AgileXplorer']
    
    data = {
        'profissao': np.random.choice(profissoes, n_samples),
        'tempoprofissao': np.random.randint(0, 30, n_samples),
        'renda': np.random.uniform(2000, 20000, n_samples),
        'tiporesidencia': np.random.choice(residencias, n_samples),
        'escolaridade': np.random.choice(escolaridades, n_samples),
        'score': np.random.choice(scores, n_samples),
        'idade': np.random.randint(18, 70, n_samples),
        'dependentes': np.random.randint(0, 5, n_samples),
        'estadocivil': np.random.choice(estados, n_samples),
        'produto': np.random.choice(produtos, n_samples),
        'valorsolicitado': np.random.uniform(10000, 100000, n_samples),
        'valortotalbem': np.random.uniform(20000, 150000, n_samples),
    }
    
    df = pd.DataFrame(data)
    df['proporcaosolicitadototal'] = df['valorsolicitado'] / df['valortotalbem']
    
    # Criar target baseado em regras simples
    df['classe'] = 'bom'
    df.loc[(df['renda'] < 3000) | (df['score'] == 'Baixo'), 'classe'] = 'ruim'
    df.loc[df['proporcaosolicitadototal'] > 0.8, 'classe'] = 'ruim'
    
    return df

# Criar diretórios
os.makedirs('./objects', exist_ok=True)
os.makedirs('./logs', exist_ok=True)

print("📊 Gerando dados sintéticos...")
df = create_mock_data()
print(f"✅ Dataset criado com {len(df)} amostras")

# Preparar dados
X = df.drop('classe', axis=1)
y = df['classe']

print("🔄 Dividindo dados em treino e teste...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)

# Salvar scalers
print("📊 Salvando scalers...")
numeric_cols = ['tempoprofissao', 'renda', 'idade', 'dependentes', 'valorsolicitado', 'valortotalbem', 'proporcaosolicitadototal']

for col in numeric_cols:
    scaler = StandardScaler()
    X_train[col] = scaler.fit_transform(X_train[[col]])
    X_test[col] = scaler.transform(X_test[[col]])
    joblib.dump(scaler, f'./objects/scaler{col}.joblib')

# Salvar encoders
print("🏷️ Salvando encoders...")
categorical_cols = ['profissao', 'tiporesidencia', 'escolaridade', 'score', 'estadocivil', 'produto']

for col in categorical_cols:
    encoder = LabelEncoder()
    X_train[col] = encoder.fit_transform(X_train[col])
    X_test[col] = encoder.transform(X_test[col])
    joblib.dump(encoder, f'./objects/labelencoder{col}.joblib')

# Target encoding
label_encoder_y = LabelEncoder()
y_train_encoded = label_encoder_y.fit_transform(y_train)
y_test_encoded = label_encoder_y.transform(y_test)

# Seleção de features
print("🎯 Selecionando features...")
rf = RandomForestClassifier(random_state=seed)
selector = RFE(rf, n_features_to_select=10, step=1)
X_train_selected = selector.fit_transform(X_train, y_train_encoded)
X_test_selected = selector.transform(X_test)
joblib.dump(selector, './objects/selector.joblib')

# Treinar modelo final
print("🤖 Treinando modelo RandomForest...")
model = RandomForestClassifier(n_estimators=100, random_state=seed)
model.fit(X_train_selected, y_train_encoded)

# Salvar modelo como joblib (simulando o .keras)
joblib.dump(model, './objects/meu_modelo.joblib')

# Criar arquivo .keras fake para compatibilidade
with open('./objects/meu_modelo.keras', 'w') as f:
    f.write('# Mock model file for testing')

print("💾 Modelo salvo!")

# Avaliação
print("📈 Avaliando modelo...")
y_pred = model.predict(X_test_selected)
print("\n📊 Relatório de Classificação:")
print(classification_report(y_test_encoded, y_pred, target_names=['ruim', 'bom']))

print("=" * 60)
print("✅ Treinamento do modelo MOCK concluído!")
print("📁 Arquivos salvos em ./objects/")
print("🎯 Modelo pronto para uso na API!")
