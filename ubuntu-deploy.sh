#!/bin/bash
# Script de Deploy para VM Ubuntu Azure
# Análise de Crédito - Deploy Completo
# Autor: TonFLY

set -e  # Para caso qualquer comando falhe

echo "🚀 DEPLOY EM VM UBUNTU AZURE - ANÁLISE DE CRÉDITO"
echo "=================================================="

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Passo 1: Atualizar sistema
echo "📦 Atualizando sistema Ubuntu..."
sudo apt update && sudo apt upgrade -y
print_status "Sistema atualizado"

# Passo 2: Instalar dependências básicas
echo "🔧 Instalando dependências básicas..."
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    build-essential
print_status "Dependências básicas instaladas"

# Passo 3: Instalar Python 3.12
echo "🐍 Instalando Python 3.12..."
if ! command_exists python3.12; then
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip
    # Criar link simbólico
    sudo ln -sf /usr/bin/python3.12 /usr/bin/python3
    sudo ln -sf /usr/bin/python3.12 /usr/bin/python
else
    print_warning "Python 3.12 já está instalado"
fi
print_status "Python 3.12 configurado"

# Passo 4: Instalar Docker
echo "🐳 Instalando Docker..."
if ! command_exists docker; then
    # Remover versões antigas
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Adicionar repositório Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Instalar Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Adicionar usuário ao grupo docker
    sudo usermod -aG docker $USER
    
    # Instalar docker-compose standalone
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Iniciar Docker
    sudo systemctl enable docker
    sudo systemctl start docker
else
    print_warning "Docker já está instalado"
fi
print_status "Docker instalado e configurado"

# Passo 5: Clonar repositório
echo "📥 Clonando repositório do projeto..."
cd /home/$USER
if [ -d "analise_credito_com_appweb" ]; then
    print_warning "Repositório já existe, fazendo pull..."
    cd analise_credito_com_appweb
    git pull origin main
else
    git clone https://github.com/TonFLY/analise_credito_com_appweb.git
    cd analise_credito_com_appweb
fi
print_status "Repositório clonado/atualizado"

# Passo 6: Configurar ambiente Python
echo "🏗️ Configurando ambiente Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_status "Ambiente Python configurado"

# Passo 7: Treinar modelo
echo "🤖 Treinando modelo de ML..."
python model_mock.py
print_status "Modelo treinado com sucesso"

# Passo 8: Configurar firewall para as portas
echo "🔥 Configurando firewall..."
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 5000  # API
sudo ufw allow 8501  # Streamlit
sudo ufw allow 8502  # Dashboard
sudo ufw --force enable
print_status "Firewall configurado"

# Passo 9: Criar arquivo de ambiente
echo "⚙️ Criando arquivo de ambiente..."
cat > .env << EOF
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=false
STREAMLIT_PORT=8501
DATABASE_URL=sqlite:///credit_analysis.db
LOG_LEVEL=INFO
EOF
print_status "Arquivo .env criado"

# Passo 10: Deploy com Docker (opção 1)
echo "🚀 Iniciando deploy com Docker..."
echo "Escolha uma opção de deploy:"
echo "1) Docker Compose (Recomendado)"
echo "2) Deploy manual sem Docker"
echo "3) Apenas configurar (não iniciar serviços)"

read -p "Digite sua escolha (1-3): " choice

case $choice in
    1)
        echo "🐳 Iniciando com Docker Compose..."
        # Logout e login necessário para grupo docker
        print_warning "IMPORTANTE: Após este script, faça logout/login ou execute: newgrp docker"
        sudo docker-compose build
        sudo docker-compose up -d
        sleep 10
        echo ""
        print_status "Deploy Docker concluído!"
        echo "🏦 Aplicação: http://$(curl -s ifconfig.me):8501"
        echo "📊 Dashboard: http://$(curl -s ifconfig.me):8502" 
        echo "🔌 API: http://$(curl -s ifconfig.me):5000/health"
        ;;
    2)
        echo "📱 Deploy manual..."
        # Ativar ambiente virtual
        source venv/bin/activate
        
        # Iniciar API em background
        nohup python api_mock.py > logs/api.log 2>&1 &
        echo $! > api.pid
        
        # Aguardar API iniciar
        sleep 5
        
        # Iniciar Streamlit em background
        nohup streamlit run webapp.py --server.address=0.0.0.0 --server.port=8501 > logs/streamlit.log 2>&1 &
        echo $! > streamlit.pid
        
        # Iniciar Dashboard em background  
        nohup streamlit run dashboard.py --server.address=0.0.0.0 --server.port=8502 > logs/dashboard.log 2>&1 &
        echo $! > dashboard.pid
        
        sleep 5
        print_status "Deploy manual concluído!"
        echo "🏦 Aplicação: http://$(curl -s ifconfig.me):8501"
        echo "📊 Dashboard: http://$(curl -s ifconfig.me):8502"
        echo "🔌 API: http://$(curl -s ifconfig.me):5000/health"
        ;;
    3)
        echo "✅ Configuração concluída!"
        echo "Para iniciar manualmente:"
        echo "  Docker: sudo docker-compose up -d"
        echo "  Manual: source venv/bin/activate && python api_mock.py"
        ;;
    *)
        print_error "Opção inválida"
        exit 1
        ;;
