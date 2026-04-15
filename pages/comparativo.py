from dash import html, dcc, Input, Output
import plotly.express as px

# =========================
# 🎨 ESTILO
# =========================
CARD_STYLE = {
    "backgroundColor": "#ffffff",
    "padding": "15px",
    "borderRadius": "10px",
    "boxShadow": "0px 2px 8px rgba(0,0,0,0.1)",
}

ROW_STYLE = {
    "display": "flex",
    "gap": "20px",
    "marginBottom": "20px"
}

COL_STYLE = {
    "flex": "1"
}

FILTER_STYLE = {
    "backgroundColor": "#f8f9fa",
    "padding": "15px",
    "borderRadius": "10px",
    "marginBottom": "20px"
}


# =========================
# 📊 Layout
# =========================
def layout():
    return html.Div([

        html.H2("🔀 Comparação entre Redes Sociais", style={"marginBottom": "20px"}),

        # 🎛️ Filtro
        html.Div([
            html.Label("Cargo"),
            dcc.Dropdown(
                options=[
                    {"label": "Vereadores", "value": "Vereador"},
                    {"label": "Prefeitos", "value": "Prefeito"},
                    {"label": "Todos", "value": "Todos"}
                ],
                value="Todos",
                id="filtro_cargo_comp"
            ),
        ], style=FILTER_STYLE),

        # =========================
        # 📊 LINHA 1
        # =========================
        html.Div([
            html.Div(dcc.Graph(id="grafico_perc_seguidores"), style=CARD_STYLE | COL_STYLE),
            html.Div(dcc.Graph(id="grafico_perc_interacoes"), style=CARD_STYLE | COL_STYLE),
        ], style=ROW_STYLE),

        # =========================
        # 📊 LINHA 2
        # =========================
        html.Div([
            html.Div(dcc.Graph(id="grafico_engajamento_rede"), style=CARD_STYLE | COL_STYLE),
            html.Div(dcc.Graph(id="grafico_heatmap_rede"), style=CARD_STYLE | COL_STYLE),
        ], style=ROW_STYLE),

    ], style={
        "backgroundColor": "#f4f6f9",
        "padding": "20px",
        "fontFamily": "Arial, sans-serif"
    })


# =========================
# 🔄 Callback
# =========================
def register_callbacks(app, df):

    @app.callback(
        Output("grafico_perc_seguidores", "figure"),
        Output("grafico_perc_interacoes", "figure"),
        Output("grafico_engajamento_rede", "figure"),
        Output("grafico_heatmap_rede", "figure"),
        Input("filtro_cargo_comp", "value")
    )
    def atualizar_comparativo(cargo):

        df_comp = df.copy()

        if cargo != "Todos":
            df_comp = df_comp[df_comp["Cargo"] == cargo]

        df_cargo = df_comp.copy()

        # =========================
        # 📊 Totais por candidato
        # =========================
        df_total = df_comp.groupby("Profile_padronizado").agg({
            "Seguidores": "sum",
            "Interacoes": "sum"
        }).rename(columns={
            "Seguidores": "Seguidores_total",
            "Interacoes": "Interacoes_total"
        })

        df_comp = df_comp.merge(df_total, on="Profile_padronizado", how="left")

        # =========================
        # 📊 Percentuais
        # =========================
        df_comp["Perc_Seguidores"] = df_comp["Seguidores"] / df_comp["Seguidores_total"]
        df_comp["Perc_Interacoes"] = df_comp["Interacoes"] / df_comp["Interacoes_total"]

        df_comp = df_comp.fillna(0)

        # =========================
        # 🎨 Função de estilo
        # =========================
        def estilizar(fig):
            fig.update_layout(
                template="plotly_white",
                title_x=0.5,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_tickangle=-45
            )
            return fig

        # =========================
        # 📊 Gráficos
        # =========================
        fig_perc_seguidores = estilizar(px.bar(
            df_comp,
            x="Profile_padronizado",
            y="Perc_Seguidores",
            color="Social network",
            barmode="stack",
            title="Distribuição % de Seguidores por Rede"
        ))

        fig_perc_interacoes = estilizar(px.bar(
            df_comp,
            x="Profile_padronizado",
            y="Perc_Interacoes",
            color="Social network",
            barmode="stack",
            title="Distribuição % de Interações por Rede"
        ))

        fig_engajamento_rede = estilizar(px.bar(
            df_cargo,
            x="Profile_padronizado",
            y="Engajamento",
            color="Social network",
            barmode="group",
            title="Engajamento por Rede Social"
        ))

        fig_heatmap_rede = estilizar(px.density_heatmap(
            df_cargo,
            x="Social network",
            y="Engajamento",
            title="Distribuição de Engajamento por Rede"
        ))

        return (
            fig_perc_seguidores,
            fig_perc_interacoes,
            fig_engajamento_rede,
            fig_heatmap_rede
        )