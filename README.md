# 🏦 Análise de Crédito com Aplicação Web

Uma aplicação completa de Machine Learning para análise de risco de crédito, implementada com arquitetura em 3 camadas: banco de dados PostgreSQ### **🐳 Execução com Docker (Recomendado para Produção)**

#### **Pré-requisitos Docker:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado
- 4GB RAM disponível para containers
- 2GB espaço em disco

#### **Setup Automático com Docker:**
```powershell
# Verificar se Docker está funcionando
python docker-manager.py check

# Setup completo automático (build + start + health check)
python docker-manager.py full

# Ou manualmente:
docker-compose build
docker-compose up -d

# Verificar status dos serviços
python docker-manager.py health
```

#### **Gerenciamento de Containers:**
```powershell
# Parar todos os serviços
python docker-manager.py stop
# ou
docker-compose down

# Reiniciar serviços
python docker-manager.py restart

# Ver logs em tempo real
python docker-manager.py logs
# ou
docker-compose logs -f

# Verificar saúde dos serviços
python docker-manager.py health
```

#### **Acessar Aplicações Docker:**
- 🏦 **App Principal**: http://localhost:8501
- 📊 **Dashboard**: http://localhost:8502  
- 🔌 **API Health**: http://localhost:5000/health

#### **Arquitetura Docker:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Container │    │Streamlit Container│    │Dashboard Container│
│   Port: 5000    │────│   Port: 8501     │    │   Port: 8502     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                        ┌─────────────────┐
                        │ credit_network  │
                        │   (Bridge)      │
                        └─────────────────┘
