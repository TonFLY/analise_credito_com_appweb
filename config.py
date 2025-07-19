import os
import yaml
from dotenv import load_dotenv
import logging

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Classe centralizada de configurações usando variáveis de ambiente"""
    
    # Configurações do Banco de Dados
    DATABASE_CONFIG = {
        'dbname': os.getenv('DB_NAME', 'novadrivebank'),
        'user': os.getenv('DB_USER', 'etlreadonlybank'),
        'password': os.getenv('DB_PASSWORD', 'novadrive376A@'),
        'host': os.getenv('DB_HOST', '159.223.187.110'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    # Configurações da API
    API_HOST = os.getenv('API_HOST', '127.0.0.1')
    API_PORT = int(os.getenv('API_PORT', '5000'))
    API_DEBUG = os.getenv('API_DEBUG', 'true').lower() == 'true'
    API_URL = f"http://{API_HOST}:{API_PORT}/predict"
    
    # Configurações do Streamlit
    STREAMLIT_PORT = int(os.getenv('STREAMLIT_PORT', '8501'))
    
    # Configurações do Modelo
    MODEL_RANDOM_SEED = int(os.getenv('MODEL_RANDOM_SEED', '42'))
    MODEL_EPOCHS = int(os.getenv('MODEL_EPOCHS', '500'))
    MODEL_BATCH_SIZE = int(os.getenv('MODEL_BATCH_SIZE', '10'))
    MODEL_LEARNING_RATE = float(os.getenv('MODEL_LEARNING_RATE', '0.001'))
    
    # Configurações de Log
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Caminhos
    OBJECTS_DIR = './objects'
    LOGS_DIR = './logs'
    MODEL_PATH = f'{OBJECTS_DIR}/meu_modelo.keras'
    SELECTOR_PATH = f'{OBJECTS_DIR}/selector.joblib'

def setup_logging():
    """Configura o sistema de logging"""
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(f'{Config.LOGS_DIR}/app.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

# Compatibilidade com config.yaml existente (fallback)
def load_legacy_config():
    """Carrega configuração do arquivo YAML (para compatibilidade)"""
    try:
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return None
