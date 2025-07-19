# 🚀 GUIA DE DEPLOY - VM UBUNTU AZURE

## 📋 **PASSO A PASSO COMPLETO**

### **Passo 1: Conectar na VM Ubuntu**
```bash
# Substitua pelo IP da sua VM
ssh azureuser@SEU_IP_PUBLICO
```

### **Passo 2: Executar Setup Automático**

**Opção A - Setup Completo (Recomendado):**
```bash
# Baixar e executar script de setup
curl -fsSL https://raw.githubusercontent.com/TonFLY/analise_credito_com_appweb/main/ubuntu-setup.sh -o setup.sh
chmod +x setup.sh
./setup.sh
```

**Opção B - Comandos Manuais:**
```bash
# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências
sudo apt install -y git python3-pip python3-venv curl

# 3. Clonar projeto
git clone https://github.com/TonFLY/analise_credito_com_appweb.git
cd analise_credito_com_appweb

# 4. Configurar ambiente
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Treinar modelo
python model_mock.py

# 6. Iniciar serviços
# Terminal 1 - API
python api_mock.py &

# Terminal 2 - Streamlit
streamlit run webapp.py --server.address=0.0.0.0 --server.port=8501 &

# Terminal 3 - Dashboard
streamlit run dashboard.py --server.address=0.0.0.0 --server.port=8502 &
```

### **Passo 3: Configurar Portas Azure**

No portal Azure, configure o Network Security Group:
- **Porta 22**: SSH (já deve estar aberta)
- **Porta 5000**: API Flask
- **Porta 8501**: Streamlit App
- **Porta 8502**: Dashboard

### **Passo 4: Acessar Aplicação**

Após o setup, acesse:
- 🏦 **App Principal**: `http://SEU_IP:8501`
- 📊 **Dashboard**: `http://SEU_IP:8502`
- 🔌 **API**: `http://SEU_IP:5000/health`

---

## 🐳 **OPÇÃO DOCKER (Mais Robusta)**

Se preferir usar Docker:

```bash
# Conectar na VM
ssh azureuser@SEU_IP

# Instalar Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

# Clonar e executar
git clone https://github.com/TonFLY/analise_credito_com_appweb.git
cd analise_credito_com_appweb

# Deploy com Docker
docker-compose up -d

# Verificar status
docker-compose ps
docker-compose logs -f
```

---

## 🔧 **COMANDOS ÚTEIS NA VM**

### **Verificar Status:**
```bash
# Processos em execução
ps aux | grep python
ps aux | grep streamlit

# Portas abertas
sudo netstat -tlnp | grep -E ':5000|:8501|:8502'

# Logs do sistema
sudo journalctl -f
```

### **Gerenciar Serviços:**
```bash
# Parar serviços
sudo systemctl stop analise-credito-api
sudo systemctl stop analise-credito-app

# Iniciar serviços
sudo systemctl start analise-credito-api
sudo systemctl start analise-credito-app

# Ver logs
sudo journalctl -u analise-credito-api -f
```

### **Reiniciar Aplicação:**
```bash
cd /home/azureuser/analise_credito_com_appweb
git pull origin main
source venv/bin/activate
sudo systemctl restart analise-credito-api
sudo systemctl restart analise-credito-app
```

---

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Se a aplicação não carregar:**
```bash
# Verificar se Python está funcionando
python3 --version

# Verificar se as dependências estão instaladas
pip list | grep streamlit
pip list | grep flask

# Verificar se as portas estão abertas
sudo ufw status
sudo ufw allow 8501
sudo ufw allow 5000
```

### **Se der erro de permissão:**
```bash
# Dar permissões corretas
sudo chown -R $USER:$USER /home/$USER/analise_credito_com_appweb
chmod +x *.py
```

### **Se o modelo não funcionar:**
```bash
# Retreinar o modelo
cd analise_credito_com_appweb
source venv/bin/activate
python model_mock.py
```

---

## ✅ **CHECKLIST DE VERIFICAÇÃO**

- [ ] VM Ubuntu conectada via SSH
- [ ] Git instalado e projeto clonado
- [ ] Python 3.x instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Modelo treinado (`python model_mock.py`)
- [ ] Portas liberadas no Azure NSG (5000, 8501, 8502)
- [ ] Firewall Ubuntu configurado
- [ ] Serviços rodando (API + Streamlit)
- [ ] Aplicação acessível pelo navegador

---

**🎯 Com esse guia, sua aplicação estará funcionando na VM Ubuntu em poucos minutos!**