``` com modelo de rede neural, e interface web Streamlit.

## 📋 Descrição do Projeto

Este projeto implementa um sistema completo de análise de crédito que simula o processo de avaliação de risco em instituições financeiras. O sistema utiliza aprendizado de máquina para prever a probabilidade de inadimplência de clientes com base em seus dados pessoais e financeiros.

### 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │───▶│   API Flask     │───▶│  Streamlit UI   │
│  (Dados)        │    │  (ML Model)     │    │  (Interface)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Fluxo de Dados:**
1. **Extração**: Dados extraídos do PostgreSQL via consulta SQL complexa
2. **Processamento**: Limpeza, feature engineering e pré-processamento
3. **Modelo**: Rede neural com 4 camadas densas para classificação binária  
4. **API**: Endpoint Flask que serve o modelo treinado
5. **Interface**: Streamlit para entrada de dados e visualização de resultados
## ⚙️ Funcionalidades Principais

### 🤖 **Modelo de Machine Learning**
- **Arquitetura**: Rede neural com 4 camadas densas (128→64→32→1 neurônios)
- **Técnicas**: Dropout (30%) para evitar overfitting, otimizador Adam
- **Seleção de Features**: RFE para selecionar as 10 melhores características
- **Performance**: Classificação binária com métricas de precisão, recall e F1-score

### 🔄 **Pipeline de Processamento de Dados**
- **Limpeza**: Tratamento de valores nulos, correção de erros de digitação com fuzzy matching
- **Feature Engineering**: Criação da variável `proporção_solicitado_total`
- **Normalização**: StandardScaler para variáveis numéricas
- **Codificação**: LabelEncoder para variáveis categóricas
- **Tratamento de Outliers**: Remoção baseada em intervalos estatísticos

### 🌐 **API RESTful (Flask)**
- **Endpoint**: `/predict` para predições em tempo real
- **Formato**: Recebe/retorna dados em JSON
- **Pré-processamento**: Aplicação automática das transformações de treino
- **Escalabilidade**: Pode ser containerizada e deployada em produção

### 💻 **Interface Web Interativa (Streamlit)**
- **Formulário**: Campos intuitivos para entrada de dados do cliente
- **Validação**: Controles de entrada com valores mínimos/máximos
- **Resultado**: Exibição clara de probabilidade e classificação de risco
- **UX/UI**: Interface responsiva e user-friendly

### 🔍 **Explicabilidade com LIME**
- **Interpretabilidade**: Explicações das decisões do modelo
- **Transparência**: Visualização das features mais importantes
- **Conformidade**: Atende requisitos de explicabilidade em FinTech
- **Output**: Relatórios HTML interativos
## 🛠️ Tecnologias Utilizadas

### **Backend & API**
- **Python 3.12.4**: Linguagem principal
- **Flask 3.0.3**: Framework para API RESTful
- **PostgreSQL**: Banco de dados relacional

### **Machine Learning**
- **TensorFlow 2.16.1 / Keras**: Framework para deep learning
- **Scikit-learn 1.4.1**: Pré-processamento e avaliação
- **NumPy 1.26.4**: Operações numéricas
- **Pandas 2.2.1**: Manipulação de dados

### **Frontend & Visualização**
- **Streamlit 1.32.1**: Interface web interativa
- **Matplotlib 3.8.3**: Gráficos e visualizações
- **Seaborn 0.13.2**: Visualizações estatísticas

### **Explicabilidade & Interpretabilidade**
- **LIME 0.2.0.1**: Local Interpretable Model-agnostic Explanations
- **SHAP 0.45.0**: SHapley Additive exPlanations

### **Utilitários**
- **psycopg2-binary 2.9.9**: Conexão PostgreSQL
- **PyYAML 6.0.1**: Configurações em YAML  
- **fuzzywuzzy 0.18.0**: Correção de strings
- **joblib 1.3.2**: Serialização de modelos

### **Estrutura dos Arquivos**
```
📦 analise_credito_com_appweb/
├── 📄 modelcreation.py      # Treinamento do modelo ML
├── 📄 model_mock.py         # 🆕 Modelo mock sklearn (Python 3.13 compatível)
├── 📄 api.py                # API Flask básica para predições
├── 📄 api_mock.py           # 🆕 API Flask com modelo mock funcionando
├── 📄 webapp.py             # Interface Streamlit
├── 📄 dashboard.py          # 🆕 Dashboard de métricas e monitoramento
├── 📄 xai.py                # Explicabilidade com LIME
├── 📄 utils.py              # Funções auxiliares
├── 📄 const.py              # Consulta SQL
├── 📄 config.py             # 🆕 Configurações centralizadas com variáveis de ambiente
├── 📄 config.yaml           # Configurações legadas (YAML)
├── 📄 logger.py             # 🆕 Sistema de logging avançado
├── 📄 setup.py              # 🆕 Script de automação e setup
├── 📄 testflask.py          # Testes básicos da API
├── 📄 requirements.txt      # ⬆️ Dependências atualizadas
├── 📄 modelcreation.ipynb   # Notebook de desenvolvimento
├── 📄 Dockerfile            # 🆕 Containerização otimizada
├── 📄 docker-compose.yml    # 🆕 Orquestração de containers atualizada
├── 📄 docker-manager.py     # 🆕 Gerenciador Docker automatizado
├── 📄 docker-init.py        # 🆕 Script de inicialização para containers
├── 📄 .dockerignore         # 🆕 Otimização de build Docker
├── 📄 .env.example          # 🆕 Exemplo de variáveis de ambiente
├── 📁 objects/              # Modelos e transformadores salvos
│   ├── 🤖 modelo_mock.joblib # Modelo sklearn treinado
│   ├── 📊 scaler*.joblib    # Normalizadores (7 arquivos)
│   ├── 🏷️ labelencoder*.joblib # Codificadores (6 arquivos)
│   └── 🎯 selector.joblib   # Seletor de features
├── 📁 logs/                 # 🆕 Logs do sistema
│   ├── 📋 app.log           # Log geral da aplicação
│   ├── 📊 predictions.log   # Log de predições
│   └── ⚡ performance.log   # Log de performance
└── 📁 tests/                # 🆕 Testes automatizados
    ├── 🧪 test_utils.py     # Testes das funções utilitárias
    ├── 🔌 test_api.py       # Testes da API
    └── 📊 test_prediction.py # Testes de predição integrada
```
├── 📁 logs/                 # 🆕 Logs do sistema
│   ├── 📋 app.log           # Log geral da aplicação
│   ├── 📊 predictions.log   # Log de predições
│   └── ⚡ performance.log   # Log de performance
└── 📁 tests/                # 🆕 Testes automatizados
    ├── 🧪 test_utils.py     # Testes das funções utilitárias
    └── 🔌 test_api.py       # Testes da API
```

## 🚀 Como Executar o Projeto

### **📋 Pré-requisitos**
- Python 3.12.4 ou superior
- PostgreSQL (opcional - configurado conforme `.env`)
- 8GB RAM recomendado para treinamento
- Docker (opcional - para containerização)

### **⚡ Setup Automático (Recomendado)**

1. **Clone e configure automaticamente:**
   ```powershell
   git clone https://github.com/TonFLY/analise_credito_com_appweb.git
   cd analise_credito_com_appweb
   
   # Crie o ambiente virtual
   python -m venv venv
   venv\Scripts\Activate.ps1
   
   # Instale dependências
   pip install -r requirements.txt
   
   # Execute setup completo automático
   python setup.py complete
   ```

