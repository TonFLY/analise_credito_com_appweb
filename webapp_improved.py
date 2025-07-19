import streamlit as st
import requests
import yaml
import json
import time
from datetime import datetime
from config import Config
import logging

# Configuração da página
st.set_page_config(
    page_title="Análise de Crédito",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-result {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-result {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .danger-result {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_api_url():
    """Obtém URL da API com fallback"""
    try:
        return Config.API_URL
    except:
        # Fallback para config.yaml
        try:
            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)
                return config['url_api']['url']
        except:
            return 'http://127.0.0.1:5000/predict'

def check_api_health():
    """Verifica se a API está funcionando"""
    try:
        api_url = get_api_url()
        health_url = api_url.replace('/predict', '/health')
        response = requests.get(health_url, timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def display_header():
    """Exibe cabeçalho da aplicação"""
    st.markdown("""
    <div class="main-header">
        <h1>🏦 Sistema de Análise de Crédito</h1>
        <p>Avaliação inteligente de risco creditício com Machine Learning</p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Configura e exibe sidebar"""
    st.sidebar.title("🔧 Configurações")
    
    # Verificação da API
    is_healthy, health_data = check_api_health()
    
    if is_healthy:
        st.sidebar.success("✅ API Online")
        if health_data:
            st.sidebar.json(health_data)
    else:
        st.sidebar.error("❌ API Offline")
        st.sidebar.warning("Certifique-se de que a API está executando")
    
    st.sidebar.markdown("---")
    
    # Links úteis
    st.sidebar.markdown("### 🔗 Links Úteis")
    st.sidebar.markdown("- [📊 Dashboard](http://localhost:8502)")
    st.sidebar.markdown("- [🔗 API Docs](http://localhost:5000)")
    st.sidebar.markdown("- [📖 GitHub](https://github.com/TonFLY/analise_credito_com_appweb)")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Versão:** 2.0.0")
    st.sidebar.markdown("**Desenvolvido por:** TonFLY")

def get_form_data():
    """Coleta dados do formulário principal"""
    # Listas de opções atualizadas
    profissoes = ['Advogado', 'Arquiteto', 'Cientista de Dados', 'Contador', 
                  'Dentista', 'Empresário', 'Engenheiro', 'Médico', 'Programador']
    tipos_residencia = ['Alugada', 'Outros', 'Própria']
    escolaridades = ['Ens.Fundamental', 'Ens.Médio', 'Pós ou Mais', 'Superior']
    scores = ['Baixo', 'Bom', 'Justo', 'Muito Bom']
    estados_civis = ['Casado', 'Divorciado', 'Solteiro', 'Viúvo']
    produtos = ['AgileXplorer', 'DoubleDuty', 'EcoPrestige', 'ElegantCruise', 
                'SpeedFury', 'TrailConqueror', 'VoyageRoamer', 'WorkMaster']

    with st.form(key='prediction_form'):
        st.subheader("📝 Dados do Cliente")
        
        # Linha 1: Dados pessoais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            profissao = st.selectbox('👔 Profissão', profissoes)
            idade = st.number_input('🎂 Idade', min_value=18, max_value=110, value=30, step=1)
        
        with col2:
            estado_civil = st.selectbox('💑 Estado Civil', estados_civis)
            dependentes = st.number_input('👨‍👩‍👧‍👦 Dependentes', min_value=0, max_value=10, value=0, step=1)
        
        with col3:
            escolaridade = st.selectbox('🎓 Escolaridade', escolaridades)
            tipo_residencia = st.selectbox('🏠 Tipo de Residência', tipos_residencia)
        
        st.markdown("---")
        
        # Linha 2: Dados financeiros
        st.subheader("💰 Dados Financeiros")
        
        col1, col2 = st.columns(2)
        
        with col1:
            renda = st.number_input('💵 Renda Mensal (R$)', min_value=0.0, value=5000.0, step=500.0, format="%.2f")
            tempo_profissao = st.number_input('⏱️ Tempo na Profissão (anos)', min_value=0, max_value=50, value=3, step=1)
        
        with col2:
            score = st.selectbox('📊 Score de Crédito', scores)
            st.markdown("*Score baseado em histórico de crédito*")
        
        st.markdown("---")
        
        # Linha 3: Dados do produto
        st.subheader("🚗 Dados do Financiamento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            produto = st.selectbox('🏷️ Produto', produtos)
            valor_solicitado = st.number_input('💳 Valor Solicitado (R$)', min_value=1000.0, value=50000.0, step=1000.0, format="%.2f")
        
        with col2:
            valor_total_bem = st.number_input('🏎️ Valor Total do Bem (R$)', min_value=1000.0, value=80000.0, step=1000.0, format="%.2f")
            
            # Cálculo automático da proporção
            if valor_total_bem > 0:
                proporcao = valor_solicitado / valor_total_bem
                st.metric("📈 Proporção Solicitado/Total", f"{proporcao:.2%}")
            
        # Botão de envio
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            submit_button = st.form_submit_button(
                label='🔍 Analisar Crédito',
                use_container_width=True
            )
    
    if submit_button:
        return {
            'profissao': [profissao],
            'tempoprofissao': [tempo_profissao],
            'renda': [renda],
            'tiporesidencia': [tipo_residencia],
            'escolaridade': [escolaridade],
            'score': [score],
            'idade': [idade],
            'dependentes': [dependentes],
            'estadocivil': [estado_civil],
            'produto': [produto],
            'valorsolicitado': [valor_solicitado],
            'valortotalbem': [valor_total_bem],
            'proporcaosolicitadototal': [valor_solicitado / valor_total_bem if valor_total_bem > 0 else 0]
        }
    
    return None

def make_prediction(data):
    """Faz predição via API"""
    try:
        url = get_api_url()
        
        with st.spinner('🤖 Analisando dados...'):
            start_time = time.time()
            response = requests.post(url, json=data, timeout=30)
            end_time = time.time()
            
        processing_time = (end_time - start_time) * 1000  # em ms
        
        if response.status_code == 200:
            predictions = response.json()
            return predictions, processing_time, None
        else:
            return None, processing_time, f"Erro HTTP {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        return None, 0, "Timeout: API não respondeu em 30 segundos"
    except requests.exceptions.ConnectionError:
        return None, 0, "Erro de conexão: Verifique se a API está executando"
    except Exception as e:
        return None, 0, f"Erro inesperado: {str(e)}"

def display_results(predictions, processing_time):
    """Exibe resultados da predição"""
    if predictions and len(predictions) > 0:
        probabilidade = predictions[0][0] * 100
        classe = "Bom Pagador" if probabilidade > 50 else "Risco Alto"
        
        # Determinar estilo baseado no resultado
        if probabilidade > 70:
            result_class = "success-result"
            emoji = "✅"
            risk_level = "BAIXO RISCO"
        elif probabilidade > 50:
            result_class = "warning-result" 
            emoji = "⚠️"
            risk_level = "RISCO MODERADO"
        else:
            result_class = "danger-result"
            emoji = "❌"
            risk_level = "ALTO RISCO"
        
        # Exibir resultado principal
        st.markdown(f"""
        <div class="{result_class}">
            <h2 style="text-align: center;">{emoji} {classe}</h2>
            <h3 style="text-align: center;">Probabilidade: {probabilidade:.2f}%</h3>
            <h4 style="text-align: center;">Classificação: {risk_level}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Métricas detalhadas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🎯 Probabilidade",
                f"{probabilidade:.1f}%",
                delta=f"{probabilidade - 50:.1f}%" if probabilidade != 50 else None
            )
        
        with col2:
            st.metric("📊 Classificação", classe)
        
        with col3:
            st.metric("⚡ Tempo de Análise", f"{processing_time:.0f}ms")
        
        with col4:
            confidence = "Alta" if abs(probabilidade - 50) > 30 else "Média" if abs(probabilidade - 50) > 15 else "Baixa"
            st.metric("🎯 Confiança", confidence)
        
        # Interpretação dos resultados
        st.markdown("---")
        st.subheader("📈 Interpretação dos Resultados")
        
        if probabilidade > 70:
            st.success("""
            **🟢 APROVAÇÃO RECOMENDADA**
            - Cliente apresenta baixo risco de inadimplência
            - Perfil compatível com aprovação de crédito
            - Recomenda-se prosseguir com a análise documental
            """)
        elif probabilidade > 50:
            st.warning("""
            **🟡 ANÁLISE ADICIONAL NECESSÁRIA**
            - Cliente apresenta risco moderado
            - Recomenda-se análise mais detalhada
            - Considere garantias adicionais ou condições especiais
            """)
        else:
            st.error("""
            **🔴 APROVAÇÃO NÃO RECOMENDADA**
            - Cliente apresenta alto risco de inadimplência
            - Perfil não compatível com aprovação automática
            - Recomenda-se recusa ou condições muito restritivas
            """)
        
        # Log da transação
        with st.expander("🔍 Detalhes Técnicos"):
            st.json({
                "timestamp": datetime.now().isoformat(),
                "probabilidade": float(probabilidade),
                "classificacao": classe,
                "tempo_processamento_ms": processing_time,
                "versao_modelo": "2.0.0"
            })

def main():
    """Função principal da aplicação"""
    display_header()
    display_sidebar()
    
    # Verificação inicial da API
    is_healthy, _ = check_api_health()
    
    if not is_healthy:
        st.error("""
        ⚠️ **API Offline**
        
        A API não está respondendo. Para usar a aplicação:
        
        1. Execute: `python api_improved.py` (ou `python api.py`)
        2. Verifique se a API está rodando em http://localhost:5000
        3. Recarregue esta página
        """)
        st.stop()
    
    # Formulário principal
    form_data = get_form_data()
    
    if form_data:
        # Validações básicas
        if form_data['valortotalbem'][0] <= 0:
            st.error("❌ Valor total do bem deve ser maior que zero")
            return
            
        if form_data['valorsolicitado'][0] > form_data['valortotalbem'][0]:
            st.warning("⚠️ Valor solicitado é maior que o valor total do bem")
        
        # Fazer predição
        predictions, processing_time, error = make_prediction(form_data)
        
        if error:
            st.error(f"❌ {error}")
        else:
            display_results(predictions, processing_time)

if __name__ == "__main__":
    main()
