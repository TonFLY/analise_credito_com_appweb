# Importações de bibliotecas e módulos necessários
from flask import Flask, request, jsonify, render_template_string
from tensorflow.keras.models import load_model
import pandas as pd
import joblib
import os
from datetime import datetime
from config import Config, setup_logging
from logger import ModelLogger, timing_decorator, error_handler
from utils import load_scalers, load_encoders

# Setup de logging
logger = setup_logging()
model_logger = ModelLogger()

# Criação da instância do aplicativo Flask
app = Flask(__name__)

# Carregamento do modelo e seletor
model = None
selector_carregado = None

def load_model_artifacts():
    """Carrega modelo e artefatos com tratamento de erro"""
    global model, selector_carregado
    
    try:
        if os.path.exists(Config.MODEL_PATH):
            model = load_model(Config.MODEL_PATH)
            logger.info(f"Modelo carregado: {Config.MODEL_PATH}")
        else:
            logger.error(f"Modelo não encontrado: {Config.MODEL_PATH}")
            return False
            
        if os.path.exists(Config.SELECTOR_PATH):
            selector_carregado = joblib.load(Config.SELECTOR_PATH)
            logger.info(f"Seletor carregado: {Config.SELECTOR_PATH}")
        else:
            logger.error(f"Seletor não encontrado: {Config.SELECTOR_PATH}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Erro ao carregar artefatos: {e}")
        return False

# Carrega artefatos na inicialização
artifacts_loaded = load_model_artifacts()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    status = {
        'status': 'healthy' if artifacts_loaded else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None,
        'selector_loaded': selector_carregado is not None,
        'version': '2.0.0'
    }
    
    return jsonify(status), 200 if artifacts_loaded else 503

@app.route('/', methods=['GET'])
def home():
    """Página inicial da API"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Análise de Crédito</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .endpoint { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .method { background: #3498db; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
            .status { padding: 10px; border-radius: 5px; margin: 20px 0; }
            .healthy { background: #d5f4e6; color: #27ae60; }
            .unhealthy { background: #fadbd8; color: #e74c3c; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏦 API de Análise de Crédito v2.0</h1>
            
            <div class="status {{ status_class }}">
                <strong>Status:</strong> {{ status }}
            </div>
            
            <h2>📡 Endpoints Disponíveis</h2>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <strong>/health</strong> - Verificação de saúde da API
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <strong>/predict</strong> - Realizar predição de crédito
            </div>
            
            <h2>📊 Exemplo de Uso</h2>
            <pre>
curl -X POST http://{{ host }}:{{ port }}/predict \
-H "Content-Type: application/json" \
-d '{
    "profissao": ["Advogado"],
    "tempoprofissao": [5],
    "renda": [10000.0],
    "tiporesidencia": ["Própria"],
    "escolaridade": ["Superior"],
    "score": ["Bom"],
    "idade": [35],
    "dependentes": [2],
    "estadocivil": ["Casado"],
    "produto": ["EcoPrestige"],
    "valorsolicitado": [50000.0],
    "valortotalbem": [100000.0],
    "proporcaosolicitadototal": [0.5]
}'
            </pre>
            
            <p><strong>Desenvolvido por TonFLY | 2025</strong></p>
        </div>
    </body>
    </html>
    """
    
    status = 'Saudável ✅' if artifacts_loaded else 'Com Problemas ❌'
    status_class = 'healthy' if artifacts_loaded else 'unhealthy'
    
    return render_template_string(
        html_template,
        status=status,
        status_class=status_class,
        host=Config.API_HOST,
        port=Config.API_PORT
    )

@app.route('/predict', methods=['POST'])
@error_handler
@timing_decorator
def predict():
    """Endpoint de predição melhorado com logging"""
    if not artifacts_loaded:
        logger.error("Tentativa de predição com artefatos não carregados")
        return jsonify({'error': 'Modelo não disponível'}), 503
    
    # Obtém os dados JSON da requisição
    input_data = request.get_json()
    
    if not input_data:
        logger.warning("Requisição sem dados JSON")
        return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
    
    logger.info(f"Nova predição solicitada com {len(input_data)} features")
    
    # Converte os dados em um DataFrame Pandas
    df = pd.DataFrame(input_data)
    
    # Valida se todas as colunas necessárias estão presentes
    required_columns = [
        'profissao', 'tempoprofissao', 'renda', 'tiporesidencia', 
        'escolaridade', 'score', 'idade', 'dependentes', 'estadocivil', 
        'produto', 'valorsolicitado', 'valortotalbem', 'proporcaosolicitadototal'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.warning(f"Colunas ausentes: {missing_columns}")
        return jsonify({'error': f'Colunas ausentes: {missing_columns}'}), 400
    
    # Aplica pré-processamento
    try:
        df = load_scalers(df, ['tempoprofissao', 'renda', 'idade', 'dependentes',
                              'valorsolicitado', 'valortotalbem', 'proporcaosolicitadototal'])
        
        df = load_encoders(df, ['profissao', 'tiporesidencia', 'escolaridade', 'score',
                               'estadocivil', 'produto'])
        
        df = selector_carregado.transform(df)
        
        # Realiza a previsão
        predictions = model.predict(df)
        
        # Log da predição
        for i, pred in enumerate(predictions):
            probability = float(pred[0])
            classification = "Bom" if probability > 0.5 else "Ruim"
            
            # Log detalhado (apenas na primeira iteração para evitar spam)
            if hasattr(predict, '_timing_info'):
                processing_time = predict._timing_info
                model_logger.log_prediction(
                    input_data=input_data,
                    prediction=classification,
                    probability=probability,
                    processing_time=processing_time
                )
        
        logger.info(f"Predição concluída. Resultado: {predictions.tolist()}")
        return jsonify(predictions.tolist())
        
    except Exception as e:
        logger.error(f"Erro durante predição: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handler para erro 404"""
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para erro 500"""
    logger.error(f"Erro interno: {error}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    # Cria diretórios necessários
    os.makedirs(Config.OBJECTS_DIR, exist_ok=True)
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    
    if artifacts_loaded:
        logger.info(f"🚀 API iniciando em http://{Config.API_HOST}:{Config.API_PORT}")
        logger.info(f"📊 Dashboard disponível em http://localhost:8502")
        
        app.run(
            host=Config.API_HOST,
            port=Config.API_PORT,
            debug=Config.API_DEBUG
        )
    else:
        logger.error("❌ Falha ao iniciar API - artefatos não carregados")
        logger.info("💡 Execute primeiro: python modelcreation.py")
        exit(1)