2. **Acesse as aplicações:**
   - � **App Principal**: `http://localhost:8501`
   - 📊 **Dashboard**: `http://localhost:8502` 
   - � **API**: `http://localhost:5000`

### **🔧 Setup Manual (Avançado)**

#### **Passo 1: Configuração do Ambiente**
```powershell
# Clone e setup básico
git clone https://github.com/TonFLY/analise_credito_com_appweb.git
cd analise_credito_com_appweb
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure variáveis de ambiente
copy .env.example .env
# Edite .env com suas configurações
```

#### **Passo 2: Treinar o Modelo**
```powershell
python modelcreation.py
# ou usando o setup
python setup.py train
```

#### **Passo 3: Executar Serviços**

**API melhorada:**
```powershell
python api_improved.py
```

**Interface Principal:**
```powershell
streamlit run webapp.py
```

**Dashboard de Métricas:**
```powershell
streamlit run dashboard.py --server.port 8502
```

### **� Execução com Docker**

```powershell
# Build e execução completa
docker-compose up --build

# Apenas a API
docker-compose up api

# Parar todos os serviços
docker-compose down
```

### **🧪 Executando Testes**

```powershell
# Testes automatizados
python setup.py test

# ou manualmente
python -m pytest tests/ -v

# ou usando unittest
python -m unittest discover tests/ -v
```
## 🎥 Demonstração

![USO DO APLICATIVO](https://github.com/TonFLY/images/blob/main/gif.gif?raw=true)

## 📊 Modelo de Machine Learning

### **Arquitetura da Rede Neural**
```
Input Layer (10 features) 
    ↓
Dense Layer (128 neurons) + ReLU + Dropout(30%)
    ↓  
Dense Layer (64 neurons) + ReLU + Dropout(30%)
    ↓
Dense Layer (32 neurons) + ReLU + Dropout(30%)
    ↓
Output Layer (1 neuron) + Sigmoid
```

### **Características Técnicas**
- 🎯 **Objetivo**: Classificação binária (Bom/Ruim pagador)
- 🔄 **Otimizador**: Adam (learning_rate=0.001)
- 📉 **Loss Function**: Binary Crossentropy
- 🏃 **Épocas**: 500 com validação 30%/70%
- 📊 **Seleção**: RFE para top 10 features
- 🎲 **Seed**: 42 (reprodutibilidade)

### **Pipeline de Dados**
1. **Extração**: Query SQL complexa juntando 4 tabelas
2. **Limpeza**: Tratamento de nulos e correção fuzzy
3. **Feature Engineering**: Proporção solicitado/total
4. **Normalização**: StandardScaler para numéricas
5. **Codificação**: LabelEncoder para categóricas
6. **Seleção**: RFE para otimização de features

## 🔮 Próximos Passos e Melhorias

### **🚀 Desenvolvimentos Futuros**
- **Hyperparameter Tuning**: Grid Search e Bayesian Optimization
- **Model Ensemble**: Combinação Random Forest + Neural Network
- **Monitoramento MLOps**: Drift detection e retraining automático
- **A/B Testing**: Framework para testar novos modelos

### **🏗️ Infraestrutura**
- **Containerização**: Docker para deployment
- **CI/CD Pipeline**: GitHub Actions para automação
- **Logging & Monitoring**: Prometheus + Grafana
- **Load Balancer**: Nginx para alta disponibilidade

### **📈 Features Avançadas**
- **Dashboard Executivo**: Métricas de negócio em tempo real
- **Integração Externa**: Bureau de crédito e Open Banking
- **Modelo Temporal**: Análise de série temporal para sazonalidade
- **Explicabilidade Avançada**: SHAP values e feature importance

### **🔒 Compliance & Segurança**
- **LGPD/GDPR**: Anonimização e direito ao esquecimento
- **Auditoria**: Log de todas as decisões
- **Bias Detection**: Fairness em decisões de crédito
- **Security**: Autenticação OAuth2 e criptografia

---

## 👨‍💻 Sobre o Projeto

Este projeto representa uma implementação completa de um sistema de análise de crédito utilizando as melhores práticas de Machine Learning e Engenharia de Software. Foi desenvolvido com foco em:

- ✅ **Qualidade de Código**: Documentação, testes e estrutura modular
- ✅ **Escalabilidade**: Arquitetura preparada para produção  
- ✅ **Explicabilidade**: Transparência nas decisões algorítmicas
- ✅ **Experiência do Usuário**: Interface intuitiva e responsiva

**Contribuições são bem-vindas!** 🤝

---

*Desenvolvido por **TonFLY** | [GitHub](https://github.com/TonFLY) | 2025*

