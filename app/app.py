from flask import Flask, request, render_template, Response, redirect
import pickle
import numpy as np
import pandas as pd
import io, os
from dashboard import (
    gerar_metricas,
    grafico_classificacao,
    grafico_comorbidades,
    grafico_sintomas
)

# Diretórios
MODEL = "best_rf_model.pkl"  # Substitua pelo nome do seu modelo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "templates"),
    static_folder=os.path.join(BASE_DIR, "..", "static")
)
MODEL_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'models', MODEL))

# Carregamento do Modelo
with open(MODEL_PATH, 'rb') as f:
    modelo = pickle.load(f)

scaler = None  # Ative seu scaler aqui se necessário

# Variável global para armazenar temporariamente o último DataFrame gerado
ULTIMO_RESULTADO = {"df": None}

# Lista exata das 31 features
FEATURES_TREINAMENTO = [
    'FEBRE', 'TOSSE', 'GARGANTA', 'DISPNEIA', 'DESC_RESP', 'SATURACAO', 
    'DIARREIA', 'VOMITO', 'DOR_ABD', 'FADIGA', 'PERD_OLFT', 'PERD_PALA', 
    'OUTRO_SIN', 'NU_IDADE_N', 'PUERPERA', 'CARDIOPATI', 'HEMATOLOGI', 
    'SIND_DOWN', 'HEPATICA', 'ASMA', 'DIABETES', 'NEUROLOGIC', 'PNEUMOPATI', 
    'IMUNODEPRE', 'RENAL', 'OBESIDADE', 'OUT_MORBI', 'VACINA_COV', 
    'TRAT_COV', 'HOSPITAL', 'UTI'
]


@app.route("/")
def home():
    return render_template("home.html")

@app.route('/predict', methods=['POST'])
def predict():
    if 'arquivo' not in request.files:
        return "Nenhum arquivo enviado", 400
    
    file = request.files['arquivo']
    if file.filename == '':
        return "Nenhum arquivo selecionado", 400

    try:
        if file.filename.endswith('.csv'):
            df_original = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df_original = pd.read_excel(file)
        else:
            return "Formato inválido. Use CSV ou Excel.", 400
    except Exception as e:
        return f"Erro ao ler arquivo: {str(e)}", 400

    colunas_faltantes = [col for col in FEATURES_TREINAMENTO if col not in df_original.columns]
    if colunas_faltantes:
        return f"Erro! Colunas ausentes: {', '.join(colunas_faltantes)}", 400

    try:
        df_features = df_original[FEATURES_TREINAMENTO].copy().fillna(0)
        dados_para_predicao = scaler.transform(df_features) if scaler is not None else df_features.values
        predicoes = modelo.predict(dados_para_predicao)

        # Criando o DataFrame final que será exportado para o Excel
        df_resultado = pd.DataFrame()
        
        # Inserindo a coluna de identificação sequencial na posição inicial
        df_resultado['ID_PACIENTE'] = np.arange(1, len(df_original) + 1)
        
        # Copia todas as colunas que vieram no arquivo enviado pelo usuário
        for col in df_original.columns:
            df_resultado[col] = df_original[col]
            
        # Adiciona a coluna de predição textual no final
        df_resultado['CLASSIFICACAO_RISCO'] = [
            "Alto Risco" if pred == 1 else "Baixo Risco" for pred in predicoes
        ]

        ULTIMO_RESULTADO["df"] = df_resultado

        metricas = gerar_metricas(df_resultado)

        grafico = grafico_classificacao(df_resultado)

        grafico_comorb = grafico_comorbidades(df_resultado)

        grafico_sint = grafico_sintomas(df_resultado)

        return render_template(
            "dashboard.html",
            metricas=metricas,
            grafico=grafico,
            grafico_comorb=grafico_comorb,
            grafico_sint=grafico_sint
        )

    except Exception as e:
        return f"Erro no processamento interno: {str(e)}", 500


@app.route("/resultado")
def resultado():

    df = ULTIMO_RESULTADO["df"]

    if df is None:
        return redirect("/")

    df_visual = df.copy()

    df_visual["CLASSIFICACAO_RISCO"] = [
        '<span class="badge-alto">Alto Risco</span>'
        if x == "Alto Risco"
        else '<span class="badge-baixo">Baixo Risco</span>'
        for x in df_visual["CLASSIFICACAO_RISCO"]
    ]

    tabela_html = df_visual.to_html(
        index=False,
        escape=False,
        classes="table"
    )

    return render_template(
        "resultado.html",
        tabela_html=tabela_html
    )

@app.route('/export')
def export():
    df_resultado = ULTIMO_RESULTADO.get("df")
    
    if df_resultado is None:
        return "Nenhum dado disponível para exportação. Faça o upload novamente.", 400
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_resultado.to_excel(writer, index=False)
    output.seek(0)
    
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=resultado_covid19.xlsx"}
    )

if __name__ == '__main__':
    app.run(debug=True)