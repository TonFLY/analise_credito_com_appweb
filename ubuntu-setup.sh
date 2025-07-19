#!/bin/bash
# Script de Setup Completo para Ubuntu Azure VM
# Análise de Crédito com Aplicação Web
# Autor: TonFLY

set -e  # Para na primeira falha

echo "🚀 INICIANDO SETUP COMPLETO - ANÁLISE DE CRÉDITO"
echo "=================================================="

# Função para imprimir status
print_status() {
    echo "✅ $1"
}

print_error() {
    echo "❌ $1"
}

print_info() {
    echo "🔄 $1"
}

# 1. Atualizar sistema
print_info "Atualizando sistema Ubuntu..."
sudo apt-get update -y
sudo apt-get upgrade -y
print_status "Sistema atualizado"

# 2. Instalar dependências básicas
print_info "Instalando dependências básicas..."
sudo apt-get install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv
print_status "Dependências básicas instaladas"

# 3. Instalar Python 3.12
print_info "Instalando Python 3.12..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update -y
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
print_status "Python 3.12 instalado"

# 4. Instalar Docker
print_info "Instalando Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker
print_status "Docker instalado"

# 5. Instalar Docker Compose
print_info "Instalando Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
print_status "Docker Compose instalado"

# 6. Configurar firewall
print_info "Configurando firewall..."
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5000  # API
sudo ufw allow 8501  # Streamlit
sudo ufw allow 8502  # Dashboard
print_status "Firewall configurado"

# 7. Clonar repositório
print_info "Clonando repositório..."
cd /home/$USER
if [ -d "analise_credito_com_appweb" ]; then
    rm -rf analise_credito_com_appweb
fi
git clone https://github.com/TonFLY/analise_credito_com_appweb.git
cd analise_credito_com_appweb
print_status "Repositório clonado"

# 8. Configurar ambiente Python
print_info "Configurando ambiente Python..."
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_status "Ambiente Python configurado"

# 9. Treinar modelo
print_info "Treinando modelo ML..."
python model_mock.py
print_status "Modelo treinado"

# 10. Testar API
print_info "Testando API..."
python test_prediction.py &
sleep 5
print_status "API testada"

# 11. Criar serviços systemd
print_info "Criando serviços do sistema..."

# Serviço da API
sudo tee /etc/systemd/system/analise-credito-api.service > /dev/null <<EOF
[Unit]
Description=Análise de Crédito API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/analise_credito_com_appweb
Environment=PATH=/home/$USER/analise_credito_com_appweb/venv/bin
ExecStart=/home/$USER/analise_credito_com_appweb/venv/bin/python api_mock.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Serviço do Streamlit
sudo tee /etc/systemd/system/analise-credito-app.service > /dev/null <<EOF
[Unit]
Description=Análise de Crédito Streamlit App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/analise_credito_com_appweb
Environment=PATH=/home/$USER/analise_credito_com_appweb/venv/bin
ExecStart=/home/$USER/analise_credito_com_appweb/venv/bin/streamlit run webapp.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Serviço do Dashboard
sudo tee /etc/systemd/system/analise-credito-dashboard.service > /dev/null <<EOF
[Unit]
Description=Análise de Crédito Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/analise_credito_com_appweb
Environment=PATH=/home/$USER/analise_credito_com_appweb/venv/bin
ExecStart=/home/$USER/analise_credito_com_appweb/venv/bin/streamlit run dashboard.py --server.address=0.0.0.0 --server.port=8502 --server.headless=true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

print_status "Serviços criados"

# 12. Habilitar e iniciar serviços
print_info "Iniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl enable analise-credito-api
sudo systemctl enable analise-credito-app
sudo systemctl enable analise-credito-dashboard
sudo systemctl start analise-credito-api
sleep 5
sudo systemctl start analise-credito-app
sleep 5
sudo systemctl start analise-credito-dashboard
print_status "Serviços iniciados"

# 13. Verificar status
print_info "Verificando status dos serviços..."
sudo systemctl status analise-credito-api --no-pager
sudo systemctl status analise-credito-app --no-pager
sudo systemctl status analise-credito-dashboard --no-pager

# 14. Obter IP público
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com/)

echo ""
echo "🎉 SETUP CONCLUÍDO COM SUCESSO!"
echo "=================================="
echo "🌍 IP Público: $PUBLIC_IP"
echo ""
echo "🔗 URLs de Acesso:"
echo "  🏦 App Principal: http://$PUBLIC_IP:8501"
echo "  📊 Dashboard: http://$PUBLIC_IP:8502"
echo "  🔌 API: http://$PUBLIC_IP:5000/health"
echo ""
echo "📋 Comandos Úteis:"
echo "  sudo systemctl status analise-credito-api    # Status API"
echo "  sudo systemctl restart analise-credito-app   # Reiniciar App"
echo "  sudo systemctl logs -f analise-credito-api   # Ver logs"
echo "  docker-compose up -d                         # Usar Docker"
echo ""
echo "🔧 Logs dos Serviços:"
echo "  sudo journalctl -u analise-credito-api -f"
echo "  sudo journalctl -u analise-credito-app -f"
echo ""
echo "✅ Sistema pronto para uso!"
