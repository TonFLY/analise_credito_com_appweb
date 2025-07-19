#!/usr/bin/env python3
"""
Script de Deploy Azure para o Sistema de Análise de Crédito
Automatiza o deploy em VM do Azure com Docker
Autor: TonFLY
Data: 2025
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

class AzureDeployManager:
    """Gerenciador de deploy para Azure"""
    
    def __init__(self):
        self.project_name = "analise-credito"
        self.resource_group = "rg-analise-credito"
        self.location = "Brazil South"  # ou "East US"
        self.vm_name = "vm-analise-credito"
        self.vm_size = "Standard_B2s"  # 2 vCPU, 4GB RAM
        self.admin_username = "azureuser"
        
        # Configurações de rede
        self.vnet_name = "vnet-analise-credito"
        self.subnet_name = "subnet-app"
        self.nsg_name = "nsg-analise-credito"
        self.public_ip_name = "ip-analise-credito"
        
        # Portas da aplicação
        self.app_ports = [22, 80, 443, 5000, 8501, 8502]
        
    def check_azure_cli(self):
        """Verifica se Azure CLI está instalado"""
        print("🔍 Verificando Azure CLI...")
        
        try:
            result = subprocess.run(
                ["az", "--version"], 
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("✅ Azure CLI encontrado")
                return True
            else:
                print("❌ Azure CLI não está funcionando")
                return False
        except FileNotFoundError:
            print("❌ Azure CLI não está instalado!")
            print("💡 Instale em: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
            return False
    
    def login_azure(self):
        """Faz login no Azure"""
        print("🔐 Fazendo login no Azure...")
        
        try:
            result = subprocess.run(["az", "login"], check=True)
            print("✅ Login realizado com sucesso")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro no login do Azure")
            return False
    
    def create_resource_group(self):
        """Cria o grupo de recursos"""
        print(f"📁 Criando grupo de recursos: {self.resource_group}")
        
        cmd = [
            "az", "group", "create",
            "--name", self.resource_group,
            "--location", self.location
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print("✅ Grupo de recursos criado")
            return True
        except subprocess.CalledProcessError as e:
            if "already exists" in str(e.stderr):
                print("✅ Grupo de recursos já existe")
                return True
            print(f"❌ Erro ao criar grupo de recursos: {e}")
            return False
    
    def create_network_security_group(self):
        """Cria o grupo de segurança de rede"""
        print(f"🔒 Criando NSG: {self.nsg_name}")
        
        # Criar NSG
        cmd = [
            "az", "network", "nsg", "create",
            "--resource-group", self.resource_group,
            "--name", self.nsg_name
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print("✅ NSG criado")
        except subprocess.CalledProcessError as e:
            if "already exists" in str(e.stderr):
                print("✅ NSG já existe")
            else:
                print(f"❌ Erro ao criar NSG: {e}")
                return False
        
        # Criar regras para as portas da aplicação
        for i, port in enumerate(self.app_ports):
            port_name = "SSH" if port == 22 else f"App-{port}"
            priority = 1000 + i * 10
            
            cmd = [
                "az", "network", "nsg", "rule", "create",
                "--resource-group", self.resource_group,
                "--nsg-name", self.nsg_name,
                "--name", f"Allow-{port_name}",
                "--protocol", "tcp",
                "--priority", str(priority),
                "--destination-port-range", str(port),
                "--access", "allow"
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"✅ Regra criada para porta {port}")
            except subprocess.CalledProcessError:
                print(f"⚠️ Regra para porta {port} já existe")
        
        return True
    
    def create_virtual_network(self):
        """Cria a rede virtual"""
        print(f"🌐 Criando VNet: {self.vnet_name}")
        
        cmd = [
            "az", "network", "vnet", "create",
            "--resource-group", self.resource_group,
            "--name", self.vnet_name,
            "--address-prefix", "10.0.0.0/16",
            "--subnet-name", self.subnet_name,
            "--subnet-prefix", "10.0.1.0/24"
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print("✅ VNet criada")
            return True
        except subprocess.CalledProcessError as e:
            if "already exists" in str(e.stderr):
                print("✅ VNet já existe")
                return True
            print(f"❌ Erro ao criar VNet: {e}")
            return False
    
    def create_public_ip(self):
        """Cria IP público"""
        print(f"🌍 Criando IP público: {self.public_ip_name}")
        
        cmd = [
            "az", "network", "public-ip", "create",
            "--resource-group", self.resource_group,
            "--name", self.public_ip_name,
            "--allocation-method", "Static",
            "--sku", "Standard"
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print("✅ IP público criado")
            return True
        except subprocess.CalledProcessError as e:
            if "already exists" in str(e.stderr):
                print("✅ IP público já existe")
                return True
            print(f"❌ Erro ao criar IP público: {e}")
            return False
    
    def create_virtual_machine(self):
        """Cria a máquina virtual"""
        print(f"🖥️ Criando VM: {self.vm_name}")
        
        cmd = [
            "az", "vm", "create",
            "--resource-group", self.resource_group,
            "--name", self.vm_name,
            "--image", "Ubuntu2004",
            "--size", self.vm_size,
            "--admin-username", self.admin_username,
            "--generate-ssh-keys",
            "--vnet-name", self.vnet_name,
            "--subnet", self.subnet_name,
            "--nsg", self.nsg_name,
            "--public-ip-address", self.public_ip_name,
            "--output", "json"
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            vm_info = json.loads(result.stdout)
            public_ip = vm_info.get("publicIpAddress")
            
            print("✅ VM criada com sucesso")
            print(f"🌍 IP Público: {public_ip}")
            
            # Salvar informações da VM
            self.save_vm_info(vm_info)
            return True, public_ip
            
        except subprocess.CalledProcessError as e:
            if "already exists" in str(e.stderr):
                print("✅ VM já existe")
                # Obter IP da VM existente
                public_ip = self.get_vm_public_ip()
                return True, public_ip
            print(f"❌ Erro ao criar VM: {e}")
            return False, None
    
    def get_vm_public_ip(self):
        """Obtém o IP público da VM"""
        cmd = [
            "az", "network", "public-ip", "show",
            "--resource-group", self.resource_group,
            "--name", self.public_ip_name,
            "--query", "ipAddress",
            "--output", "tsv"
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def save_vm_info(self, vm_info):
        """Salva informações da VM"""
        deploy_info = {
            "timestamp": datetime.now().isoformat(),
            "vm_info": vm_info,
            "access_urls": {
                "api": f"http://{vm_info.get('publicIpAddress')}:5000",
                "streamlit": f"http://{vm_info.get('publicIpAddress')}:8501",
                "dashboard": f"http://{vm_info.get('publicIpAddress')}:8502"
            }
        }
        
        with open("azure_deploy_info.json", "w") as f:
            json.dump(deploy_info, f, indent=2)
        
        print("💾 Informações de deploy salvas em 'azure_deploy_info.json'")
    
    def install_docker_on_vm(self, public_ip):
        """Instala Docker na VM"""
        print("🐳 Instalando Docker na VM...")
        
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release",
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
            "echo \"deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null",
            "sudo apt-get update",
            "sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin",
            "sudo usermod -aG docker $USER",
            "sudo systemctl enable docker",
            "sudo systemctl start docker"
        ]
        
        for cmd in commands:
            ssh_cmd = [
                "ssh", "-o", "StrictHostKeyChecking=no",
                f"{self.admin_username}@{public_ip}",
                cmd
            ]
            
            try:
                subprocess.run(ssh_cmd, check=True, capture_output=True)
                print(f"✅ Executado: {cmd[:50]}...")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Possível erro: {cmd[:30]}...")
        
        print("✅ Docker instalado na VM")
    
    def deploy_application(self, public_ip):
        """Faz deploy da aplicação"""
        print("🚀 Fazendo deploy da aplicação...")
        
        # Clonar repositório
        clone_cmd = [
            "ssh", "-o", "StrictHostKeyChecking=no",
            f"{self.admin_username}@{public_ip}",
            f"git clone https://github.com/TonFLY/analise_credito_com_appweb.git && cd analise_credito_com_appweb"
        ]
        
        try:
            subprocess.run(clone_cmd, check=True)
            print("✅ Repositório clonado")
        except subprocess.CalledProcessError:
            print("⚠️ Repositório pode já existir")
        
        # Executar setup com Docker
        setup_commands = [
            "cd analise_credito_com_appweb",
            "sudo docker-compose build",
            "sudo docker-compose up -d"
        ]
        
        for cmd in setup_commands:
            ssh_cmd = [
                "ssh", "-o", "StrictHostKeyChecking=no",
                f"{self.admin_username}@{public_ip}",
                cmd
            ]
            
            try:
                subprocess.run(ssh_cmd, check=True, timeout=600)
                print(f"✅ Executado: {cmd}")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                print(f"⚠️ Possível erro em: {cmd}")
        
        print("✅ Aplicação deployada")
    
    def show_access_info(self, public_ip):
        """Mostra informações de acesso"""
        print("\n" + "="*60)
        print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print(f"🌍 IP Público da VM: {public_ip}")
        print(f"👤 Usuário SSH: {self.admin_username}")
        print("\n🔗 URLs de Acesso:")
        print(f"  🏦 Aplicação Principal: http://{public_ip}:8501")
        print(f"  📊 Dashboard: http://{public_ip}:8502")
        print(f"  🔌 API: http://{public_ip}:5000/health")
        print("\n💻 Acesso SSH:")
        print(f"  ssh {self.admin_username}@{public_ip}")
        print("\n🐳 Comandos Docker na VM:")
        print("  sudo docker-compose logs -f")
        print("  sudo docker-compose restart")
        print("  sudo docker-compose down")
        print("="*60)
    
    def full_deploy(self):
        """Deploy completo"""
        print("🚀 INICIANDO DEPLOY COMPLETO NO AZURE")
        print("="*50)
        
        steps = [
            ("Verificando Azure CLI", self.check_azure_cli),
            ("Fazendo login", self.login_azure),
            ("Criando grupo de recursos", self.create_resource_group),
            ("Criando grupo de segurança", self.create_network_security_group),
            ("Criando rede virtual", self.create_virtual_network),
            ("Criando IP público", self.create_public_ip),
        ]
        
        # Executar passos iniciais
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ Falha em: {step_name}")
                return False
        
        # Criar VM
        print(f"\n📋 Criando VM...")
        success, public_ip = self.create_virtual_machine()
        if not success:
            return False
        
        # Aguardar VM inicializar
        print("⏳ Aguardando VM inicializar...")
        time.sleep(30)
        
        # Instalar Docker e fazer deploy
        try:
            self.install_docker_on_vm(public_ip)
            self.deploy_application(public_ip)
            self.show_access_info(public_ip)
            return True
        except Exception as e:
            print(f"❌ Erro no deploy: {e}")
            return False
    
    def cleanup(self):
        """Remove recursos do Azure"""
        print(f"🧹 Removendo recursos do grupo: {self.resource_group}")
        
        cmd = [
            "az", "group", "delete",
            "--name", self.resource_group,
            "--yes", "--no-wait"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ Recursos sendo removidos em background")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao remover recursos: {e}")

def main():
    """Função principal"""
    deploy = AzureDeployManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "deploy":
            deploy.full_deploy()
        elif command == "cleanup":
            deploy.cleanup()
        elif command == "info":
            # Mostrar informações se existir arquivo
            if Path("azure_deploy_info.json").exists():
                with open("azure_deploy_info.json") as f:
                    info = json.load(f)
                    public_ip = info["vm_info"]["publicIpAddress"]
                    deploy.show_access_info(public_ip)
            else:
                print("❌ Arquivo de informações não encontrado")
        else:
            print("❌ Comando inválido!")
            print("💡 Uso: python azure-deploy.py [deploy|cleanup|info]")
    else:
        print("""
🚀 Azure Deploy Manager - Análise de Crédito

Comandos disponíveis:
  deploy   - Deploy completo da aplicação
  cleanup  - Remove todos os recursos
  info     - Mostra informações de acesso

Exemplos:
  python azure-deploy.py deploy    # Deploy completo
  python azure-deploy.py info      # Ver URLs de acesso
  python azure-deploy.py cleanup   # Limpar recursos

⚠️  IMPORTANTE:
- Certifique-se de ter Azure CLI instalado
- Faça login no Azure antes de executar
- O deploy pode levar 10-15 minutos
- Recursos Azure geram custos!
        """)

if __name__ == "__main__":
    main()
