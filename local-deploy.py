#!/usr/bin/env python3
"""
Script de Deploy Local para Desenvolvimento
Deploy rápido para testes locais com Docker
Autor: TonFLY
"""

import subprocess
import time
import requests
import os
import sys
from pathlib import Path

class LocalDeploy:
    """Gerenciador de deploy local"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.processes = []
    
    def check_requirements(self):
        """Verifica se todos os requisitos estão atendidos"""
        print("🔍 Verificando requisitos...")
        
        checks = [
            ("Python", self.check_python),
            ("Docker (opcional)", self.check_docker),
            ("Dependências", self.check_dependencies),
            ("Arquivos de modelo", self.check_model_files)
        ]
        
        all_good = True
        for name, check_func in checks:
            if check_func():
                print(f"✅ {name}: OK")
            else:
                print(f"⚠️ {name}: Problema detectado")
                if name == "Dependências":
                    all_good = False
        
        return all_good
    
    def check_python(self):
        """Verifica versão do Python"""
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 8:
                return True
            return False
        except:
            return False
    
    def check_docker(self):
        """Verifica se Docker está disponível"""
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def check_dependencies(self):
        """Verifica se dependências estão instaladas"""
        try:
            import flask, streamlit, pandas, numpy, sklearn
            return True
        except ImportError:
            return False
    
    def check_model_files(self):
        """Verifica se arquivos de modelo existem"""
        objects_dir = self.project_root / "objects"
        if not objects_dir.exists():
            return False
        
        required_files = ["modelo_mock.joblib", "selector.joblib"]
        for file in required_files:
            if not (objects_dir / file).exists():
                return False
        
        return True
    
    def install_dependencies(self):
        """Instala dependências"""
        print("📦 Instalando dependências...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                         check=True, capture_output=True)
            print("✅ Dependências instaladas")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na instalação: {e}")
            return False
    
    def train_model_if_needed(self):
        """Treina modelo se necessário"""
        if self.check_model_files():
            print("✅ Modelo já existe")
            return True
        
        print("🤖 Treinando modelo...")
        try:
            subprocess.run([sys.executable, "model_mock.py"], 
                         check=True, timeout=300)
            print("✅ Modelo treinado")
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print("❌ Erro no treinamento")
            return False
    
    def start_api_local(self):
        """Inicia API localmente"""
        print("🚀 Iniciando API...")
        
        try:
            process = subprocess.Popen([sys.executable, "api_mock.py"],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            self.processes.append(("API", process))
            
            # Aguarda API inicializar
            time.sleep(3)
            
            # Testa se está funcionando
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API funcionando em http://localhost:5000")
                return True
            else:
                print("❌ API não está respondendo")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar API: {e}")
            return False
    
    def start_streamlit_local(self):
        """Inicia Streamlit localmente"""
        print("🎨 Iniciando Streamlit...")
        
        try:
            process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "webapp.py",
                "--server.address", "localhost",
                "--server.port", "8501",
                "--server.headless", "true"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(("Streamlit", process))
            print("✅ Streamlit iniciado em http://localhost:8501")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar Streamlit: {e}")
            return False
    
    def start_dashboard_local(self):
        """Inicia Dashboard localmente"""
        if not Path("dashboard.py").exists():
            print("⚠️ Dashboard não encontrado")
            return True
        
        print("📊 Iniciando Dashboard...")
        
        try:
            process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "dashboard.py",
                "--server.address", "localhost",
                "--server.port", "8502",
                "--server.headless", "true"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(("Dashboard", process))
            print("✅ Dashboard iniciado em http://localhost:8502")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar Dashboard: {e}")
            return False
    
    def deploy_with_docker(self):
        """Deploy usando Docker"""
        print("🐳 Deploy com Docker...")
        
        try:
            # Build
            subprocess.run(["docker-compose", "build"], check=True)
            print("✅ Images construídas")
            
            # Up
            subprocess.run(["docker-compose", "up", "-d"], check=True)
            print("✅ Containers iniciados")
            
            # Aguardar inicialização
            time.sleep(15)
            
            # Verificar saúde
            services = [
                ("API", "http://localhost:5000/health"),
                ("Streamlit", "http://localhost:8501"),
                ("Dashboard", "http://localhost:8502")
            ]
            
            for name, url in services:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        print(f"✅ {name}: Funcionando")
                    else:
                        print(f"⚠️ {name}: Status {response.status_code}")
                except:
                    print(f"❌ {name}: Não acessível")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro no Docker: {e}")
            return False
    
    def cleanup(self):
        """Limpa processos"""
        print("🧹 Limpando processos...")
        
        for name, process in self.processes:
            try:
                process.terminate()
                print(f"✅ {name} finalizado")
            except:
                pass
        
        # Limpar Docker se necessário
        try:
            subprocess.run(["docker-compose", "down"], 
                         capture_output=True)
        except:
            pass
    
    def run_tests(self):
        """Executa testes"""
        print("🧪 Executando testes...")
        
        test_files = [
            "tests/test_utils.py",
            "tests/test_api.py",
            "test_prediction.py"
        ]
        
        for test_file in test_files:
            if Path(test_file).exists():
                try:
                    subprocess.run([sys.executable, test_file], 
                                 check=True, timeout=30)
                    print(f"✅ {test_file}: Passou")
                except:
                    print(f"⚠️ {test_file}: Falhou")
            else:
                print(f"⚠️ {test_file}: Não encontrado")
    
    def deploy_local(self, use_docker=False):
        """Deploy local completo"""
        print("🚀 DEPLOY LOCAL - ANÁLISE DE CRÉDITO")
        print("="*50)
        
        # Verificar requisitos
        if not self.check_requirements():
            print("❌ Requisitos não atendidos!")
            
            if not self.check_dependencies():
                print("📦 Tentando instalar dependências...")
                if not self.install_dependencies():
                    return False
        
        # Treinar modelo se necessário
        if not self.train_model_if_needed():
            return False
        
        # Executar testes
        self.run_tests()
        
        # Deploy
        if use_docker and self.check_docker():
            success = self.deploy_with_docker()
        else:
            steps = [
                self.start_api_local,
                self.start_streamlit_local,
                self.start_dashboard_local
            ]
            
            success = all(step() for step in steps)
        
        if success:
            print("\n🎉 DEPLOY LOCAL CONCLUÍDO!")
            print("="*40)
            print("🏦 App Principal: http://localhost:8501")
            print("📊 Dashboard: http://localhost:8502")
            print("🔌 API: http://localhost:5000/health")
            print("="*40)
            print("\n💡 Pressione Ctrl+C para parar")
        
        return success

def main():
    """Função principal"""
    deploy = LocalDeploy()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "docker":
            deploy.deploy_local(use_docker=True)
        elif command == "local":
            deploy.deploy_local(use_docker=False)
        elif command == "test":
            deploy.run_tests()
        elif command == "check":
            deploy.check_requirements()
        elif command == "clean":
            deploy.cleanup()
        else:
            print("Comandos: docker, local, test, check, clean")
    else:
        print("""
🚀 Local Deploy Manager

Comandos:
  python local-deploy.py local    # Deploy local (sem Docker)
  python local-deploy.py docker   # Deploy com Docker  
  python local-deploy.py test     # Executar testes
  python local-deploy.py check    # Verificar requisitos
  python local-deploy.py clean    # Limpar processos

Exemplo:
  python local-deploy.py local    # Deploy rápido para dev
        """)
        
        try:
            deploy.deploy_local(use_docker=False)
            input("\n🎯 Pressione Enter para parar...")
        except KeyboardInterrupt:
            print("\n⚡ Interrompido pelo usuário")
        finally:
            deploy.cleanup()

if __name__ == "__main__":
    main()
