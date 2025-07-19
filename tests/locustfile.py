"""
Teste de carga para a API de Análise de Crédito
Usa Locust para simular múltiplos usuários
"""

from locust import HttpUser, task, between
import json
import random

class CreditAnalysisUser(HttpUser):
    wait_time = between(1, 3)  # Espera entre 1-3 segundos entre requests
    
    def on_start(self):
        """Executado quando o usuário inicia"""
        self.client.verify = False  # Desabilitar verificação SSL para testes
    
    @task(3)
    def health_check(self):
        """Testa o health check (mais frequente)"""
        self.client.get("/health")
    
    @task(1)
    def predict_credit_risk(self):
        """Testa predição de risco de crédito"""
        # Dados de exemplo para predição
        test_data = {
            "idade": random.randint(18, 80),
            "renda": random.randint(1000, 50000),
            "valor_solicitado": random.randint(1000, 100000),
            "tem_conta_corrente": random.choice([0, 1]),
            "tem_conta_poupanca": random.choice([0, 1]),
            "tem_emprego": random.choice([0, 1]),
            "sexo": random.choice([0, 1]),
            "estado_civil": random.randint(0, 3),
            "educacao": random.randint(0, 4),
            "anos_emprego": random.randint(0, 40)
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = self.client.post("/predict", 
                                  data=json.dumps(test_data),
                                  headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            # Verificar se a resposta tem a estrutura esperada
            if 'probability' in result or 'prediction' in result:
                print(f"✅ Predição realizada: {result}")
            else:
                print(f"⚠️ Resposta inesperada: {result}")
        else:
            print(f"❌ Erro na predição: {response.status_code}")

class WebAppUser(HttpUser):
    """Simula usuário acessando o Streamlit"""
    wait_time = between(2, 5)
    
    @task
    def access_webapp(self):
        """Acessa a página principal do Streamlit"""
        self.client.get("/")
    
    @task
    def health_monitoring(self):
        """Monitora se a aplicação está respondendo"""
        self.client.get("/health")  # Se houver endpoint de health no Streamlit
