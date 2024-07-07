from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import pandas as pd
import joblib
from utils import *

app = Flask(__name__)

model = load_model('meu_modelo.keras')
selector_carregado = joblib.load('./objects/selector.joblib')

@app.route('/predict', methods=['POST'])
def predict():
    input_data = request.get_json()

    df = pd.DataFrame(input_data)

    df = load_scalers(df, ['tempoprofissao', 'renda', 'idade', 'dependentes', 
                           'valorsolicitado', 'valortotalbem', 'proporcaosolicitadototal'])
    df = load_encoders(df, ['profissao', 'tiporesidencia', 'escolaridade', 'score', 
                            'estadocivil', 'produto'])
    df = selector_carregado.transform(df)

    predictions = model.predict(df)

    return jsonify(predictions.tolist())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



    

