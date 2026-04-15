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
def layout(redes):

    return html.Div([

        html.H1("📊 Dashboard de Redes Sociais", style={"marginBottom": "20px"}),

        # 🎛️ Filtros
        html.Div([
            html.H3("Filtros"),

            html.Label("Cargo"),
            dcc.Dropdown(
                options=[
                    {"label": "Vereadores", "value": "Vereador"},
                    {"label": "Prefeitos", "value": "Prefeito"},
                    {"label": "Todos", "value": "Todos"}
                ],
                value="Todos",
                id="filtro_cargo"
            ),

            html.Label("Rede Social"),
            dcc.Dropdown(
                options=[{"label": r, "value": r} for r in redes],
                value=redes[0],
                id="filtro_rede"
            ),

            html.Label("Buscar Profile"),
            dcc.Input(id="filtro_nome", style={"width": "100%"}),

            html.Label("Top N"),
            dcc.Slider(min=5, max=30, step=5, value=10, id="top_n")

        ], style=FILTER_STYLE),

        # =========================
        # 📊 LINHA 1
        # =========================
        html.Div([
            html.Div(dcc.Graph(id="grafico_seguidores"), style=CARD_STYLE | COL_STYLE),
            html.Div(dcc.Graph(id="grafico_interacoes"), style=CARD_STYLE | COL_STYLE),
        ], style=ROW_STYLE),

        # =========================
        # 📊 LINHA 2
        # =========================
        html.Div([
            html.Div(dcc.Graph(id="grafico_engajamento"), style=CARD_STYLE | COL_STYLE),
            html.Div(dcc.Graph(id="grafico_scatter"), style=CARD_STYLE | COL_STYLE),
        ], style=ROW_STYLE),

        # =========================
        # 📊 LINHA 3
        # =========================
        html.Div([
            html.Div(dcc.Graph(id="grafico_heatmap"), style=CARD_STYLE | COL_STYLE),
            html.Div(dcc.Graph(id="grafico_comparativo"), style=CARD_STYLE | COL_STYLE),
        ], style=ROW_STYLE),

        # =========================
        # 📊 LINHA 4
        # =========================
        html.Div([
            html.Div(dcc.Graph(id="grafico_cargo"), style=CARD_STYLE),
        ])

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
        Output("grafico_seguidores", "figure"),
        Output("grafico_interacoes", "figure"),
        Output("grafico_engajamento", "figure"),
        Output("grafico_scatter", "figure"),
        Output("grafico_heatmap", "figure"),
        Output("grafico_comparativo", "figure"),
        Output("grafico_cargo", "figure"),
        Input("filtro_cargo", "value"),
        Input("filtro_rede", "value"),
        Input("filtro_nome", "value"),
        Input("top_n", "value")
    )
    def atualizar(cargo, rede, nome, top_n):

        df_filtrado = df.copy()

        if cargo != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Cargo"] == cargo]

        df_filtrado = df_filtrado[df_filtrado["Social network"] == rede]

        if nome:
            df_filtrado = df_filtrado[
                df_filtrado["Profile_padronizado"].str.contains(nome, case=False, na=False)
            ]

        df_top = df_filtrado.sort_values("Seguidores", ascending=False).head(top_n)

        # =========================
        # 📊 GRÁFICOS
        # =========================
        def estilizar(fig):
            fig.update_layout(
                template="plotly_white",
                title_x=0.5,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            return fig

        fig_seguidores = estilizar(px.bar(
            df_top, x="Profile_padronizado", y="Seguidores",
            title=f"Top {top_n} Seguidores - {rede}"
        ))

        fig_interacoes = estilizar(px.bar(
            df_top, x="Profile_padronizado", y="Interacoes",
            title=f"Top {top_n} Interações - {rede}"
        ))

        fig_engajamento = estilizar(px.bar(
            df_top.sort_values("Engajamento", ascending=False),
            x="Profile_padronizado", y="Engajamento",
            title="Taxa de Engajamento"
        ))

        fig_scatter = estilizar(px.scatter(
            df_filtrado,
            x="Seguidores",
            y="Interacoes",
            size=df_filtrado["Engajamento"] + 0.0001,
            color="Engajamento",
            hover_data=["Profile_padronizado"],
            title="Seguidores vs Interações",
            log_x=True,
            log_y=True
        ))

        fig_heatmap = estilizar(px.density_heatmap(
            df_filtrado,
            x="Seguidores",
            y="Interacoes",
            title="Densidade de Perfis"
        ))

        df_agg = df.groupby("Social network").agg({
            "Seguidores": "sum",
            "Interacoes": "sum"
        }).reset_index()

        fig_comparativo = estilizar(px.bar(
            df_agg,
            x="Social network",
            y=["Seguidores", "Interacoes"],
            barmode="group",
            title="Comparação entre Redes"
        ))

        df_cargo = df.groupby("Cargo").agg({
            "Seguidores": "sum",
            "Interacoes": "sum",
            "Engajamento": "mean"
        }).reset_index()

        fig_cargo = estilizar(px.bar(
            df_cargo,
            x="Cargo",
            y=["Seguidores", "Interacoes"],
            barmode="group",
            title="Vereadores vs Prefeitos"
        ))

        return (
            fig_seguidores,
            fig_interacoes,
            fig_engajamento,
            fig_scatter,
            fig_heatmap,
            fig_comparativo,
            fig_cargo
        )