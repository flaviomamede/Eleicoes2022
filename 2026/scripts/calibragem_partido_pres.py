#!/usr/bin/env python3
"""Calibragem ecológica partido → presidente (todas as UFs disponíveis).

Estima taxas de transferência nas urnas Positivo (UE2020) e aplica nas Diebold.
Cargo de referência padrão: Deputado Federal (1º turno).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

ROOT = Path(__file__).resolve().parents[1]
BUWEB = ROOT / "dados" / "buweb"
OUT = ROOT / "analise"
FIG = ROOT / "figuras"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

# Partidos da tabela VotoReal (números oficiais)
PARTIDOS_REF = [
    10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 27, 28, 29, 30,
    33, 35, 36, 40, 43, 44, 45, 50, 51, 55, 70, 77, 80, 90, 95, 96,
]
# 95/96 usados como branco/nulo no cargo legislativo


def fit_rates(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    if X.shape[0] < 40 or np.nanstd(y) < 1e-9:
        return np.full(X.shape[1], np.nan)
    # remove colunas quase zeradas
    col_ok = X.sum(axis=0) > 1e-6
    coef = np.full(X.shape[1], np.nan)
    if col_ok.sum() == 0:
        return coef
    res = lsq_linear(
        X[:, col_ok], y, bounds=(0.0, 1.0), method="bvls", lsmr_tol="auto", verbose=0
    )
    coef[col_ok] = res.x
    # colunas vazias → 0 (sem informação)
    coef[~col_ok] = 0.0
    return coef


def load_uf(uf: str, turno: int, cargo: str) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    uf = uf.lower()
    tag = f"{uf}_{turno}t"
    p_part = BUWEB / f"{tag}_partido_secao.parquet"
    p_sec = BUWEB / f"{tag}_secao.parquet"
    if not p_part.exists() or not p_sec.exists():
        return None
    part = pd.read_parquet(p_part)
    sec = pd.read_parquet(p_sec)
    part = part[part["cargo"] == cargo].copy()
    if part.empty:
        return None
    return part, sec


def build_matrix(part: pd.DataFrame, sec: pd.DataFrame) -> pd.DataFrame:
    keys = ["uf", "municipio", "zona", "secao", "local"]
    # votos de partido (Nominal+Legenda já agregados como Partido)
    pp = part[part["tipo_votavel"] == "Partido"].copy()
    pp["nr_partido"] = pd.to_numeric(pp["nr_partido"], errors="coerce").fillna(-1).astype(int)
    # branco/nulo do cargo
    bn = part[part["tipo_votavel"].isin(["Branco", "Nulo"])].copy()
    bn["nr_partido"] = bn["tipo_votavel"].map({"Branco": 95, "Nulo": 96})

    long = pd.concat(
        [
            pp[keys + ["nr_partido", "qt_votos"]],
            bn[keys + ["nr_partido", "qt_votos"]],
        ],
        ignore_index=True,
    )
    piv = (
        long.pivot_table(
            index=keys, columns="nr_partido", values="qt_votos", aggfunc="sum", fill_value=0
        )
        .reset_index()
    )
    # garantir colunas dos partidos de referência
    for n in PARTIDOS_REF:
        if n not in piv.columns:
            piv[n] = 0
    # outros partidos → coluna 0
    known = set(PARTIDOS_REF) | set(keys)
    outros_cols = [c for c in piv.columns if c not in known and isinstance(c, (int, np.integer))]
    if outros_cols:
        piv[0] = piv[outros_cols].sum(axis=1)
        piv = piv.drop(columns=outros_cols)
    else:
        piv[0] = 0

    meta_cols = [
        c
        for c in [
            "qt_comparecimento",
            "vPres_bolsonaro",
            "vPres_lula",
            "vPres_total",
            "vPres_branco",
            "vPres_nulo",
            "grupo_urna",
            "modelUrna",
            "marca",
        ]
        if c in sec.columns
    ]
    m = piv.merge(sec[keys + meta_cols], on=keys, how="inner")
    m = m[m["grupo_urna"].isin(["Positivo", "Diebold"])].copy()
    m["N"] = m["qt_comparecimento"].replace(0, np.nan)
    # presidente outros = total - bolso - lula - branco - nulo
    for c in ("vPres_bolsonaro", "vPres_lula", "vPres_branco", "vPres_nulo", "vPres_total"):
        if c not in m.columns:
            m[c] = 0
    m["vPres_outros"] = (
        m["vPres_total"]
        - m["vPres_bolsonaro"]
        - m["vPres_lula"]
        - m["vPres_branco"]
        - m["vPres_nulo"]
    ).clip(lower=0)
    return m


def party_cols(df: pd.DataFrame) -> list:
    cols = [0] + PARTIDOS_REF
    return [c for c in cols if c in df.columns]


def calibrate_and_apply(m: pd.DataFrame, party_c: list) -> dict:
    pos = m[m["grupo_urna"] == "Positivo"]
    die = m[m["grupo_urna"] == "Diebold"]
    if len(pos) < 50:
        return {}

    Xpos = (pos[party_c].to_numpy(float) / pos[["N"]].to_numpy(float))
    Xpos = np.nan_to_num(Xpos, nan=0.0)

    targets = {
        "Bolsonaro": pos["vPres_bolsonaro"].to_numpy(float) / pos["N"].to_numpy(float),
        "Lula": pos["vPres_lula"].to_numpy(float) / pos["N"].to_numpy(float),
        "Outros": pos["vPres_outros"].to_numpy(float) / pos["N"].to_numpy(float),
        "Branco": pos["vPres_branco"].to_numpy(float) / pos["N"].to_numpy(float),
        "Nulo": pos["vPres_nulo"].to_numpy(float) / pos["N"].to_numpy(float),
    }
    rates = {}
    for name, y in targets.items():
        y = np.nan_to_num(y, nan=0.0)
        rates[name] = fit_rates(Xpos, y)

    def predict(chunk: pd.DataFrame) -> pd.DataFrame:
        X = np.nan_to_num(
            chunk[party_c].to_numpy(float) / chunk[["N"]].to_numpy(float), nan=0.0
        )
        out = chunk.copy()
        for name, coef in rates.items():
            frac = X @ np.nan_to_num(coef, nan=0.0)
            out[f"est_{name}"] = frac * chunk["N"].to_numpy(float)
        out["res_Bolsonaro"] = out["vPres_bolsonaro"] - out["est_Bolsonaro"]
        out["res_Lula"] = out["vPres_lula"] - out["est_Lula"]
        return out

    rows = []
    rate_rows = []
    for marca, chunk in [("Positivo", pos), ("Diebold", die)]:
        if len(chunk) < 10:
            continue
        pred = predict(chunk)
        rows.append(
            {
                "marca": marca,
                "urnas": len(chunk),
                "votos_Bolsonaro": float(chunk["vPres_bolsonaro"].sum()),
                "votos_Lula": float(chunk["vPres_lula"].sum()),
                "est_Bolsonaro": float(pred["est_Bolsonaro"].sum()),
                "est_Lula": float(pred["est_Lula"].sum()),
                "res_Bolsonaro": float(pred["res_Bolsonaro"].sum()),
                "res_Lula": float(pred["res_Lula"].sum()),
                "erro_pct_Bolsonaro": float(
                    100
                    * pred["res_Bolsonaro"].sum()
                    / max(abs(pred["est_Bolsonaro"].sum()), 1)
                ),
                "erro_pct_Lula": float(
                    100 * pred["res_Lula"].sum() / max(abs(pred["est_Lula"].sum()), 1)
                ),
            }
        )
    for i, n in enumerate(party_c):
        rate_rows.append(
            {
                "nr_partido": int(n),
                "s_Bolsonaro": float(rates["Bolsonaro"][i]),
                "s_Lula": float(rates["Lula"][i]),
                "s_Outros": float(rates["Outros"][i]),
                "s_Branco": float(rates["Branco"][i]),
                "s_Nulo": float(rates["Nulo"][i]),
            }
        )
    return {"residuos": rows, "taxas": rate_rows, "n_positivo": len(pos), "n_diebold": len(die)}


def holdout_positivo(m: pd.DataFrame, party_c: list, seed: int = 2022) -> dict:
    pos = m[m["grupo_urna"] == "Positivo"].copy()
    if pos["zona"].nunique() < 4 or len(pos) < 80:
        return {}
    rng = np.random.default_rng(seed)
    zonas = pos["zona"].unique()
    rng.shuffle(zonas)
    cut = max(1, int(0.7 * len(zonas)))
    tr = pos[pos["zona"].isin(zonas[:cut])]
    te = pos[pos["zona"].isin(zonas[cut:])]
    if len(tr) < 40 or len(te) < 20:
        return {}
    Xtr = np.nan_to_num(tr[party_c].to_numpy(float) / tr[["N"]].to_numpy(float), nan=0.0)
    yB = np.nan_to_num((tr["vPres_bolsonaro"] / tr["N"]).to_numpy(float), nan=0.0)
    yL = np.nan_to_num((tr["vPres_lula"] / tr["N"]).to_numpy(float), nan=0.0)
    cB, cL = fit_rates(Xtr, yB), fit_rates(Xtr, yL)
    Xte = np.nan_to_num(te[party_c].to_numpy(float) / te[["N"]].to_numpy(float), nan=0.0)
    estB = (Xte @ np.nan_to_num(cB, nan=0.0)) * te["N"].to_numpy(float)
    estL = (Xte @ np.nan_to_num(cL, nan=0.0)) * te["N"].to_numpy(float)
    resB = te["vPres_bolsonaro"].to_numpy(float) - estB
    resL = te["vPres_lula"].to_numpy(float) - estL
    return {
        "erro_pct_teste_Bolsonaro": float(100 * resB.sum() / max(abs(estB.sum()), 1)),
        "erro_pct_teste_Lula": float(100 * resL.sum() / max(abs(estL.sum()), 1)),
        "mape_teste_Bolsonaro": float(
            np.mean(np.abs(resB) / np.maximum(te["vPres_bolsonaro"].to_numpy(float), 1)) * 100
        ),
        "mape_teste_Lula": float(
            np.mean(np.abs(resL) / np.maximum(te["vPres_lula"].to_numpy(float), 1)) * 100
        ),
        "zonas_treino": int(cut),
        "zonas_teste": int(len(zonas) - cut),
    }


def main(turno: int = 1, cargo: str = "Deputado Federal") -> None:
    # descobrir UFs
    ufs = sorted(
        {
            p.name.split("_")[0].upper()
            for p in BUWEB.glob(f"*_{turno}t_partido_secao.parquet")
        }
    )
    print("UFs", ufs, "turno", turno, "cargo", cargo)

    all_resid = []
    all_rates = []
    all_hold = []
    siglas = {}

    for uf in ufs:
        loaded = load_uf(uf, turno, cargo)
        if loaded is None:
            # tentar Distrital no DF
            if uf == "DF" and cargo == "Deputado Estadual":
                loaded = load_uf(uf, turno, "Deputado Distrital")
            if loaded is None:
                print("skip", uf)
                continue
        part, sec = loaded
        # mapa siglas
        for _, r in part[part["tipo_votavel"] == "Partido"][
            ["nr_partido", "sg_partido"]
        ].drop_duplicates().iterrows():
            siglas[int(r["nr_partido"])] = r["sg_partido"]

        m = build_matrix(part, sec)
        pc = party_cols(m)
        result = calibrate_and_apply(m, pc)
        if not result:
            print("sem calibragem", uf)
            continue
        for row in result["residuos"]:
            row["uf"] = uf
            row["turno"] = turno
            row["cargo"] = cargo
            all_resid.append(row)
        for row in result["taxas"]:
            row["uf"] = uf
            row["turno"] = turno
            row["cargo"] = cargo
            row["sg_partido"] = siglas.get(row["nr_partido"], str(row["nr_partido"]))
            all_rates.append(row)
        ho = holdout_positivo(m, pc)
        if ho:
            ho["uf"] = uf
            ho["turno"] = turno
            ho["cargo"] = cargo
            all_hold.append(ho)
        print(
            uf,
            "pos",
            result["n_positivo"],
            "die",
            result["n_diebold"],
            "ok",
        )

    resid = pd.DataFrame(all_resid)
    rates = pd.DataFrame(all_rates)
    hold = pd.DataFrame(all_hold)
    tag = f"{turno}t_{cargo.lower().replace(' ', '_')}"
    resid.to_csv(OUT / f"residuos_partido_{tag}.csv", index=False)
    rates.to_csv(OUT / f"taxas_partido_{tag}.csv", index=False)
    hold.to_csv(OUT / f"holdout_partido_{tag}.csv", index=False)

    # contraste
    if not resid.empty:
        piv = resid.pivot_table(index="uf", columns="marca", values=["erro_pct_Bolsonaro", "erro_pct_Lula", "urnas"])
        contr = pd.DataFrame(
            {
                "uf": piv.index,
                "erro_pct_Bolsonaro_Positivo": piv[("erro_pct_Bolsonaro", "Positivo")],
                "erro_pct_Bolsonaro_Diebold": piv[("erro_pct_Bolsonaro", "Diebold")],
                "delta_Bolsonaro": piv[("erro_pct_Bolsonaro", "Diebold")]
                - piv[("erro_pct_Bolsonaro", "Positivo")],
                "erro_pct_Lula_Positivo": piv[("erro_pct_Lula", "Positivo")],
                "erro_pct_Lula_Diebold": piv[("erro_pct_Lula", "Diebold")],
                "delta_Lula": piv[("erro_pct_Lula", "Diebold")]
                - piv[("erro_pct_Lula", "Positivo")],
            }
        ).reset_index(drop=True)
        contr.to_csv(OUT / f"contraste_partido_{tag}.csv", index=False)

        # Brasil
        br = resid.groupby("marca", as_index=False)[
            ["urnas", "votos_Bolsonaro", "votos_Lula", "est_Bolsonaro", "est_Lula", "res_Bolsonaro", "res_Lula"]
        ].sum()
        br["erro_pct_Bolsonaro"] = 100 * br["res_Bolsonaro"] / br["est_Bolsonaro"].abs().clip(lower=1)
        br["erro_pct_Lula"] = 100 * br["res_Lula"] / br["est_Lula"].abs().clip(lower=1)
        br.to_csv(OUT / f"residuos_brasil_partido_{tag}.csv", index=False)

        # figura
        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.axhline(0, color="#666", lw=0.8)
        ax.axvline(0, color="#666", lw=0.8)
        ax.scatter(contr["delta_Bolsonaro"], contr["delta_Lula"], s=60, alpha=0.8)
        for _, r in contr.iterrows():
            ax.annotate(r["uf"], (r["delta_Bolsonaro"], r["delta_Lula"]), fontsize=8)
        ax.set_xlabel("Δ erro % Bolsonaro (Diebold − Positivo)")
        ax.set_ylabel("Δ erro % Lula (Diebold − Positivo)")
        ax.set_title(
            f"{turno}º turno · cargo {cargo}\nCalibrado nas UE2020, aplicado nas duas marcas"
        )
        fig.tight_layout()
        fig.savefig(FIG / f"contraste_partido_{tag}.png", dpi=140)
        plt.close()

        # taxas médias nacionais (média simples por UF nas Positivo — só descritivo)
        # melhor: média ponderada pelo total de votos do partido nas Positivo — aproximar média simples
        mean_rates = (
            rates.groupby(["nr_partido", "sg_partido"], as_index=False)[
                ["s_Bolsonaro", "s_Lula", "s_Outros"]
            ]
            .mean()
            .sort_values("s_Bolsonaro", ascending=False)
        )
        mean_rates.to_csv(OUT / f"taxas_medias_uf_{tag}.csv", index=False)

    meta = {
        "turno": turno,
        "cargo": cargo,
        "ufs": ufs,
        "metodo": "lsq_linear bounds [0,1] por coluna de destino (Bolsonaro, Lula, Outros, Branco, Nulo)",
        "calibragem": "somente Positivo (UE2020) por UF",
        "aplicacao": "Positivo e Diebold",
    }
    (OUT / f"meta_partido_{tag}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2)
    )
    print("gravado em", OUT)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--turno", type=int, default=1)
    ap.add_argument("--cargo", default="Deputado Federal")
    args = ap.parse_args()
    main(turno=args.turno, cargo=args.cargo)
    # também deputado estadual / governador no 1t
    if args.turno == 1 and args.cargo == "Deputado Federal":
        main(turno=1, cargo="Deputado Estadual")
        main(turno=1, cargo="Governador")
