#!/usr/bin/env python3
"""Testes de controle T1/T2/T3 da calibragem (blocos partidários, soma 1).

T1: UE2020 capital → UE2020 interior (placebo geográfico)
T2: UE2020 → antigas no mesmo município (≥30 seções cada)
T3: antigas → UE2020 (direção inversa), por UF

Usa secoes_2022_t*.parquet + modelo de urna de urnas_pres_gov.parquet.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dados" / "base_secoes"
URNAS = ROOT / "dados" / "urnas_pres_gov.parquet"
OUT = ROOT / "analise"
FIG = ROOT / "figuras"
OUT.mkdir(exist_ok=True)

# Capitais (nome TSE aproximado → match por NM_MUNICIPIO)
CAPITAIS = {
    "AC": "RIO BRANCO",
    "AL": "MACEIO",
    "AM": "MANAUS",
    "AP": "MACAPA",
    "BA": "SALVADOR",
    "CE": "FORTALEZA",
    "DF": "BRASILIA",
    "ES": "VITORIA",
    "GO": "GOIANIA",
    "MA": "SAO LUIS",
    "MG": "BELO HORIZONTE",
    "MS": "CAMPO GRANDE",
    "MT": "CUIABA",
    "PA": "BELEM",
    "PB": "JOAO PESSOA",
    "PE": "RECIFE",
    "PI": "TERESINA",
    "PR": "CURITIBA",
    "RJ": "RIO DE JANEIRO",
    "RN": "NATAL",
    "RO": "PORTO VELHO",
    "RR": "BOA VISTA",
    "RS": "PORTO ALEGRE",
    "SC": "FLORIANOPOLIS",
    "SE": "ARACAJU",
    "SP": "SAO PAULO",
    "TO": "PALMAS",
}

BLOCOS = {
    "PL": {22},
    "DIREITA_ALIADA": {11, 10, 20, 14, 51, 28},  # PP, REPUBLICANOS, PSC, PTB, PATRIOTA, PRTB
    "CENTRO": {15, 44, 55, 45, 23, 19, 30, 12, 40, 77, 70, 90, 36, 33, 35, 27, 29},
    "ESQUERDA": {13, 65, 43, 50, 18, 16, 21, 80, 29},  # PT, PCdoB, PV, PSOL, REDE, PSTU, PCB, UP...
    "BRANCO_NULO": set(),  # colunas _BRANCO/_NULO
}
# PDT 12 is often centro-esquerda; keep in CENTRO as Opus listed PDT in ESQUERDA - fix:
BLOCOS["ESQUERDA"] |= {12}  # PDT
BLOCOS["CENTRO"] -= {12}

DESTINOS = ["Bolsonaro", "Lula", "Outros", "BrancoNulo"]


def norm_name(s: str) -> str:
    import unicodedata

    s = str(s).upper()
    s = "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )
    return s.replace("'", "").strip()


def load_secoes(turno: int) -> pd.DataFrame:
    pq = BASE / f"secoes_2022_t{turno}.parquet"
    if not pq.exists():
        raise FileNotFoundError(f"Ausente {pq} — rode gerar_base_secoes.py antes")
    return pd.read_parquet(pq)


def attach_modelo(df: pd.DataFrame, turno: int) -> pd.DataFrame:
    u = pd.read_parquet(URNAS)
    u = u[u["turno"] == turno][
        ["estado", "municipio", "zona", "secao", "modelUrna", "grupo_urna", "marca"]
    ].copy()
    u = u.rename(
        columns={
            "estado": "SG_UF",
            "municipio": "CD_MUNICIPIO",
            "zona": "NR_ZONA",
            "secao": "NR_SECAO",
        }
    )
    # se duplicata de chave no modelo, preferir primeira
    u = u.drop_duplicates(subset=["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"])
    m = df.merge(u, on=["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"], how="left")
    m["grupo"] = m["grupo_urna"].where(
        m["grupo_urna"].isin(["Positivo", "Diebold"]), "Outro"
    )
    return m


def mark_capital(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["_mun"] = df["NM_MUNICIPIO"].map(norm_name)
    caps = {uf: norm_name(n) for uf, n in CAPITAIS.items()}
    df["is_capital"] = [
        caps.get(uf) is not None and mun == caps.get(uf)
        for uf, mun in zip(df["SG_UF"], df["_mun"])
    ]
    return df


def bloco_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Frações dos blocos + alvos (proporções do comparecimento)."""
    N = df["QT_COMPARECIMENTO"].astype(float).replace(0, np.nan)
    cols_df = [c for c in df.columns if c.startswith("DF_")]
    # 2T: usar não há DF — caller passa turno 1 para composição; para 2T
    # o pipeline Opus usa partidos do 1T. Aqui T1/T2/T3 no 1T com DF.
    block_votes = {b: np.zeros(len(df)) for b in BLOCOS}
    assigned = set()
    for b, nums in BLOCOS.items():
        if b == "BRANCO_NULO":
            continue
        for n in nums:
            c = f"DF_{n}"
            if c in df.columns:
                block_votes[b] = block_votes[b] + df[c].astype(float).values
                assigned.add(c)
    # branco/nulo DF
    for suf in ("DF_BRANCO", "DF_NULO"):
        if suf in df.columns:
            block_votes["BRANCO_NULO"] = block_votes["BRANCO_NULO"] + df[suf].astype(float).values
            assigned.add(suf)
    # demais partidos DF → CENTRO
    for c in cols_df:
        if c in assigned or c.endswith("_OUTROS_TIPOS"):
            continue
        if c.endswith("_BRANCO") or c.endswith("_NULO"):
            continue
        block_votes["CENTRO"] = block_votes["CENTRO"] + df[c].astype(float).values

    X = pd.DataFrame(block_votes, index=df.index)
    for c in X.columns:
        X[c] = X[c] / N.values

    y = pd.DataFrame(index=df.index)
    y["Bolsonaro"] = df.get("PRES_22", 0).astype(float) / N
    y["Lula"] = df.get("PRES_13", 0).astype(float) / N
    y["BrancoNulo"] = (
        df.get("PRES_BRANCO", 0).astype(float) + df.get("PRES_NULO", 0).astype(float)
    ) / N
    y["Outros"] = (
        df.get("PRES_total_calc", pd.Series(0, index=df.index)).astype(float) * 0
    )
    # Outros = 1 - B - L - BN (clip)
    y["Outros"] = (1.0 - y["Bolsonaro"] - y["Lula"] - y["BrancoNulo"]).clip(lower=0)
    ok = N.notna() & (N > 0)
    return X.loc[ok].fillna(0), y.loc[ok].fillna(0), list(BLOCOS.keys())


