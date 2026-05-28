from flask import Flask, request, render_template_string, Response
import pickle
import numpy as np
import pandas as pd
import io

# Criar app
app = Flask(__name__)

# Carregamento do Modelo
with open('./best_rf_model.pkl', 'rb') as f:
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

# Estilos CSS atualizados com limites de tamanho, rolagem interna e fixação de colunas
ESTILOS_CSS = """
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:#f4f7f6; margin: 0; padding: 20px; color: #333; }
    .box { background:white; padding:30px; margin:30px auto; max-width:600px; border-radius:10px; box-shadow: 0px 4px 15px rgba(0,0,0,0.05); text-align:center; }
    input[type="file"] { margin: 20px 0; padding: 15px; background: #fafafa; border: 2px dashed #bbb; width: 80%; border-radius: 5px; }
    
    /* Botões */
    .btn { padding:12px 25px; background:#28a745; color:white; border:none; border-radius:5px; font-size: 1em; cursor:pointer; font-weight: bold; text-decoration: none; display: inline-block; margin-right: 10px; }
    .btn:hover { background:#218838; }
    .btn-voltar { background: #6c757d; }
    .btn-voltar:hover { background: #5a6268; }
    .btn-exportar { background: #007bff; }
    .btn-exportar:hover { background: #0069d9; }
    
    .actions-container { margin-bottom: 20px; display: flex; align-items: center; }
    .info { font-size: 0.9em; color: #666; text-align: left; margin: 15px 20px; padding: 10px; background: #e9ecef; border-left: 4px solid #007bff; }
    
    /* Limita o tamanho e adiciona barras internas de rolagem */
    .table-container { 
        background: white; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05); 
        margin-top: 10px; 
        max-height: 600px;    
        overflow-y: auto;     
        overflow-x: auto;     
    }
    
    table { width: 100%; border-collapse: collapse; font-size: 0.9em; text-align: left; }
    
    /* Fixa o cabeçalho no topo enquanto rola verticalmente */
    th { 
        background-color: #007bff; 
        color: white; 
        padding: 12px; 
        font-weight: 600; 
        position: sticky; 
        top: 0; 
        z-index: 10;
    }
    
    td { padding: 10px; border-bottom: 1px solid #dee2e6; white-space: nowrap; }
    tr:hover { background-color: #f1f3f5; }
    
    /* MODIFICAÇÃO CSS: Fixa a coluna ID_PACIENTE à esquerda */
    td:first-child { font-weight: bold; color: #007bff; position: sticky; left: 0; background: #fdfdfd; box-shadow: 2px 0 5px rgba(0,0,0,0.05); }
    th:first-child { position: sticky; left: 0; background: #0056b3; z-index: 12; }
    
    /* Fixa a coluna de classificação à direita */
    td:last-child { font-weight: bold; position: sticky; right: 0; background: white; box-shadow: -2px 0 5px rgba(0,0,0,0.05); }
    th:last-child { position: sticky; right: 0; background: #0056b3; z-index: 11; }
    
    .badge-alto { color: #dc3545; background: #f8d7da; padding: 4px 8px; border-radius: 4px; }
    .badge-baixo { color: #28a745; background: #d4edda; padding: 4px 8px; border-radius: 4px; }
</style>
"""

# HTML da Página Inicial
HTML_HOME = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Predição de Risco - COVID-19</title>
    {ESTILOS_CSS}
</head>
<body>
<div class="box">
    <h2>Análise de Risco de Óbito - COVID-19</h2>
    <p>Insira a tabela de pacientes (CSV ou Excel) para visualizar os resultados na tela.</p>
    
    <div class="info">
        <strong>Requisito:</strong> O arquivo deve conter as 31 colunas necessárias para o modelo (de FEBRE até UTI).
    </div>

    <form action="/predict" method="POST" enctype="multipart/form-data">
        <input type="file" name="arquivo" accept=".csv, .xlsx, .xls" required>
        <br><br>
        <button type="submit" class="btn">Visualizar Classificação</button>
    </form>
</div>
</body>
</html>
"""

# HTML da Página de Resultados
HTML_RESULTADO = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Resultados da Predição</title>
    {ESTILOS_CSS}
</head>
<body>
    <div style="max-width: 98%; margin: 0 auto;">
        
        <div class="actions-container">
            <a href="/" class="btn btn-voltar">← Analisar outro arquivo</a>
            <a href="/export" class="btn btn-exportar">📥 Exportar para Excel (.xlsx)</a>
        </div>
        
        <h2>Resultados da Classificação em Lote</h2>
        <p>As colunas ID_PACIENTE (esquerda) e CLASSIFICACAO_RISCO (direita) encontram-se fixadas na visualização.</p>
        
        <div class="table-container">
            {{{{ tabela_html | safe }}}}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_HOME)

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

        # Salva o DataFrame final estruturado na memória do servidor
        ULTIMO_RESULTADO["df"] = df_resultado

        # Cria a versão com formatação visual para exibição no HTML
        df_visual = df_resultado.copy()
        df_visual['CLASSIFICACAO_RISCO'] = [
            '<span class="badge-alto">Alto Risco</span>' if pred == "Alto Risco" 
            else '<span class="badge-baixo">Baixo Risco</span>' for pred in df_visual['CLASSIFICACAO_RISCO']
        ]

        tabela_html = df_visual.to_html(index=False, escape=False)
        return render_template_string(HTML_RESULTADO, tabela_html=tabela_html)

    except Exception as e:
        return f"Erro no processamento interno: {str(e)}", 500

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