esac

# Criar scripts de controle
echo "📝 Criando scripts de controle..."

# Script para parar serviços
cat > stop_services.sh << 'EOF'
#!/bin/bash
echo "🛑 Parando serviços..."

# Parar Docker se estiver rodando
if command -v docker-compose >/dev/null 2>&1; then
    sudo docker-compose down 2>/dev/null || true
fi

# Parar processos manuais
if [ -f api.pid ]; then
    kill $(cat api.pid) 2>/dev/null || true
    rm api.pid
fi

if [ -f streamlit.pid ]; then
    kill $(cat streamlit.pid) 2>/dev/null || true
    rm streamlit.pid
fi

if [ -f dashboard.pid ]; then
    kill $(cat dashboard.pid) 2>/dev/null || true  
    rm dashboard.pid
fi

echo "✅ Serviços parados"
EOF

# Script para iniciar serviços
cat > start_services.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando serviços..."

if command -v docker-compose >/dev/null 2>&1; then
    echo "Usando Docker Compose..."
    sudo docker-compose up -d
else
    echo "Iniciando manualmente..."
    source venv/bin/activate
    
    mkdir -p logs
    nohup python api_mock.py > logs/api.log 2>&1 &
    echo $! > api.pid
    
    sleep 3
    
    nohup streamlit run webapp.py --server.address=0.0.0.0 --server.port=8501 > logs/streamlit.log 2>&1 &
    echo $! > streamlit.pid
    
    nohup streamlit run dashboard.py --server.address=0.0.0.0 --server.port=8502 > logs/dashboard.log 2>&1 &
    echo $! > dashboard.pid
fi

echo "✅ Serviços iniciados"
echo "🏦 App: http://$(curl -s ifconfig.me):8501"
echo "🔌 API: http://$(curl -s ifconfig.me):5000/health"
EOF

# Script para ver status
cat > status_services.sh << 'EOF'
#!/bin/bash
echo "📊 Status dos serviços..."

IP=$(curl -s ifconfig.me)

# Testar API
if curl -s http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ API: Funcionando - http://$IP:5000"
else
    echo "❌ API: Não responde"
fi

# Testar Streamlit
if curl -s http://localhost:8501 >/dev/null 2>&1; then
    echo "✅ Streamlit: Funcionando - http://$IP:8501"
else
    echo "❌ Streamlit: Não responde"
fi

# Testar Dashboard
if curl -s http://localhost:8502 >/dev/null 2>&1; then
    echo "✅ Dashboard: Funcionando - http://$IP:8502"
else
    echo "❌ Dashboard: Não responde"
fi

# Processos Docker
if command -v docker >/dev/null 2>&1; then
    echo ""
    echo "🐳 Containers Docker:"
    sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Nenhum container rodando"
fi
EOF

chmod +x *.sh
print_status "Scripts de controle criados"

echo ""
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "================================="
echo ""
echo "📱 URLs da aplicação:"
PUBLIC_IP=$(curl -s ifconfig.me)
echo "🏦 Aplicação Principal: http://$PUBLIC_IP:8501"
echo "📊 Dashboard: http://$PUBLIC_IP:8502"
echo "🔌 API Health Check: http://$PUBLIC_IP:5000/health"
echo ""
echo "🔧 Scripts de controle:"
echo "  ./start_services.sh   - Iniciar serviços"
echo "  ./stop_services.sh    - Parar serviços"  
echo "  ./status_services.sh  - Ver status"
echo ""
echo "📋 Logs disponíveis em:"
echo "  logs/api.log"
echo "  logs/streamlit.log"
echo "  logs/dashboard.log"
echo ""

if [ "$choice" = "1" ]; then
    print_warning "⚠️ IMPORTANTE para Docker:"
    echo "Execute: sudo usermod -aG docker $USER"
    echo "Depois faça logout/login ou: newgrp docker"
fi

echo ""
print_status "Sistema pronto para uso! 🚀"