def fit_rates(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Taxas (n_blocos × n_destinos), cada linha soma 1, entradas em [0,1]."""
    n_b, n_d = X.shape[1], Y.shape[1]
    # init: OLS clipped
    coef0 = np.zeros((n_b, n_d))
    for j in range(n_d):
        for i in range(n_b):
            if X[:, i].std() < 1e-12:
                continue
            # rough
            coef0[i, j] = np.clip(np.corrcoef(X[:, i], Y[:, j])[0, 1], 0, 1) * 0.25
        s = coef0[:, j].sum()
        if s > 0:
            coef0[:, j] *= 0.5 / max(s, 1e-9)
    # normalize rows
    for i in range(n_b):
        s = coef0[i].sum()
        coef0[i] = coef0[i] / s if s > 0 else np.array([0.25, 0.25, 0.25, 0.25])

    def pack(C):
        return C.ravel()

    def unpack(v):
        return v.reshape(n_b, n_d)

    def loss(v):
        C = unpack(v)
        pred = X @ C
        return np.mean((pred - Y) ** 2)

    cons = []
    for i in range(n_b):
        cons.append(
            {
                "type": "eq",
                "fun": lambda v, i=i: unpack(v)[i].sum() - 1.0,
            }
        )
    bounds = [(0.0, 1.0)] * (n_b * n_d)
    res = minimize(
        loss,
        pack(coef0),
        method="SLSQP",
        bounds=bounds,
        constraints=cons,
        options={"maxiter": 500, "ftol": 1e-10},
    )
    C = unpack(res.x)
    # renormalize numerical drift
    C = np.clip(C, 0, 1)
    C = C / C.sum(axis=1, keepdims=True).clip(min=1e-12)
    return C


def apply_and_metrics(df_train, df_test, label: str) -> dict | None:
    if len(df_train) < 40 or len(df_test) < 20:
        return None
    Xtr, Ytr, blocs = bloco_matrix(df_train)
    Xte, Yte, _ = bloco_matrix(df_test)
    if len(Xtr) < 40 or len(Xte) < 20:
        return None
    C = fit_rates(Xtr.to_numpy(float), Ytr.to_numpy(float))
    pred = Xte.to_numpy(float) @ C
    Nte = df_test.loc[Xte.index, "QT_COMPARECIMENTO"].astype(float).values
    # votos
    real_B = (Yte["Bolsonaro"].values * Nte).sum()
    real_L = (Yte["Lula"].values * Nte).sum()
    est_B = (pred[:, 0] * Nte).sum()
    est_L = (pred[:, 1] * Nte).sum()
    # proporções agregadas
    p_real_B = real_B / max(Nte.sum(), 1)
    p_est_B = est_B / max(Nte.sum(), 1)
    p_real_L = real_L / max(Nte.sum(), 1)
    p_est_L = est_L / max(Nte.sum(), 1)
    return {
        "label": label,
        "n_treino": len(df_train),
        "n_teste": len(df_test),
        "erro_rel_Bolsonaro": 100 * (real_B - est_B) / max(abs(est_B), 1),
        "erro_rel_Lula": 100 * (real_L - est_L) / max(abs(est_L), 1),
        "delta_pp_Bolsonaro": 100 * (p_real_B - p_est_B),
        "delta_pp_Lula": 100 * (p_real_L - p_est_L),
        "votos_Bolsonaro": real_B,
        "est_Bolsonaro": est_B,
        "votos_Lula": real_L,
        "est_Lula": est_L,
    }


def run_t1(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for uf, g in df.groupby("SG_UF"):
        pos = g[g["grupo"] == "Positivo"]
        cap = pos[pos["is_capital"]]
        inter = pos[~pos["is_capital"]]
        m = apply_and_metrics(cap, inter, "T1")
        if m:
            m["uf"] = uf
            rows.append(m)
    return pd.DataFrame(rows)


def run_t2(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (uf, mun), g in df.groupby(["SG_UF", "CD_MUNICIPIO"]):
        pos = g[g["grupo"] == "Positivo"]
        die = g[g["grupo"] == "Diebold"]
        if len(pos) < 30 or len(die) < 30:
            continue
        m = apply_and_metrics(pos, die, "T2")
        if m:
            m["uf"] = uf
            m["municipio"] = int(mun)
            m["nm_municipio"] = g["NM_MUNICIPIO"].iloc[0]
            rows.append(m)
    det = pd.DataFrame(rows)
    if det.empty:
        return det, pd.DataFrame()
    agg = (
        det.groupby("uf", as_index=False)
        .agg(
            n_municipios=("municipio", "nunique"),
            n_teste=("n_teste", "sum"),
            erro_rel_Bolsonaro=("erro_rel_Bolsonaro", "mean"),
            erro_rel_Lula=("erro_rel_Lula", "mean"),
            delta_pp_Bolsonaro=("delta_pp_Bolsonaro", "mean"),
            delta_pp_Lula=("delta_pp_Lula", "mean"),
        )
    )
    return det, agg


def run_t3(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for uf, g in df.groupby("SG_UF"):
        pos = g[g["grupo"] == "Positivo"]
        die = g[g["grupo"] == "Diebold"]
        m = apply_and_metrics(die, pos, "T3")
        if m:
            m["uf"] = uf
            rows.append(m)
    return pd.DataFrame(rows)


def main(turno: int = 1) -> None:
    print("carregando seções…")
    df = load_secoes(turno)
    print("modelo de urna…")
    df = attach_modelo(df, turno)
    df = mark_capital(df)
    print(
        "cobertura modelo",
        df["grupo"].value_counts(dropna=False).to_dict(),
        "capitais",
        df["is_capital"].sum(),
    )

    t1 = run_t1(df)
    t1.to_csv(OUT / f"controle_T1_capital_interior_{turno}t.csv", index=False)
    print("T1 UFs", len(t1))
    if len(t1):
        print(t1[["uf", "erro_rel_Bolsonaro", "delta_pp_Bolsonaro"]].sort_values("erro_rel_Bolsonaro").head(10))

    t2_det, t2_agg = run_t2(df)
    t2_det.to_csv(OUT / f"controle_T2_intramunicipal_det_{turno}t.csv", index=False)
    t2_agg.to_csv(OUT / f"controle_T2_intramunicipal_uf_{turno}t.csv", index=False)
    print("T2 municípios", len(t2_det), "UFs", len(t2_agg))

    t3 = run_t3(df)
    t3.to_csv(OUT / f"controle_T3_inversa_{turno}t.csv", index=False)
    print("T3 UFs", len(t3))

    # resumo
    resumo = {
        "turno": turno,
        "T1_erro_rel_B_medio": float(t1["erro_rel_Bolsonaro"].mean()) if len(t1) else None,
        "T2_erro_rel_B_medio": float(t2_agg["erro_rel_Bolsonaro"].mean()) if len(t2_agg) else None,
        "T3_erro_rel_B_medio": float(t3["erro_rel_Bolsonaro"].mean()) if len(t3) else None,
        "leitura": (
            "Se |T1| grande e |T2| ~0 → geografia; se |T1|~0 e |T2| grande → marca"
        ),
    }
    (OUT / f"controle_T1T2T3_resumo_{turno}t.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2)
    )
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(1)
