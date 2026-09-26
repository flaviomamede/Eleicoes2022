#!/usr/bin/env python3
"""Calibragem ecológica Gov→Pres e contraste Positivo vs Diebold (todas as UFs)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

ROOT = Path(__file__).resolve().parents[1]
DADOS = ROOT / "dados"
SCORES = ROOT / "scores"
OUT = ROOT / "analise"
FIG = ROOT / "figuras"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

RNG = np.random.default_rng(2022)


def fit_rates(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Taxas em [0,1] via mínimos quadrados com caixas (Goodman restrito, 1 coluna)."""
    if len(y) < 30 or X.shape[0] < 30:
        return np.full(X.shape[1], np.nan)
    # evita seções sem comparecimento
    res = lsq_linear(X, y, bounds=(0.0, 1.0), method="bvls", lsmr_tol="auto", verbose=0)
    return res.x


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    d = df.query("grupo_urna in ['Positivo','Diebold']").copy()
    d["vGovA"] = d["vGovA"].fillna(0)
    d["vGovB"] = d["vGovB"].fillna(0)
    d["vPresA22"] = d["vPresA22"].fillna(0)
    d["vPresB13"] = d["vPresB13"].fillna(0)
    n = d["qComparecimento"].fillna(0).astype(float)
    # em alguns registros qComparecimento falta: usa soma dos votos presidenciais
    fallback = (
        d["vPresA22"]
        + d["vPresB13"]
        + d["vPresNulo"].fillna(0)
        + d["vPresBranco"].fillna(0)
    )
    n = np.where(n > 0, n, fallback)
    d["N"] = n
    d = d[d["N"] > 0].copy()
    outros = d["N"] - d["vGovA"] - d["vGovB"]
    d["GovOutros"] = np.clip(outros, 0, None)
    d["pA"] = d["vPresA22"] / d["N"]
    d["pB"] = d["vPresB13"] / d["N"]
    d["gA"] = d["vGovA"] / d["N"]
    d["gB"] = d["vGovB"] / d["N"]
    d["gO"] = d["GovOutros"] / d["N"]
    return d


def calibrate_uf(train: pd.DataFrame) -> dict:
    X = train[["gA", "gB", "gO"]].to_numpy(dtype=float)
    s22 = fit_rates(X, train["pA"].to_numpy(dtype=float))
    s13 = fit_rates(X, train["pB"].to_numpy(dtype=float))
    return {
        "s_GovA_Bolsonaro": float(s22[0]) if np.isfinite(s22[0]) else np.nan,
        "s_GovB_Bolsonaro": float(s22[1]) if np.isfinite(s22[1]) else np.nan,
        "s_Outros_Bolsonaro": float(s22[2]) if np.isfinite(s22[2]) else np.nan,
        "s_GovA_Lula": float(s13[0]) if np.isfinite(s13[0]) else np.nan,
        "s_GovB_Lula": float(s13[1]) if np.isfinite(s13[1]) else np.nan,
        "s_Outros_Lula": float(s13[2]) if np.isfinite(s13[2]) else np.nan,
        "n_treino": int(len(train)),
    }


def apply_rates(df: pd.DataFrame, rates: dict) -> pd.DataFrame:
    out = df.copy()
    out["est_Bolsonaro"] = out["N"] * (
        rates["s_GovA_Bolsonaro"] * out["gA"]
        + rates["s_GovB_Bolsonaro"] * out["gB"]
        + rates["s_Outros_Bolsonaro"] * out["gO"]
    )
    out["est_Lula"] = out["N"] * (
        rates["s_GovA_Lula"] * out["gA"]
        + rates["s_GovB_Lula"] * out["gB"]
        + rates["s_Outros_Lula"] * out["gO"]
    )
    out["res_Bolsonaro"] = out["vPresA22"] - out["est_Bolsonaro"]
    out["res_Lula"] = out["vPresB13"] - out["est_Lula"]
    return out


def mape_safe(y, yhat) -> float:
    y = np.asarray(y, float)
    yhat = np.asarray(yhat, float)
    denom = np.maximum(np.abs(y), 1.0)
    return float(np.mean(np.abs(y - yhat) / denom) * 100)


