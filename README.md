# Análise de Crédito com App Web

Um projeto pessoal de estudo para explorar a criação de uma aplicação web completa para análise de crédito, utilizando um modelo de aprendizado de máquina (rede neural) e a biblioteca Streamlit para a interface.

## Descrição do Projeto

Este projeto é um exercício prático desenvolvido para aprimorar minhas habilidades em aprendizado de máquina, desenvolvimento web e ciência de dados. Ele simula o processo de análise de crédito em um ambiente controlado, utilizando um conjunto de dados fictício. O objetivo principal é aplicar conceitos teóricos em um projeto prático e explorar as tecnologias envolvidas na construção de uma aplicação web interativa para análise de dados
## Funcionalidades Principais

* **Modelo de Predição de Risco de Crédito::** Implementação de um modelo de rede neural para prever a probabilidade de inadimplência de um cliente com base em seus dados financeiros e pessoais.
* **Interface Web Interativa (Streamlit):** Criação de uma interface web intuitiva utilizando o Streamlit para permitir a fácil inserção de dados do cliente e a visualização dos resultados da análise de forma clara e organizada.
* **Explicabilidade com LIME:** Utilização da técnica LIME para fornecer explicações claras sobre as decisões do modelo, tornando-o mais transparente e compreensível.
* **Pré-processamento:** Implementação de etapas de pré-processamento como tratamento de valores ausentes, correção de erros de digitação, tratamento de outliers, normalização e codificação de variáveis categóricas.
* **Integração com Banco de Dados (PostgreSQL):** Os dados são armazenados em um banco de dados PostgreSQL, permitindo o acesso seguro, consultas eficientes e análises futuras.
* **API REST (Flask)::**  Implantação do modelo de aprendizado de máquina como uma API RESTful utilizando o Flask, permitindo que a interface web interaja com o modelo de forma eficiente.
## Tecnologias Utilizadas

* **Linguagem:** Python
* **Framework Web:** Streamlit
* **Framework de API:** Flask
* **Banco de Dados:** PostgreSQL
* **Bibliotecas:**
    * **Aprendizado de Máquina:** TensorFlow, Keras
    * **Pré-processamento:** Pandas, Scikit-learn
    * **Explicabilidade:** LIME
    * **Conexão com Banco de Dados:** psycopg2
    * **Outros:** NumPy, YAML, fuzzywuzzy

## Como Executar o Projeto

**Requisitos:**

* Python 3.12.4
* Bibliotecas listadas no arquivo `requirements.txt`

**Passos:**

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/TonFLY/analise_credito_com_appweb.git](https://github.com/TonFLY/analise_credito_com_appweb.git)

   
2. **Crie um ambiente virtual (venv):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   
3. **Instale as Dependências:**
   ```bash
   pip install -r requirements.txt
4. **Configure o Banco de Dados (PostgreSQL):**
   * `config.yaml` ja contem a configuração não é uma boa pratica deixar disponivel porém por um banco de dados ficticio e didatico estará disponivel
5. **Execute o modelo de machine learning**
   ```bash
   python modelcreation.py
6. **Execute a API**
   ```bash
   python api.py
7. **Exercute a aplicação:**
   ```bash
   python -m streamlit run webapp.py
8. **Acesse a interface Web:**
   * Abra o navegador e acesse o endereço indicado no terminal (geralmente `http://localhost:8501` pode variar entre 8501 a 8505).
## Demonstração

![USO DO APLICATIVO](https://github.com/TonFLY/images/blob/main/gif.gif?raw=true)

## Próximos Passos

* **Otimização do Modelo:** Explorar técnicas de ajuste de hiperparâmetros e seleção de modelos para melhorar ainda mais a performance.
* **Monitoramento do Modelo:** Implementar mecanismos para monitorar o desempenho do modelo em produção e detectar desvios.
* **Interface de Relatórios:** Desenvolver uma interface para gerar relatórios mais completos e personalizados sobre os resultados da análise.
* **Integração com Outras Fontes de Dados:** Incorporar dados de birôs de crédito ou outras fontes externas para enriquecer a análise.
* **Contêinerização (Docker):** Empacotar a aplicação em um contêiner Docker para facilitar a implantação em diferentes ambientes.

