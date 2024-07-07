from fuzzywuzzy import process
import pandas as pd
from sklearn.preprocessing import StandardScaler,LabelEncoder
import joblib
import yaml
import psycopg2
import const

def fetch_data_from_db(sql_query):
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)

        con = psycopg2.connect(
            dbname=config['database_config']['dbname'], 
            user=config['database_config']['user'], 
            password=config['database_config']['password'], 
            host=config['database_config']['host']
        )

        cursor = con.cursor()
        cursor.execute(sql_query)

        df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()

    return df

def substitui_nulos(df):
    for coluna in df.columns:
        if df[coluna].dtype == 'object':
            moda = df[coluna].mode()[0]
            df[coluna].fillna(moda, inplace=True)
        else:
            mediana = df[coluna].median()
            df[coluna].fillna(mediana, inplace=True)

def corrigir_erros_digitacao(df, coluna, lista_valida):
    for i, valor in enumerate(df[coluna]):
        valor_str = str(valor) if pd.notnull(valor) else valor

        if valor_str not in lista_valida and pd.notnull(valor_str):
            correcao = process.extractOne(valor_str, lista_valida)[0]
            df.at[i, coluna] = correcao

def tratar_outliers(df, coluna, minimo, maximo):
    mediana = df[(df[coluna] >= minimo) & (df[coluna] <= maximo)][coluna].median()
    df[coluna] = df[coluna].apply(lambda x: mediana if x < minimo or x > maximo else x)
    return df

def save_scalers(df, nome_colunas):
    for nome_coluna in nome_colunas:
        scaler = StandardScaler()
        df[nome_coluna] = scaler.fit_transform(df[[nome_coluna]])
        joblib.dump(scaler, f"./objects/scaler{nome_coluna}.joblib")

    return df

def save_encoders(df, nome_colunas):
    for nome_coluna in nome_colunas:
        label_encoder = LabelEncoder()
        df[nome_coluna] = label_encoder.fit_transform(df[nome_coluna])
        joblib.dump(label_encoder, f"./objects/labelencoder{nome_coluna}.joblib")

    return df

def load_scalers(df, nome_colunas):
    for nome_coluna in nome_colunas:
        nome_arquivo_scaler = f"./objects/scaler{nome_coluna}.joblib"
        scaler = joblib.load(nome_arquivo_scaler)
        df[nome_coluna] = scaler.transform(df[[nome_coluna]])
    return df

def load_encoders(df, nome_colunas):
    for nome_coluna in nome_colunas:
        nome_arquivo_encoder = f"./objects/labelencoder{nome_coluna}.joblib"
        label_encoder = joblib.load(nome_arquivo_encoder)
        df[nome_coluna] = label_encoder.transform(df[nome_coluna])
    return df            
                                                                    

