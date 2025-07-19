import logging
import time
import json
import os
from datetime import datetime
from functools import wraps
from config import Config

class ModelLogger:
    """Logger especializado para operações de ML"""
    
    def __init__(self):
        self.logger = logging.getLogger('model_logger')
        self.predictions_log = f'{Config.LOGS_DIR}/predictions.log'
        self.performance_log = f'{Config.LOGS_DIR}/performance.log'
        
    def log_prediction(self, input_data, prediction, probability, processing_time):
        """Log de predições individuais"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'input_data': input_data,
            'prediction': prediction,
            'probability': float(probability),
            'processing_time_ms': processing_time * 1000,
        }
        
        with open(self.predictions_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
    def log_model_performance(self, metrics):
        """Log de métricas do modelo"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        }
        
        with open(self.performance_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

def timing_decorator(func):
    """Decorator para medir tempo de execução"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger = logging.getLogger(__name__)
        logger.info(f"{func.__name__} executado em {execution_time:.4f}s")
        
        return result, execution_time
    return wrapper

def error_handler(func):
    """Decorator para tratamento de erros"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper
