#!/usr/bin/env python
"""
Script de inicialização para containers Docker.
Garante que todos os modelos e preprocessadores estejam disponíveis.
"""

import os
import sys
import subprocess
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_objects_directory():
    """Verifica se o diretório objects existe e tem os arquivos necessários."""
    objects_dir = './objects'
    
    if not os.path.exists(objects_dir):
        logger.info("Diretório objects não encontrado. Criando...")
        os.makedirs(objects_dir, exist_ok=True)
        return False
    
    # Lista de arquivos necessários
    required_files = [
        'modelo_mock.joblib',
        'selector.joblib'
    ]
    
    # Verificar se os scalers e encoders existem
    for i in range(7):  # 7 scalers
        required_files.append(f'scaler_{i}.joblib')
    
    for i in range(6):  # 6 encoders
        required_files.append(f'labelencoder_{i}.joblib')
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(os.path.join(objects_dir, file)):
            missing_files.append(file)
    
    if missing_files:
        logger.warning(f"Arquivos faltando: {missing_files}")
        return False
    
    logger.info("Todos os arquivos de modelo encontrados!")
    return True

def train_model():
    """Treina o modelo se necessário."""
    logger.info("Treinando modelo...")
    try:
        result = subprocess.run([sys.executable, 'model_mock.py'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            logger.info("Modelo treinado com sucesso!")
            return True
        else:
            logger.error(f"Erro no treinamento: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("Timeout no treinamento do modelo")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado no treinamento: {e}")
        return False

def main():
    """Função principal de inicialização."""
    logger.info("Iniciando setup do container...")
    
    # Verificar se os modelos existem
    if not check_objects_directory():
        logger.info("Modelos não encontrados. Iniciando treinamento...")
        if not train_model():
            logger.error("Falha no treinamento do modelo!")
            sys.exit(1)
    
    logger.info("Setup do container concluído com sucesso!")
    return True

if __name__ == "__main__":
    main()
