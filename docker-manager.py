#!/usr/bin/env python
"""
Script de gerenciamento Docker para o projeto de Análise de Crédito.
"""

import subprocess
import sys
import time
import requests

def run_command(command, description):
    """Executa um comando e exibe o resultado."""
    print(f"\n🔄 {description}")
    print(f"Executando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Sucesso!")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ Erro:")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return False

def check_docker():
    """Verifica se o Docker está instalado e funcionando."""
    print("🐳 Verificando Docker...")
    
    if not run_command("docker --version", "Verificando instalação do Docker"):
        print("\n❌ Docker não está instalado!")
        print("Instale o Docker Desktop em: https://www.docker.com/products/docker-desktop/")
        return False
    
    if not run_command("docker-compose --version", "Verificando Docker Compose"):
        print("\n❌ Docker Compose não está instalado!")
        return False
    
    return True

def build_images():
    """Constrói as imagens Docker."""
    return run_command("docker-compose build", "Construindo imagens Docker")

def start_services():
    """Inicia os serviços."""
    return run_command("docker-compose up -d", "Iniciando serviços")

def stop_services():
    """Para os serviços."""
    return run_command("docker-compose down", "Parando serviços")

def show_logs():
    """Mostra os logs dos serviços."""
    run_command("docker-compose logs -f", "Visualizando logs")

def check_health():
    """Verifica a saúde dos serviços."""
    print("\n🏥 Verificando saúde dos serviços...")
    
    services = [
        ("API", "http://localhost:5000/health"),
        ("Streamlit", "http://localhost:8501"),
        ("Dashboard", "http://localhost:8502")
    ]
    
    for service, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service}: OK")
            else:
                print(f"⚠️ {service}: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {service}: Não acessível ({e})")

def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("""
🐳 Script de Gerenciamento Docker - Análise de Crédito

Uso: python docker-manager.py <comando>

Comandos disponíveis:
  check     - Verifica se Docker está instalado
  build     - Constrói as imagens
  start     - Inicia os serviços
  stop      - Para os serviços
  restart   - Reinicia os serviços
  logs      - Mostra os logs
  health    - Verifica saúde dos serviços
  full      - Setup completo (build + start + health)

Exemplos:
  python docker-manager.py full     # Setup completo
  python docker-manager.py health   # Verificar status
  python docker-manager.py logs     # Ver logs
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "check":
        check_docker()
    
    elif command == "build":
        if check_docker():
            build_images()
    
    elif command == "start":
        if check_docker():
            start_services()
            time.sleep(10)  # Aguarda os serviços iniciarem
            check_health()
    
    elif command == "stop":
        stop_services()
    
    elif command == "restart":
        if check_docker():
            stop_services()
            time.sleep(2)
            start_services()
            time.sleep(10)
            check_health()
    
    elif command == "logs":
        show_logs()
    
    elif command == "health":
        check_health()
    
    elif command == "full":
        if check_docker():
            print("🚀 Iniciando setup completo...")
            if build_images():
                if start_services():
                    print("⏳ Aguardando serviços iniciarem...")
                    time.sleep(15)
                    check_health()
                    print("""
🎉 Setup completo!

Acesse as aplicações:
• 🏦 App Principal: http://localhost:8501
• 📊 Dashboard: http://localhost:8502
• 🔌 API: http://localhost:5000/health

Para parar: python docker-manager.py stop
                    """)
    
    else:
        print(f"❌ Comando desconhecido: {command}")

if __name__ == "__main__":
    main()
