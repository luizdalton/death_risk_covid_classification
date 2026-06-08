# Death Risk COVID Classification
Este projeto é uma aplicação Flask para classificar o risco de óbito em pacientes com COVID-19 a partir de arquivos em lote (CSV ou Excel).

<img width="715" height="456" alt="image" src="https://github.com/user-attachments/assets/b84df18c-3ad8-46a7-a893-f9a12bec5b13" />


<img width="1600" height="708" alt="image" src="https://github.com/user-attachments/assets/571c9975-cbfe-409c-9013-551b74afa6da" />

## Estrutura do Projeto

- `main.py` - Script de entrada que executa `app/app.py` usando `subprocess`.
- `app/app.py` - Aplicação Flask principal que carrega o modelo, processa uploads e retorna resultados.
- `models/best_rf_model.pkl` - Modelo treinado em formato pickle utilizado para predição.
- `requirements.txt` - Dependências Python necessárias para rodar a aplicação.
- `utils/clean_ambient.py` - Script auxiliar para identificar e remover dependências não utilizadas.

## Requisitos

- Python 3.11+ (recomendado)
- Biblioteca `Flask`
- `pandas`
- `numpy`
- `openpyxl` (usado internamente para exportar resultados em Excel)

Instale as dependências com:

```bash
pip install -r requirements.txt
```

## Como Executar

Execute o aplicativo com:

```bash
python main.py
```

A aplicação abrirá um servidor Flask local. Acesse pelo navegador em:

```text
http://127.0.0.1:5000/
```

## Como Usar

1. Na página inicial, envie um arquivo no formato CSV ou Excel (`.csv`, `.xlsx`, `.xls`).
2. O arquivo deve conter todas as 31 colunas esperadas pelo modelo:

- `FEBRE`
- `TOSSE`
- `GARGANTA`
- `DISPNEIA`
- `DESC_RESP`
- `SATURACAO`
- `DIARREIA`
- `VOMITO`
- `DOR_ABD`
- `FADIGA`
- `PERD_OLFT`
- `PERD_PALA`
- `OUTRO_SIN`
- `NU_IDADE_N`
- `PUERPERA`
- `CARDIOPATI`
- `HEMATOLOGI`
- `SIND_DOWN`
- `HEPATICA`
- `ASMA`
- `DIABETES`
- `NEUROLOGIC`
- `PNEUMOPATI`
- `IMUNODEPRE`
- `RENAL`
- `OBESIDADE`
- `OUT_MORBI`
- `VACINA_COV`
- `TRAT_COV`
- `HOSPITAL`
- `UTI`

3. Após enviar, a aplicação exibirá a tabela com a predição de risco e permitirá exportar os resultados em Excel.

## Resultado

A aplicação gera uma tabela com as colunas originais do arquivo e adiciona:

- `ID_PACIENTE` - Identificador sequencial do paciente
- `CLASSIFICACAO_RISCO` - `Alto Risco` ou `Baixo Risco`

## Exportação

Você pode exportar os resultados para um arquivo Excel clicando em "Exportar para Excel (.xlsx)" na página de resultados.

## Observações

- O modelo é carregado a partir de `models/best_rf_model.pkl`.
- Se o arquivo enviado não contiver todas as colunas necessárias, a aplicação retornará um erro indicando as colunas faltantes.
- O código atual não aplica normalização automaticamente porque `scaler` está definido como `None`. Se o modelo exigir pré-processamento, ative o scaler no `app/app.py`.

## Licença

Projeto aberto para uso e estudo.
