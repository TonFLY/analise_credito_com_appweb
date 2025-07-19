#!/usr/bin/env python3
"""
Script de setup e automação para o projeto de Análise de Crédito
Autor: TonFLY
Data: 2025
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from config import Config, setup_logging

logger = setup_logging()

class ProjectSetup:
    """Classe para automatizar setup do projeto"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.required_dirs = ['objects', 'logs', 'tests']
        self.processes = {}
    
    def create_directories(self):
        """Cria diretórios necessários"""
        logger.info("🏗️ Criando diretórios...")
        
        for dir_name in self.required_dirs:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            logger.info(f"✅ Diretório criado: {dir_name}")
    
    def check_dependencies(self):
        """Verifica se as dependências estão instaladas"""
        logger.info("🔍 Verificando dependências...")
        
        try:
            import tensorflow
            import streamlit
            import flask
            import pandas
            import plotly
            logger.info("✅ Todas as dependências estão instaladas")
            return True
        except ImportError as e:
            logger.error(f"❌ Dependência ausente: {e}")
            logger.info("💡 Execute: pip install -r requirements.txt")
            return False
    
    def train_model(self):
        """Treina o modelo se não existir"""
        model_path = Path(Config.MODEL_PATH)
        
        if model_path.exists():
            logger.info("✅ Modelo já existe, pulando treinamento")
            return True
        
        logger.info("🤖 Iniciando treinamento do modelo...")
        try:
            result = subprocess.run(
                [sys.executable, "modelcreation.py"],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutos timeout
            )
            
            if result.returncode == 0:
                logger.info("✅ Modelo treinado com sucesso")
                return True
            else:
                logger.error(f"❌ Erro no treinamento: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout no treinamento do modelo")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado no treinamento: {e}")
            return False
    
    def start_api(self):
        """Inicia a API em background"""
        logger.info("🚀 Iniciando API...")
        
        try:
            # Usa a API melhorada
            api_script = "api_improved.py" if Path("api_improved.py").exists() else "api.py"
            
            process = subprocess.Popen(
                [sys.executable, api_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes['api'] = process
            
            # Aguarda alguns segundos e testa se está funcionando
            time.sleep(5)
            
            if self.test_api_health():
                logger.info("✅ API iniciada com sucesso")
                return True
            else:
                logger.error("❌ API não está respondendo")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar API: {e}")
            return False
    
    def test_api_health(self):
        """Testa se a API está saudável"""
        try:
            response = requests.get(
                f"http://{Config.API_HOST}:{Config.API_PORT}/health",
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def start_streamlit(self):
        """Inicia o Streamlit"""
        logger.info("🎨 Iniciando interface Streamlit...")
        
        try:
            process = subprocess.Popen(
                [
                    sys.executable, "-m", "streamlit", "run", "webapp.py",
                    "--server.address", "0.0.0.0",
                    "--server.port", str(Config.STREAMLIT_PORT)
                ]
            )
            
            self.processes['streamlit'] = process
            logger.info(f"✅ Streamlit iniciado em http://localhost:{Config.STREAMLIT_PORT}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Streamlit: {e}")
            return False
    
    def start_dashboard(self):
        """Inicia o dashboard"""
        if not Path("dashboard.py").exists():
            logger.warning("⚠️ Dashboard não encontrado, pulando...")
            return True
            
        logger.info("📊 Iniciando dashboard...")
        
        try:
            process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "dashboard.py",
                "--server.address", "0.0.0.0",
                "--server.port", "8502"
            ])
            
            self.processes['dashboard'] = process
            logger.info("✅ Dashboard iniciado em http://localhost:8502")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar dashboard: {e}")
            return False
    
    def run_tests(self):
        """Executa testes automatizados"""
        if not Path("tests").exists():
            logger.warning("⚠️ Pasta de testes não encontrada, pulando...")
            return True
            
        logger.info("🧪 Executando testes...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "-v"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Todos os testes passaram")
                return True
            else:
                logger.warning(f"⚠️ Alguns testes falharam: {result.stdout}")
                return True  # Não bloqueia o setup
                
        except FileNotFoundError:
            # pytest não instalado, tenta unittest
            logger.info("Pytest não encontrado, usando unittest...")
            return self.run_unittest()
    
    def run_unittest(self):
        """Executa testes com unittest"""
        try:
            result = subprocess.run([
                sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"
            ], capture_output=True, text=True)
            
            logger.info("✅ Testes unittest executados")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Erro nos testes: {e}")
            return True
    
    def cleanup(self):
        """Limpa processos em execução"""
        logger.info("🧹 Limpando processos...")
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                logger.info(f"✅ Processo {name} finalizado")
            except:
                pass
    
    def setup_complete(self):
        """Setup completo do projeto"""
        logger.info("🚀 Iniciando setup completo do projeto...")
        
        steps = [
            ("Criando diretórios", self.create_directories),
            ("Verificando dependências", self.check_dependencies),
            ("Treinando modelo", self.train_model),
            ("Executando testes", self.run_tests),
            ("Iniciando API", self.start_api),
            ("Iniciando Streamlit", self.start_streamlit),
            ("Iniciando Dashboard", self.start_dashboard),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 {step_name}...")
            
            if not step_func():
                logger.error(f"❌ Falha em: {step_name}")
                self.cleanup()
                return False
        
        logger.info("🎉 Setup completo!")
        logger.info("=" * 60)
        logger.info("🌐 URLs disponíveis:")
        logger.info(f"📱 App Principal: http://localhost:{Config.STREAMLIT_PORT}")
        logger.info(f"📊 Dashboard: http://localhost:8502")
        logger.info(f"🔗 API: http://localhost:{Config.API_PORT}")
        logger.info("=" * 60)
        
        return True

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        setup = ProjectSetup()
        
        if command == "complete":
            setup.setup_complete()
        elif command == "train":
            setup.create_directories()
            setup.train_model()
        elif command == "test":
            setup.run_tests()
        elif command == "api":
            setup.start_api()
            input("Pressione Enter para parar a API...")
            setup.cleanup()
        elif command == "streamlit":
            setup.start_streamlit()
            input("Pressione Enter para parar o Streamlit...")
            setup.cleanup()
        else:
            print("❌ Comando inválido!")
            print("💡 Uso: python setup.py [complete|train|test|api|streamlit]")
    else:
        # Setup interativo
        setup = ProjectSetup()
        try:
            setup.setup_complete()
            input("\n🎯 Pressione Enter para parar todos os serviços...")
        except KeyboardInterrupt:
            logger.info("\n⚡ Interrompido pelo usuário")
        finally:
            setup.cleanup()

if __name__ == "__main__":
    main()
