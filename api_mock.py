"""
API Mock para testes - Compatível com sklearn ao invés de TensorFlow
"""
from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import joblib
import os
import numpy as np
from datetime import datetime
import json
import time

app = Flask(__name__)

# Variáveis globais
model = None
selector = None
scalers = {}
encoders = {}

def load_model_artifacts():
    """Carrega modelo e artefatos"""
    global model, selector, scalers, encoders
    
    try:
        # Carrega modelo
        if os.path.exists('./objects/meu_modelo.joblib'):
            model = joblib.load('./objects/meu_modelo.joblib')
            print("✅ Modelo carregado (sklearn)")
        else:
            print("❌ Modelo não encontrado")
            return False
        
        # Carrega selector
        if os.path.exists('./objects/selector.joblib'):
            selector = joblib.load('./objects/selector.joblib')
            print("✅ Seletor carregado")
        else:
            print("❌ Seletor não encontrado")
            return False
        
        # Carrega scalers
        numeric_cols = ['tempoprofissao', 'renda', 'idade', 'dependentes', 'valorsolicitado', 'valortotalbem', 'proporcaosolicitadototal']
        for col in numeric_cols:
            scaler_path = f'./objects/scaler{col}.joblib'
            if os.path.exists(scaler_path):
                scalers[col] = joblib.load(scaler_path)
        
        # Carrega encoders
        categorical_cols = ['profissao', 'tiporesidencia', 'escolaridade', 'score', 'estadocivil', 'produto']
        for col in categorical_cols:
            encoder_path = f'./objects/labelencoder{col}.joblib'
            if os.path.exists(encoder_path):
                encoders[col] = joblib.load(encoder_path)
        
        print(f"✅ Carregados {len(scalers)} scalers e {len(encoders)} encoders")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar artefatos: {e}")
        return False

def log_prediction(input_data, prediction, probability, processing_time):
    """Log de predições"""
    os.makedirs('./logs', exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'input_data': input_data,
        'prediction': prediction,
        'probability': float(probability),
        'processing_time_ms': processing_time * 1000,
    }
    
    with open('./logs/predictions.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

# Carrega artefatos na inicialização
artifacts_loaded = load_model_artifacts()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    status = {
        'status': 'healthy' if artifacts_loaded else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None,
        'selector_loaded': selector is not None,
        'scalers_loaded': len(scalers),
        'encoders_loaded': len(encoders),
        'version': '2.0.0-mock'
    }
    
    return jsonify(status), 200 if artifacts_loaded else 503

@app.route('/', methods=['GET'])
def home():
    """Página inicial da API"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Mock - Análise de Crédito</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1 { color: #2c3e50; }
            .status { padding: 10px; border-radius: 5px; margin: 20px 0; }
            .healthy { background: #d5f4e6; color: #27ae60; }
            .unhealthy { background: #fadbd8; color: #e74c3c; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏦 API Mock - Análise de Crédito</h1>
            <div class="status {{ status_class }}">
                <strong>Status:</strong> {{ status }}
            </div>
            <h2>📡 Endpoints</h2>
            <p><strong>GET /health</strong> - Health check</p>
            <p><strong>POST /predict</strong> - Fazer predição</p>
            <h2>🧪 Versão de Teste</h2>
            <p>Esta é uma versão mock para testes, usando RandomForest ao invés de TensorFlow.</p>
        </div>
    </body>
    </html>
    """
    
    status = 'Funcionando ✅' if artifacts_loaded else 'Com Problemas ❌'
    status_class = 'healthy' if artifacts_loaded else 'unhealthy'
    
    return render_template_string(html, status=status, status_class=status_class)

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint de predição"""
    if not artifacts_loaded:
        return jsonify({'error': 'Modelo não disponível'}), 503
    
    start_time = time.time()
    
    try:
        # Obter dados
        input_data = request.get_json()
        if not input_data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        # Converter para DataFrame
        df = pd.DataFrame(input_data)
        
        # Aplicar scalers
        for col, scaler in scalers.items():
            if col in df.columns:
                df[col] = scaler.transform(df[[col]])
        
        # Aplicar encoders
        for col, encoder in encoders.items():
            if col in df.columns:
                try:
                    df[col] = encoder.transform(df[col])
                except ValueError:
                    # Se categoria não vista no treino, usar valor padrão
                    df[col] = 0
        
        # Selecionar features
        df_selected = selector.transform(df)
        
        # Fazer predição
        predictions_prob = model.predict_proba(df_selected)
        
        # Extrair probabilidade da classe positiva (índice 1 = 'bom')
        if predictions_prob.shape[1] > 1:
            results = [[float(prob[1])] for prob in predictions_prob]
        else:
            results = [[0.5] for _ in range(len(predictions_prob))]
        
        # Log
        processing_time = time.time() - start_time
        for i, result in enumerate(results):
            probability = result[0]
            classification = "Bom" if probability > 0.5 else "Ruim"
            log_prediction(input_data, classification, probability, processing_time)
        
        return jsonify(results)
        
    except Exception as e:
        print(f"❌ Erro na predição: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

if __name__ == '__main__':
    if artifacts_loaded:
        print("🚀 API Mock iniciando em http://127.0.0.1:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ Falha ao iniciar - execute primeiro: python model_mock.py")
        exit(1)
