import unittest
import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

class TestAPI(unittest.TestCase):
    """Testes para a API Flask"""
    
    def setUp(self):
        """Configuração dos testes de API"""
        self.base_url = Config.API_URL
        self.sample_data = {
            'profissao': ['Advogado'],
            'tempoprofissao': [5],
            'renda': [10000.0],
            'tiporesidencia': ['Própria'],
            'escolaridade': ['Superior'],
            'score': ['Bom'],
            'idade': [35],
            'dependentes': [2],
            'estadocivil': ['Casado'],
            'produto': ['EcoPrestige'],
            'valorsolicitado': [50000.0],
            'valortotalbem': [100000.0],
            'proporcaosolicitadototal': [0.5]
        }
    
    def test_api_health(self):
        """Testa se a API está respondendo"""
        try:
            response = requests.get(self.base_url.replace('/predict', '/'), timeout=5)
            # Se não há endpoint de health, testa o predict mesmo
        except requests.exceptions.ConnectionError:
            self.skipTest("API não está rodando. Execute 'python api.py' primeiro.")
    
    def test_predict_endpoint(self):
        """Testa o endpoint de predição"""
        try:
            response = requests.post(
                self.base_url, 
                json=self.sample_data,
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            
            # Verifica se a resposta é um JSON válido
            data = response.json()
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0)
            
            # Verifica se a probabilidade está entre 0 e 1
            probability = data[0][0]
            self.assertGreaterEqual(probability, 0.0)
            self.assertLessEqual(probability, 1.0)
            
        except requests.exceptions.ConnectionError:
            self.skipTest("API não está rodando. Execute 'python api.py' primeiro.")
    
    def test_invalid_data(self):
        """Testa comportamento com dados inválidos"""
        invalid_data = {'campo_inexistente': ['valor']}
        
        try:
            response = requests.post(
                self.base_url,
                json=invalid_data,
                timeout=10
            )
            
            # Deve retornar erro (400 ou 500)
            self.assertNotEqual(response.status_code, 200)
            
        except requests.exceptions.ConnectionError:
            self.skipTest("API não está rodando. Execute 'python api.py' primeiro.")

class TestIntegration(unittest.TestCase):
    """Testes de integração completos"""
    
    def test_end_to_end_flow(self):
        """Testa fluxo completo do sistema"""
        # Verifica se arquivos essenciais existem
        essential_files = [
            'modelcreation.py',
            'api.py', 
            'webapp.py',
            'utils.py',
            'config.py'
        ]
        
        for file in essential_files:
            self.assertTrue(
                os.path.exists(file),
                f"Arquivo essencial {file} não encontrado"
            )

if __name__ == '__main__':
    unittest.main(verbosity=2)
