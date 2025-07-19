#!/usr/bin/env python3
"""
Deploy Simplificado Azure Container Instances (ACI)
Deploy rápido e econômico usando containers na Azure
Autor: TonFLY
"""

import subprocess
import json
import time
from datetime import datetime

class AzureACIDeploy:
    """Deploy usando Azure Container Instances"""
    
    def __init__(self):
        self.resource_group = "rg-analise-credito-aci"
        self.location = "Brazil South"
        self.container_group = "cg-analise-credito"
        
    def check_and_login(self):
        """Verifica Azure CLI e faz login"""
        print("🔍 Verificando Azure CLI...")
        
        try:
            subprocess.run(["az", "--version"], check=True, capture_output=True)
            print("✅ Azure CLI encontrado")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("❌ Azure CLI não encontrado!")
            return False
        
        try:
            print("🔐 Fazendo login...")
            subprocess.run(["az", "login"], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def create_resource_group(self):
        """Cria grupo de recursos"""
        cmd = [
            "az", "group", "create",
            "--name", self.resource_group,
            "--location", self.location
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Grupo de recursos criado: {self.resource_group}")
            return True
        except subprocess.CalledProcessError as e:
            if "already exists" in str(e.stderr):
                print(f"✅ Grupo já existe: {self.resource_group}")
                return True
            return False
    
    def deploy_container_group(self):
        """Deploy do container group com a aplicação"""
        print("🚀 Fazendo deploy dos containers...")
        
        # YAML do container group
        container_yaml = f"""
apiVersion: 2021-07-01
location: {self.location}
name: {self.container_group}
properties:
  containers:
  - name: api-container
    properties:
      image: python:3.12-slim
      resources:
        requests:
          cpu: 1.0
          memoryInGb: 2.0
      ports:
      - port: 5000
      command:
      - "/bin/bash"
      - "-c"
      - |
        apt-get update && apt-get install -y git curl gcc g++ && 
        git clone https://github.com/TonFLY/analise_credito_com_appweb.git /app &&
        cd /app && 
        pip install -r requirements.txt && 
        python model_mock.py &&
        python api_mock.py
  - name: streamlit-container
    properties:
      image: python:3.12-slim
      resources:
        requests:
          cpu: 1.0
          memoryInGb: 2.0
      ports:
      - port: 8501
      command:
      - "/bin/bash"
      - "-c"
      - |
        apt-get update && apt-get install -y git curl && 
        git clone https://github.com/TonFLY/analise_credito_com_appweb.git /app &&
        cd /app && 
        pip install -r requirements.txt && 
        streamlit run webapp.py --server.address=0.0.0.0 --server.port=8501
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 5000
    - protocol: tcp
      port: 8501
    dnsNameLabel: analise-credito-{int(time.time())}
  restartPolicy: Always
tags:
  project: analise-credito
  environment: production
"""
        
        # Salvar YAML temporariamente
        with open("container-group.yaml", "w") as f:
            f.write(container_yaml)
        
        # Deploy usando YAML
        cmd = [
            "az", "container", "create",
            "--resource-group", self.resource_group,
            "--file", "container-group.yaml"
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Container group deployado!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro no deploy: {e}")
            return False
    
    def get_container_info(self):
        """Obtém informações do container"""
        cmd = [
            "az", "container", "show",
            "--resource-group", self.resource_group,
            "--name", self.container_group,
            "--output", "json"
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            info = json.loads(result.stdout)
            
            ip = info["properties"]["ipAddress"]["ip"]
            fqdn = info["properties"]["ipAddress"].get("fqdn", ip)
            
            print("\n" + "="*60)
            print("🎉 DEPLOY ACI CONCLUÍDO!")
            print("="*60)
            print(f"🌍 IP Público: {ip}")
            print(f"🌐 FQDN: {fqdn}")
            print(f"🏦 Aplicação: http://{fqdn}:8501")
            print(f"🔌 API: http://{fqdn}:5000/health")
            print("="*60)
            
            # Salvar informações
            deploy_info = {
                "timestamp": datetime.now().isoformat(),
                "ip": ip,
                "fqdn": fqdn,
                "urls": {
                    "app": f"http://{fqdn}:8501",
                    "api": f"http://{fqdn}:5000"
                }
            }
            
            with open("aci_deploy_info.json", "w") as f:
                json.dump(deploy_info, f, indent=2)
            
            return True
            
        except subprocess.CalledProcessError:
            return False
    
    def cleanup(self):
        """Remove recursos"""
        cmd = [
            "az", "group", "delete",
            "--name", self.resource_group,
            "--yes", "--no-wait"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Removendo recursos: {self.resource_group}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao remover: {e}")
    
    def deploy(self):
        """Deploy completo"""
        print("🚀 DEPLOY AZURE CONTAINER INSTANCES")
        print("="*40)
        
        if not self.check_and_login():
            return False
        
        if not self.create_resource_group():
            return False
        
        if not self.deploy_container_group():
            return False
        
        print("⏳ Aguardando containers inicializarem...")
        time.sleep(60)
        
        return self.get_container_info()

def main():
    """Função principal"""
    import sys
    
    deploy = AzureACIDeploy()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "deploy":
            deploy.deploy()
        elif command == "cleanup":
            deploy.cleanup()
        elif command == "info":
            import json
            from pathlib import Path
            
            if Path("aci_deploy_info.json").exists():
                with open("aci_deploy_info.json") as f:
                    info = json.load(f)
                    print("🌍 IP:", info["ip"])
                    print("🏦 App:", info["urls"]["app"])
                    print("🔌 API:", info["urls"]["api"])
            else:
                print("❌ Informações de deploy não encontradas")
        else:
            print("Comandos: deploy, cleanup, info")
    else:
        print("""
🚀 Azure Container Instances Deploy

Comandos:
  python azure-aci-deploy.py deploy    # Deploy rápido
  python azure-aci-deploy.py info      # Ver URLs  
  python azure-aci-deploy.py cleanup   # Limpar

💰 ACI é mais barato que VMs!
⚡ Deploy em ~5 minutos
        """)

if __name__ == "__main__":
    main()
