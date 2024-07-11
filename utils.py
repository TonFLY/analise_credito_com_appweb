# Importações de bibliotecas e módulos
import pandas as pd                 # Manipulação de dados em DataFrames
from fuzzywuzzy import process       # Biblioteca para comparação aproximada de strings
from sklearn.preprocessing import StandardScaler, LabelEncoder  # Pré-processamento de dados
import joblib                       # Serialização de objetos Python (para salvar modelos)
import yaml                         # Leitura de arquivos de configuração YAML
import psycopg2                     # Conexão com banco de dados PostgreSQL
import const                       # Módulo personalizado (provavelmente contém constantes e configurações)

# Função para buscar dados do banco de dados
def fetch_data_from_db(sql_query):
    try:
        # Lê as configurações de conexão do banco de dados a partir do arquivo config.yaml
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)

        # Estabelece a conexão com o banco de dados
        con = psycopg2.connect(
            dbname=config['database_config']['dbname'],
            user=config['database_config']['user'],
            password=config['database_config']['password'],
            host=config['database_config']['host']
        )

        cursor = con.cursor()
        cursor.execute(sql_query)  # Executa a consulta SQL

        # Cria um DataFrame a partir dos resultados da consulta
        df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

    finally:
        # Garante que a conexão e o cursor sejam fechados, mesmo em caso de erro
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()

    return df

# Função para substituir valores nulos por valores estatísticos
def substitui_nulos(df):
    for coluna in df.columns:  # Percorre todas as colunas do DataFrame
        if df[coluna].dtype == 'object':  # Se a coluna for categórica (tipo objeto)
            moda = df[coluna].mode()[0]  # Calcula a moda (valor mais frequente)
            df[coluna].fillna(moda, inplace=True)  # Substitui nulos pela moda
        else:  # Se a coluna for numérica
            mediana = df[coluna].median()  # Calcula a mediana
            df[coluna].fillna(mediana, inplace=True)  # Substitui nulos pela mediana

# Função para corrigir erros de digitação em colunas categóricas
def corrigir_erros_digitacao(df, coluna, lista_valida):
    for i, valor in enumerate(df[coluna]):  # Percorre os valores da coluna
        valor_str = str(valor) if pd.notnull(valor) else valor  # Converte para string (se não for nulo)
        if valor_str not in lista_valida and pd.notnull(valor_str):  # Se o valor não estiver na lista válida
            # Encontra o valor mais próximo na lista válida usando fuzzy matching
            correcao = process.extractOne(valor_str, lista_valida)[0]  
            df.at[i, coluna] = correcao  # Substitui o valor pela correção

# Função para tratar outliers em colunas numéricas
def tratar_outliers(df, coluna, minimo, maximo):
    # Calcula a mediana dos valores dentro do intervalo válido
    mediana = df[(df[coluna] >= minimo) & (df[coluna] <= maximo)][coluna].median()  
    # Substitui os outliers pela mediana
    df[coluna] = df[coluna].apply(lambda x: mediana if x < minimo or x > maximo else x)  
    return df

# Função para salvar os objetos StandardScaler após o ajuste
def save_scalers(df, nome_colunas):
    for nome_coluna in nome_colunas:  # Aplica escalonamento em cada coluna
        scaler = StandardScaler()
        df[nome_coluna] = scaler.fit_transform(df[[nome_coluna]])  
        joblib.dump(scaler, f"./objects/scaler{nome_coluna}.joblib")  # Salva o scaler
    return df

# Função para salvar os objetos LabelEncoder após o ajuste
def save_encoders(df, nome_colunas):
    for nome_coluna in nome_colunas:  # Aplica codificação em cada coluna
        label_encoder = LabelEncoder()
        df[nome_coluna] = label_encoder.fit_transform(df[nome_coluna])
        joblib.dump(label_encoder, f"./objects/labelencoder{nome_coluna}.joblib")  # Salva o encoder
    return df

# Função para carregar e aplicar os scalers aos dados
def load_scalers(df, nome_colunas):
    for nome_coluna in nome_colunas:
        scaler = joblib.load(f"./objects/scaler{nome_coluna}.joblib")
        df[nome_coluna] = scaler.transform(df[[nome_coluna]])
    return df

# Função para carregar e aplicar os encoders aos dados
def load_encoders(df, nome_colunas):
    for nome_coluna in nome_colunas:
        label_encoder = joblib.load(f"./objects/labelencoder{nome_coluna}.joblib")
        df[nome_coluna] = label_encoder.transform(df[nome_coluna])
    return df
