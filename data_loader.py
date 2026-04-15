import pandas as pd
import unicodedata
import re

mapa_perfis = {
    "pablo marcal": "Pablo Marçal",
    "pablomarcal": "Pablo Marçal",
    "pablomarcal1": "Pablo Marçal",
    "pablo marcal oficial": "Pablo Marçal",

    "tabata amaral": "Tabata Amaral",
    "tabataamaralsp": "Tabata Amaral",
    "tabata amaral 40": "Tabata Amaral",

    "guilherme boulos": "Guilherme Boulos",
    "guilhermeboulos": "Guilherme Boulos",
    "guilherme boulos 50": "Guilherme Boulos",

    "ricardo nunes": "Ricardo Nunes",
    "prefeitoricardonunes": "Ricardo Nunes",
    "ricardonunessp": "Ricardo Nunes",
    "ricardo nunes 15": "Ricardo Nunes",

    "datena": "Datena",
    "datenaoficial": "Datena",
    "oficialdatena": "Datena",
    "canal do datena": "Datena",
    "jose luiz datena 45": "Datena",

    "marina helena": "Marina Helena",
    "marinahelenabr": "Marina Helena",
    "marina helena 30": "Marina Helena"

}

def normalizar_nome(nome):
    if pd.isna(nome):
        return ""

    # remover acentos
    nome = unicodedata.normalize('NFKD', nome)
    nome = nome.encode('ascii', 'ignore').decode('utf-8')

    # lowercase
    nome = nome.lower()

    # remover caracteres especiais
    nome = re.sub(r'[^a-z0-9\s]', '', nome)

    # remover espaços extras
    nome = re.sub(r'\s+', ' ', nome).strip()

    return nome

def carregar_dados_gerais():

    # =========================
    # 📂 Vereadores
    # =========================
    seg_vereadores = pd.read_csv("data/vereadores/seguidores_spublica.csv", sep=";")
    int_vereadores = pd.read_csv("data/vereadores/interacoes_spublica.csv", sep=";")

    seg_vereadores["Cargo"] = "Vereador"
    int_vereadores["Cargo"] = "Vereador"

    # =========================
    # 📂 Prefeitos
    # =========================
    seg_prefeitos = pd.read_csv("data/prefeitos/seguidores_sp.csv", sep=";")
    int_prefeitos = pd.read_csv("data/prefeitos/interacoes_sp.csv", sep=";")

    seg_prefeitos["Cargo"] = "Prefeito"
    int_prefeitos["Cargo"] = "Prefeito"

    # =========================
    # 🔗 Concatenar
    # =========================
    seguidores = pd.concat([seg_vereadores, seg_prefeitos])
    interacoes = pd.concat([int_vereadores, int_prefeitos])

    seguidores = seguidores.rename(columns={"Fans": "Seguidores"})
    interacoes = interacoes.rename(columns={
        "Number of Reactions, Comments & Shares": "Interacoes"
    })

    df = pd.merge(
        seguidores,
        interacoes,
        on=["Profile", "Social network", "Profile-ID", "Link", "Cargo"],
        how="outer"
    )

    # =========================
    # 🧠 Feature Engineering
    # =========================
    df["Seguidores"] = df["Seguidores"].fillna(0)
    df["Interacoes"] = df["Interacoes"].fillna(0)

    df["Engajamento"] = df.apply(
        lambda row: row["Interacoes"] / row["Seguidores"]
        if row["Seguidores"] > 0 else 0,
        axis=1
    )

    df["Profile_normalizado"] = df["Profile"].apply(normalizar_nome)
    # print(df["Profile_normalizado"].head(70))
    df["Profile_padronizado"] = df["Profile_normalizado"].map(mapa_perfis)

    # fallback: se não estiver no mapa, mantém original
    df["Profile_padronizado"] = df["Profile_padronizado"].fillna(df["Profile"])

    return df

def carregar_posts():
    posts = pd.read_csv("data/prefeitos/ranking_posts_sp.csv", sep=";")

    posts = posts.rename(columns={
        "Number of Reactions, Comments & Shares": "Interacoes",
        "Post interaction rate": "Taxa_Interacao"
    })

    posts["Message"] = posts["Message"].astype(str)

    posts["Profile_normalizado"] = posts["Profile"].apply(normalizar_nome)
    # print(posts["Profile_normalizado"].head(70))
    posts["Profile_padronizado"] = posts["Profile_normalizado"].map(mapa_perfis)

    # fallback: se não estiver no mapa, mantém original
    posts["Profile_padronizado"] = posts["Profile_padronizado"].fillna(posts["Profile"])

    return posts