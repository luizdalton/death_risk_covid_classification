import plotly.express as px
import pandas as pd


####################################################
# MÉTRICAS
####################################################

def gerar_metricas(df):

    total = len(df)

    alto = (df["CLASSIFICACAO_RISCO"] == "Alto Risco").sum()

    baixo = (df["CLASSIFICACAO_RISCO"] == "Baixo Risco").sum()

    if total > 0:

        perc_alto = round((alto / total) * 100, 1)

        perc_baixo = round((baixo / total) * 100, 1)

    else:

        perc_alto = 0

        perc_baixo = 0

    idade_media = round(df["NU_IDADE_N"].mean(), 1)

    idade_max = int(df["NU_IDADE_N"].max())

    idade_min = int(df["NU_IDADE_N"].min())

    hospital = int(df["HOSPITAL"].sum())

    uti = int(df["UTI"].sum())

    vacinados = int(df["VACINA_COV"].sum())

    return {

        "total": total,

        "alto": alto,

        "baixo": baixo,

        "perc_alto": perc_alto,

        "perc_baixo": perc_baixo,

        "idade_media": idade_media,

        "idade_max": idade_max,

        "idade_min": idade_min,

        "hospital": hospital,

        "uti": uti,

        "vacinados": vacinados

    }


####################################################
# GRÁFICO 1
####################################################

def grafico_classificacao(df):

    dados = df["CLASSIFICACAO_RISCO"] \
        .value_counts() \
        .reset_index()

    dados.columns = [

        "Classe",

        "Quantidade"

    ]

    fig = px.pie(

        dados,

        names="Classe",

        values="Quantidade",

        hole=0.55,

        color="Classe",

        color_discrete_map={

            "Alto Risco": "#dc2626",

            "Baixo Risco": "#16a34a"

        }

    )

    fig.update_traces(

        textinfo="percent+label",

        textfont_size=16,

        marker=dict(

            line=dict(

                color="white",

                width=3

            )

        )

    )

    fig.update_layout(

        title="Distribuição das Classificações",

        title_x=0.5,

        title_font_size=22,

        template="plotly_white",

        height=520,

        legend_title="",

        margin=dict(

            l=20,

            r=20,

            t=70,

            b=20

        )

    )

    return fig.to_html(full_html=False)


####################################################
# GRÁFICO 2 - COMORBIDADES
####################################################

def grafico_comorbidades(df):

    colunas = {

        "CARDIOPATI": "Cardiopatia",

        "DIABETES": "Diabetes",

        "ASMA": "Asma",

        "OBESIDADE": "Obesidade",

        "RENAL": "Doença Renal",

        "HEPATICA": "Doença Hepática",

        "PNEUMOPATI": "Pneumopatia",

        "IMUNODEPRE": "Imunodepressão"

    }

    graf = pd.DataFrame({

        "Comorbidade": list(colunas.values()),

        "Quantidade": [

            int(df[col].sum())

            for col in colunas.keys()

        ]

    })

    # Apenas as 5 mais frequentes
    graf = graf.sort_values(
        by="Quantidade",
        ascending=False
    ).head(5)

    fig = px.bar(

        graf,

        x="Quantidade",

        y="Comorbidade",

        orientation="h",

        text="Quantidade",

        color="Quantidade",

        color_continuous_scale="Blues"

    )

    fig.update_traces(

        textposition="outside"

    )

    fig.update_layout(

        template="plotly_white",

        title="Top 5 Comorbidades",

        title_x=0.5,

        title_font_size=22,

        height=470,

        coloraxis_showscale=False,

        margin=dict(

            l=30,

            r=20,

            t=70,

            b=20

        )

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    return fig.to_html(full_html=False)

####################################################
# GRÁFICO 3 - SINTOMAS
####################################################

def grafico_sintomas(df):

    sintomas = {

        "FEBRE": "Febre",

        "TOSSE": "Tosse",

        "GARGANTA": "Dor de Garganta",

        "DISPNEIA": "Dispneia",

        "SATURACAO": "Baixa Saturação",

        "DIARREIA": "Diarreia",

        "VOMITO": "Vômito",

        "FADIGA": "Fadiga"

    }

    graf = pd.DataFrame({

        "Sintoma": list(sintomas.values()),

        "Quantidade": [

            int(df[col].sum())

            for col in sintomas.keys()

        ]

    })

    # Apenas os 5 mais frequentes
    graf = graf.sort_values(
        by="Quantidade",
        ascending=False
    ).head(5)

    fig = px.bar(

        graf,

        x="Quantidade",

        y="Sintoma",

        orientation="h",

        text="Quantidade",

        color="Quantidade",

        color_continuous_scale="Reds"

    )

    fig.update_traces(

        textposition="outside"

    )

    fig.update_layout(

        template="plotly_white",

        title="Top 5 Sintomas",

        title_x=0.5,

        title_font_size=22,

        height=470,

        coloraxis_showscale=False,

        margin=dict(

            l=30,

            r=20,

            t=70,

            b=20

        )

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    return fig.to_html(full_html=False)