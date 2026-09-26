"""Funções e caminhos compartilhados pelos scripts da auditoria.

Variáveis de ambiente opcionais:
  ELEICOES_DADOS       pasta de dados (padrão: <repo>/dados)
  ELEICOES_RESULTADOS  pasta de resultados (padrão: <repo>/resultados)
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DADOS = Path(os.environ.get("ELEICOES_DADOS", REPO / "dados"))
RESULTADOS = Path(os.environ.get("ELEICOES_RESULTADOS", REPO / "resultados"))
CACHE = DADOS / "cache"
GEO = DADOS / "geo"
for p in (RESULTADOS, CACHE, GEO):
    p.mkdir(parents=True, exist_ok=True)

# Metadados da base larga (texto); as demais colunas são contagens inteiras.
META_STR = [
    "ID_SECAO", "SG_UF", "NM_MUNICIPIO", "DS_TIPO_URNA", "NR_URNA_EFETIVADA",
    "CD_CARGA_1_URNA_EFETIVADA", "CD_CARGA_2_URNA_EFETIVADA",
    "CD_FLASHCARD_URNA_EFETIVADA", "DS_AGREGADAS", "DT_ABERTURA",
    "DT_ENCERRAMENTO", "DT_EMISSAO_BU", "CD_TIPO_URNA",
]
PRES_T1 = ["PRES_12", "PRES_13", "PRES_14", "PRES_15", "PRES_16", "PRES_21",
           "PRES_22", "PRES_27", "PRES_30", "PRES_44", "PRES_80"]
# Blocos partidários usados nos controles (números de partido de 2022).
BLOCO_ESQ = {"13", "65", "43", "50", "18", "40", "77", "70", "36", "90",
             "12", "16", "21", "29", "80"}
BLOCO_DIR = {"11", "10", "20", "14", "51", "28"}  # direita aliada, sem o PL
MARGEM_2T = 60_345_999 - 58_206_354               # margem oficial do 2º turno


def _arquivo_base(turno: int) -> Path:
    for nome in (f"secoes_2022_t{turno}.csv.gz", f"secoes_2022_t{turno}_csv.gz"):
        p = DADOS / nome
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Base larga do {turno}º turno não encontrada em {DADOS}. "
        "Gere-a com scripts/01a_gerar_base_secoes.py (ver README).")


def carregar_base(turno: int) -> pd.DataFrame:
    """Base larga por seção (uma linha por seção), com cache em pickle."""
    cache = CACHE / f"base_t{turno}.pkl"
    if cache.exists():
        return pd.read_pickle(cache)
    arq = _arquivo_base(turno)
    cab = pd.read_csv(arq, sep=";", nrows=2)
    tipos = {c: (str if c in META_STR else "Int64") for c in cab.columns}
    d = pd.read_csv(arq, sep=";", dtype=tipos)
    for c in d.columns:
        if c not in META_STR:
            d[c] = d[c].fillna(0).astype("int64")
    d.to_pickle(cache)
    return d


def carregar_modelo() -> pd.DataFrame:
    """Modelo de urna por seção (gerado por 01_modelo_urna.py)."""
    p = DADOS / "modelo_urna_secao.csv.gz"
    if not p.exists():
        raise FileNotFoundError("Rode antes scripts/01_modelo_urna.py.")
    m = pd.read_csv(p, dtype={"ID_SECAO": str, "LOG_MODELO": str})
    m["old"] = (m.LOG_FG2020 == 0).astype(int)
    m["sem_modelo"] = m.LOG_MODELO.isna() | m.LOG_MODELO.eq("-")
    return m


def base_com_modelo(turno: int) -> pd.DataFrame:
    """Base do turno + modelo de urna + chaves de estrato (sem o exterior)."""
    d = carregar_base(turno).merge(carregar_modelo(), on="ID_SECAO", how="left")
    d = d[d.SG_UF != "ZZ"].copy()
    d["mun"] = d.SG_UF + "_" + d.CD_MUNICIPIO.astype(str)
    d["mz"] = d.mun + "_" + d.NR_ZONA.astype(str)
    d["lv"] = d.mz + "_" + d.NR_LOCAL_VOTACAO.astype(str)
    return d


def salvar(df: pd.DataFrame, nome: str) -> Path:
    p = RESULTADOS / nome
    df.to_csv(p, index=False)
    return p


# --------------------------------------------------------------------------
# Cochran–Mantel–Haenszel (por voto, como no relatório original)
# --------------------------------------------------------------------------
CMH_COLS = ["A", "B", "C", "D"]  # A=antiga·Lula, B=antiga·Bolsonaro, C=UE2020·Lula, D=UE2020·Bolsonaro


def tabela_2x2(d: pd.DataFrame, lula="PRES_13", bolso="PRES_22") -> pd.DataFrame:
    old = d.old == 1
    return pd.DataFrame({
        "A": np.where(old, d[lula], 0), "B": np.where(old, d[bolso], 0),
        "C": np.where(~old, d[lula], 0), "D": np.where(~old, d[bolso], 0),
    }, index=d.index)


def cmh(tab: pd.DataFrame, chave: pd.Series) -> dict:
    """Razão de Mantel–Haenszel e estatística CMH sem correção de continuidade."""
    g = tab.groupby(chave.values)[CMH_COLS].sum()
    A, B, C, D = (g[c].to_numpy(float) for c in CMH_COLS)
    n1, n2, m1, m2 = A + B, C + D, A + C, B + D
    T = n1 + n2
    ok = (n1 > 0) & (n2 > 0)
    A, B, C, D, n1, n2, m1, m2, T = (x[ok] for x in (A, B, C, D, n1, n2, m1, m2, T))
    R = np.sum(A * D / T) / np.sum(B * C / T)
    num = np.sum(A - n1 * m1 / T)
    var = np.sum(n1 * n2 * m1 * m2 / (T ** 2 * (T - 1)))
    return {"estratos_mistos": int(ok.sum()), "R": R, "CMH": num ** 2 / var,
            "votos_estratos_mistos": T.sum()}


# --------------------------------------------------------------------------
# Regressão ponderada com efeito fixo e erro-padrão agrupado
# --------------------------------------------------------------------------
def estratos_mistos(d: pd.DataFrame, chave: str, flag: str = "old") -> pd.DataFrame:
    s = d.groupby(chave)[flag].agg(["min", "max"])
    ok = s.index[(s["min"] == 0) & (s["max"] == 1)]
    return d[d[chave].isin(ok)].copy()


def efeito_fixo(d: pd.DataFrame, y: str, X: list[str], chave: str,
                cluster: str | None = None, peso: str | None = "n") -> dict:
    """Coeficiente do primeiro regressor de X, com efeito fixo em `chave`
    e erro-padrão agrupado em `cluster` (padrão: a própria chave)."""
    cluster = cluster or chave
    d = d.dropna(subset=[y] + X)
    W = d[peso].to_numpy(float) if peso else np.ones(len(d))
    A = np.array(d[[y] + X].to_numpy(float), dtype=float, copy=True)
    _, inv = np.unique(d[chave].to_numpy(), return_inverse=True)
    sw = np.bincount(inv, weights=W)
    for j in range(A.shape[1]):
        A[:, j] -= (np.bincount(inv, weights=W * A[:, j]) / sw)[inv]
    Y, M = A[:, 0], A[:, 1:]
    XtWX = (M * W[:, None]).T @ M
    b = np.linalg.lstsq(XtWX, (M * W[:, None]).T @ Y, rcond=None)[0]
    e = Y - M @ b
    _, ci = np.unique(d[cluster].to_numpy(), return_inverse=True)
    G = ci.max() + 1
    S = np.zeros((G, M.shape[1]))
    np.add.at(S, ci, M * (W * e)[:, None])
    Ginv = np.linalg.pinv(XtWX)
    V = Ginv @ (S.T @ S) @ Ginv * G / (G - 1)
    return {"coef": b[0], "ep": float(np.sqrt(V[0, 0])), "t": b[0] / np.sqrt(V[0, 0]),
            "n": len(d), "clusters": int(G)}


def composicao_legislativa(t1: pd.DataFrame) -> pd.DataFrame:
    """Participação de cada partido (e de brancos+nulos) no voto a deputado
    federal e estadual do 1º turno, por seção."""
    out = pd.DataFrame({"ID_SECAO": t1.ID_SECAO})
    for cargo in ("DF", "DE"):
        cols = [c for c in t1.columns if c.startswith(cargo + "_")]
        tot = t1[cols].sum(axis=1).replace(0, np.nan)
        partidos = [c for c in cols if c.split("_")[1].isdigit()]
        for c in partidos:
            out["s" + c] = t1[c] / tot
        out[f"s{cargo}_BN"] = (t1[f"{cargo}_BRANCO"] + t1[f"{cargo}_NULO"]) / tot
        out[f"{cargo}_ESQ"] = t1[[c for c in partidos if c.split('_')[1] in BLOCO_ESQ]].sum(axis=1) / tot
        out[f"{cargo}_DIR"] = t1[[c for c in partidos if c.split('_')[1] in BLOCO_DIR]].sum(axis=1) / tot
        out[f"{cargo}_PL"] = t1[f"{cargo}_22"] / tot
    return out


def colunas_composicao(df: pd.DataFrame) -> list[str]:
    """Covariáveis de composição (exclui o PL como categoria de referência)."""
    return [c for c in df.columns
            if (c.startswith("sDF_") or c.startswith("sDE_")) and not c.endswith("_22")]