def main() -> None:
    print("lendo parquet…")
    raw = pd.read_parquet(DADOS / "urnas_pres_gov.parquet")
    # 2º turno: só dois candidatos a presidente — calibragem mais limpa
    d2 = prepare(raw.query("turno == 2"))

    ufs = sorted(d2["estado"].unique())
    rows_rates = []
    rows_resid = []
    rows_holdout = []
    detail_parts = []

    for uf in ufs:
        sub = d2[d2["estado"] == uf]
        pos = sub[sub["grupo_urna"] == "Positivo"]
        die = sub[sub["grupo_urna"] == "Diebold"]
        if len(pos) < 50:
            continue

        rates = calibrate_uf(pos)
        rates["uf"] = uf
        rates["fonte_calibragem"] = "Positivo (UE2020)"
        rows_rates.append(rates)

        # aplicar nas duas marcas
        for marca, chunk in [("Positivo", pos), ("Diebold", die)]:
            if len(chunk) < 10:
                continue
            pred = apply_rates(chunk, rates)
            detail_parts.append(pred.assign(uf=uf, marca_aplicada=marca))
            rows_resid.append(
                {
                    "uf": uf,
                    "marca": marca,
                    "urnas": len(chunk),
                    "votos_Bolsonaro": int(chunk["vPresA22"].sum()),
                    "votos_Lula": int(chunk["vPresB13"].sum()),
                    "est_Bolsonaro": float(pred["est_Bolsonaro"].sum()),
                    "est_Lula": float(pred["est_Lula"].sum()),
                    "res_Bolsonaro": float(pred["res_Bolsonaro"].sum()),
                    "res_Lula": float(pred["res_Lula"].sum()),
                    "erro_pct_Bolsonaro": float(
                        100
                        * pred["res_Bolsonaro"].sum()
                        / max(pred["est_Bolsonaro"].sum(), 1)
                    ),
                    "erro_pct_Lula": float(
                        100 * pred["res_Lula"].sum() / max(pred["est_Lula"].sum(), 1)
                    ),
                    "mape_secao_Bolsonaro": mape_safe(
                        chunk["vPresA22"], pred["est_Bolsonaro"]
                    ),
                    "mape_secao_Lula": mape_safe(chunk["vPresB13"], pred["est_Lula"]),
                }
            )

        # hold-out por zona (só Positivo)
        zonas = pos["zona"].unique()
        if len(zonas) >= 4:
            RNG.shuffle(zonas)
            cut = max(1, int(0.7 * len(zonas)))
            z_train, z_test = set(zonas[:cut]), set(zonas[cut:])
            tr = pos[pos["zona"].isin(z_train)]
            te = pos[pos["zona"].isin(z_test)]
            if len(tr) >= 50 and len(te) >= 20:
                r_ho = calibrate_uf(tr)
                pred_te = apply_rates(te, r_ho)
                pred_die = apply_rates(die, r_ho) if len(die) >= 10 else None
                rows_holdout.append(
                    {
                        "uf": uf,
                        "zonas_treino": len(z_train),
                        "zonas_teste": len(z_test),
                        "mape_teste_Positivo_Bolsonaro": mape_safe(
                            te["vPresA22"], pred_te["est_Bolsonaro"]
                        ),
                        "mape_teste_Positivo_Lula": mape_safe(
                            te["vPresB13"], pred_te["est_Lula"]
                        ),
                        "erro_pct_teste_Positivo_Bolsonaro": float(
                            100
                            * pred_te["res_Bolsonaro"].sum()
                            / max(pred_te["est_Bolsonaro"].sum(), 1)
                        ),
                        "erro_pct_teste_Positivo_Lula": float(
                            100
                            * pred_te["res_Lula"].sum()
                            / max(pred_te["est_Lula"].sum(), 1)
                        ),
                        "erro_pct_Diebold_Bolsonaro": (
                            float(
                                100
                                * pred_die["res_Bolsonaro"].sum()
                                / max(pred_die["est_Bolsonaro"].sum(), 1)
                            )
                            if pred_die is not None
                            else np.nan
                        ),
                        "erro_pct_Diebold_Lula": (
                            float(
                                100
                                * pred_die["res_Lula"].sum()
                                / max(pred_die["est_Lula"].sum(), 1)
                            )
                            if pred_die is not None
                            else np.nan
                        ),
                    }
                )

    rates_df = pd.DataFrame(rows_rates).sort_values("uf")
    resid_df = pd.DataFrame(rows_resid).sort_values(["uf", "marca"])
    hold_df = pd.DataFrame(rows_holdout).sort_values("uf")
    rates_df.to_csv(OUT / "taxas_calibradas_positivo_por_uf.csv", index=False)
    resid_df.to_csv(OUT / "residuos_positivo_vs_diebold.csv", index=False)
    hold_df.to_csv(OUT / "holdout_por_uf.csv", index=False)

    # contraste Diebold − Positivo no erro % (mesmo score)
    piv = resid_df.pivot(index="uf", columns="marca")
    contraste = pd.DataFrame(
        {
            "uf": piv.index,
            "erro_pct_Bolsonaro_Positivo": piv[("erro_pct_Bolsonaro", "Positivo")].values,
            "erro_pct_Bolsonaro_Diebold": piv[("erro_pct_Bolsonaro", "Diebold")].values,
            "delta_erro_Bolsonaro": (
                piv[("erro_pct_Bolsonaro", "Diebold")]
                - piv[("erro_pct_Bolsonaro", "Positivo")]
            ).values,
            "erro_pct_Lula_Positivo": piv[("erro_pct_Lula", "Positivo")].values,
            "erro_pct_Lula_Diebold": piv[("erro_pct_Lula", "Diebold")].values,
            "delta_erro_Lula": (
                piv[("erro_pct_Lula", "Diebold")] - piv[("erro_pct_Lula", "Positivo")]
            ).values,
            "urnas_Positivo": piv[("urnas", "Positivo")].values,
            "urnas_Diebold": piv[("urnas", "Diebold")].values,
        }
    )
    contraste.to_csv(OUT / "contraste_erro_por_uf.csv", index=False)

    # Brasil (somas)
    br = (
        resid_df.groupby("marca", as_index=False)[
            [
                "urnas",
                "votos_Bolsonaro",
                "votos_Lula",
                "est_Bolsonaro",
                "est_Lula",
                "res_Bolsonaro",
                "res_Lula",
            ]
        ]
        .sum()
    )
    br["erro_pct_Bolsonaro"] = 100 * br["res_Bolsonaro"] / br["est_Bolsonaro"]
    br["erro_pct_Lula"] = 100 * br["res_Lula"] / br["est_Lula"]
    br.to_csv(OUT / "residuos_brasil.csv", index=False)

    # --- scores subjetivos do VotoReal (agregados UF×marca×cargo) ---
    comp = pd.read_csv(SCORES / "agregado_comparacoes_votoreal.csv")
    # foco presidente via governador e média 4 cargos: cargo_codigo tipicamente
    # Documentação site: cargo 1 DE, etc. Filtrar ideologia Direita/Bolsonaro e Esquerda/Lula
    scores_jr = pd.read_csv(SCORES / "scores_votoreal_padrao.csv")
    scores_jr.to_csv(OUT / "scores_john_robson_referencia.csv", index=False)

    # erro % médio por marca e turno (todas as comparações do site)
    site = (
        comp.groupby(["turno", "marca"], as_index=False)
        .agg(
            n=("diferenca_percentual", "count"),
            erro_pct_medio=("diferenca_percentual", "mean"),
            erro_pct_mediano=("diferenca_percentual", "median"),
            votos_presidente=("votos_presidente", "sum"),
            votos_estimados=("votos_estimados", "sum"),
        )
    )
    site["erro_pct_total"] = 100 * (
        site["votos_presidente"] - site["votos_estimados"]
    ) / site["votos_estimados"]
    site.to_csv(OUT / "votoreal_erro_por_marca.csv", index=False)

    # por UF×marca no 2º turno, cargo governador se existir; senão todos
    c2 = comp[comp["turno"] == 2].copy()
    # pegar uma linha por uf×marca×presidente (média dos cargos ou só gov)
    gov = c2[c2["cargo"].str.contains("Governador", case=False, na=False)]
    if gov.empty:
        gov = c2
    site_uf = (
        gov.groupby(["uf", "marca", "presidente"], as_index=False)
        .agg(
            diferenca_percentual=("diferenca_percentual", "mean"),
            votos_presidente=("votos_presidente", "sum"),
            votos_estimados=("votos_estimados", "sum"),
        )
    )
    site_uf["erro_pct"] = 100 * (
        site_uf["votos_presidente"] - site_uf["votos_estimados"]
    ) / site_uf["votos_estimados"].clip(lower=1)
    site_uf.to_csv(OUT / "votoreal_erro_uf_marca_2t.csv", index=False)

    # --- figuras ---
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(10, 7))
    x = contraste["delta_erro_Bolsonaro"]
    y = contraste["delta_erro_Lula"]
    ax.axhline(0, color="#666", lw=0.8)
    ax.axvline(0, color="#666", lw=0.8)
    ax.scatter(x, y, s=np.sqrt(contraste["urnas_Diebold"]) * 2, alpha=0.75)
    for _, r in contraste.iterrows():
        ax.annotate(r["uf"], (r["delta_erro_Bolsonaro"], r["delta_erro_Lula"]), fontsize=8)
    ax.set_xlabel("Δ erro % Bolsonaro (Diebold − Positivo)")
    ax.set_ylabel("Δ erro % Lula (Diebold − Positivo)")
    ax.set_title("2º turno: mesmo modelo calibrado nas UE2020,\naplicado nas duas marcas")
    fig.tight_layout()
    fig.savefig(FIG / "contraste_delta_erro_uf.png", dpi=140)
    plt.close()

    fig, ax = plt.subplots(figsize=(11, 5))
    ordem = contraste.sort_values("delta_erro_Bolsonaro")
    ax.bar(ordem["uf"], ordem["delta_erro_Bolsonaro"], color="#4c78a8", label="Bolsonaro")
    ax.bar(
        ordem["uf"],
        ordem["delta_erro_Lula"],
        color="#f58518",
        alpha=0.7,
        label="Lula",
    )
    ax.axhline(0, color="black", lw=0.8)
    ax.set_ylabel("Δ erro % (Diebold − Positivo)")
    ax.set_title("Por UF: quanto o erro muda ao trocar Positivo → Diebold")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "barras_delta_erro_uf.png", dpi=140)
    plt.close()

    # resumo nacional turnos
    resumo = (
        raw.query("grupo_urna in ['Positivo','Diebold']")
        .groupby(["turno", "grupo_urna"], as_index=False)
        .agg(
            urnas=("id", "count"),
            Bolsonaro=("vPresA22", "sum"),
            Lula=("vPresB13", "sum"),
            GovA=("vGovA", "sum"),
            GovB=("vGovB", "sum"),
        )
    )
    resumo.to_csv(OUT / "totais_turno_grupo.csv", index=False)

    meta = {
        "metodo": "regressão ecológica restrita (lsq_linear bounds 0..1)",
        "preditores": ["fração GovA", "fração GovB", "fração outros no comparecimento"],
        "alvo": ["fração Bolsonaro", "fração Lula"],
        "turno": 2,
        "calibragem": "somente urnas Positivo (UE2020) por UF",
        "aplicacao": "Positivo e Diebold da mesma UF",
        "holdout": "70% zonas Positivo treino / 30% teste",
        "limitacao": (
            "sem votos partidários DE/DF/Sen; GovA/GovB são alinhamentos "
            "subjetivos do autor do SQLite; CDN TSE bloqueado (403)"
        ),
        "n_ufs": int(len(rates_df)),
    }
    (OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print("OK", OUT)
    print(br.to_string(index=False))
    print("\nmaiores |delta| Bolsonaro:")
    print(
        contraste.reindex(contraste["delta_erro_Bolsonaro"].abs().sort_values(ascending=False).index)
        .head(8)[["uf", "delta_erro_Bolsonaro", "delta_erro_Lula"]]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
