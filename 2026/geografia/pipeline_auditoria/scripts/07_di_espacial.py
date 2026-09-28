"""F3 — Invalidação diferencial com geografia (Forsberg caps. 6–7).

Usa o cache de locais de `06_espacial.py`. Perguntas:
  1) A taxa de brancos+nulos depende do apoio a Lula? (DI)
  2) Essa relação muda com a fração de urnas antigas no local?
  3) Após defasagem / erro espacial, o que sobra?

Saídas:
  resultados/di_espacial_naoespacial.csv
  resultados/di_espacial_espaciais.csv
  resultados/di_espacial_moran_residuos.csv
  resultados/di_espacial_sem.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import libpysal
import spreg
from esda import Moran
from statsmodels.genmod.generalized_linear_model import GLM
from statsmodels.genmod.families import Binomial
from statsmodels.genmod.families.links import logit

from common import CACHE, RESULTADOS, salvar


def carregar_locais() -> pd.DataFrame:
    p = CACHE / "locais_espacial.pkl"
    if not p.exists():
        raise FileNotFoundError("Rode antes scripts/06_espacial.py (gera locais_espacial.pkl).")
    m = pd.read_pickle(p).copy()
    m = m[(m.comp2 > 0) & (m.lula + m.bol > 0)].reset_index(drop=True)
    m["inv"] = (m.branco2 + m.nulo2).astype(float)
    m["val"] = (m.comp2 - m.inv).clip(lower=0).astype(float)
    m["pInv"] = m.inv / m.comp2
    m["pSup"] = m.lula / (m.lula + m.bol)
    return m


def glm_quasibin(inv, val, X: pd.DataFrame, rotulo: str) -> dict:
    """Quasi-binomial via GLM Binomial + escala de Pearson (Forsberg §6.2.3.2)."""
    endog = np.column_stack([inv, val])
    Xc = X.copy()
    Xc.insert(0, "const", 1.0)
    mod = GLM(endog, Xc, family=Binomial(link=logit()))
    # scale='X2' ≈ quasibinomial
    res = mod.fit(scale="X2", maxiter=100)
    # coeficiente de interesse: primeira coluna após const (pSup)
    nome = X.columns[0]
    return {
        "modelo": rotulo,
        "coef_pSup": float(res.params[nome]),
        "ep_pSup": float(res.bse[nome]),
        "z_pSup": float(res.tvalues[nome]),
        "p_pSup": float(res.pvalues[nome]),
        "scale": float(res.scale),
        "n": int(res.nobs),
    }


def main():
    m = carregar_locais()
    print(f"locais: {len(m)}")

    # --- não espacial (Cap. 6) ---
    rows = []
    rows.append(glm_quasibin(m.inv, m.val, m[["pSup"]], "QB: pInv ~ pSup"))
    X2 = m[["pSup", "old_frac"]].copy()
    X2["pSup_x_old"] = X2.pSup * X2.old_frac
    r2 = glm_quasibin(m.inv, m.val, X2, "QB: pInv ~ pSup + old + pSup×old")
    # extrair também coef de interação via refit report
    endog = np.column_stack([m.inv, m.val])
    Xc = X2.copy()
    Xc.insert(0, "const", 1.0)
    res = GLM(endog, Xc, family=Binomial(link=logit())).fit(scale="X2", maxiter=100)
    r2["coef_old"] = float(res.params["old_frac"])
    r2["z_old"] = float(res.tvalues["old_frac"])
    r2["p_old"] = float(res.pvalues["old_frac"])
    r2["coef_interacao"] = float(res.params["pSup_x_old"])
    r2["z_interacao"] = float(res.tvalues["pSup_x_old"])
    r2["p_interacao"] = float(res.pvalues["pSup_x_old"])
    rows.append(r2)
    naoesp = pd.DataFrame(rows)
    salvar(naoesp, "di_espacial_naoespacial.csv")
    print(naoesp[["modelo", "coef_pSup", "z_pSup", "p_pSup"]].to_string(index=False))

    # resíduos do modelo simples para Moran
    Xc1 = m[["pSup"]].copy()
    Xc1.insert(0, "const", 1.0)
    res1 = GLM(endog, Xc1, family=Binomial(link=logit())).fit(scale="X2", maxiter=100)
    m["resid_qb"] = m.pInv - res1.predict(Xc1)

    W = libpysal.weights.KNN.from_array(m[["x", "y"]].to_numpy(), k=8)
    W.transform = "r"
    mi = Moran(m["resid_qb"].to_numpy(), W, permutations=99)
    salvar(pd.DataFrame([{
        "variavel": "resíduo QB pInv~pSup",
        "I": mi.I, "z": mi.z_norm,
    }]), "di_espacial_moran_residuos.csv")
    print(f"Moran resíduos QB: I={mi.I:.3f} z={mi.z_norm:.1f}")

    # --- espaciais (Cap. 7): Y = pInv, X = pSup (+ old) ---
    y = m[["pInv"]].to_numpy()
    X = m[["pSup", "old_frac"]].to_numpy()
    ols = spreg.OLS(y, X)
    lag = spreg.GM_Lag(y, X, w=W, w_lags=1)
    err = spreg.GM_Error_Het(y, X, w=W)
    esp = pd.DataFrame([
        {"modelo": "MQO pInv~pSup+old", "coef_pSup": ols.betas[1][0],
         "ep": ols.std_err[1], "estat": ols.t_stat[1][0], "espacial": np.nan},
        {"modelo": "GM_Lag", "coef_pSup": lag.betas[1][0],
         "ep": lag.std_err[1], "estat": lag.z_stat[1][0], "espacial": lag.betas[-1][0]},
        {"modelo": "GM_Error_Het", "coef_pSup": err.betas[1][0],
         "ep": err.std_err[1], "estat": err.z_stat[1][0], "espacial": err.betas[-1][0]},
    ])
    salvar(esp, "di_espacial_espaciais.csv")
    print(esp.round(4).to_string(index=False))

    # --- SEM linear (Casetti): beta_0 e beta_1 lineares em lat/long ---
    # pInv ~ pSup * (lat + lon)  →  intercepto e efeito pSup variam no mapa
    u = (m.lat - m.lat.mean()) / m.lat.std()
    v = (m.long - m.long.mean()) / m.long.std()
    Xs = pd.DataFrame({
        "pSup": m.pSup,
        "lat_z": u,
        "lon_z": v,
        "pSup_x_lat": m.pSup * u,
        "pSup_x_lon": m.pSup * v,
        "old_frac": m.old_frac,
    })
    rsem = glm_quasibin(m.inv, m.val, Xs, "QB-SEM linear: pSup×(lat,lon)+old")
    Xsc = Xs.copy()
    Xsc.insert(0, "const", 1.0)
    rsem_fit = GLM(endog, Xsc, family=Binomial(link=logit())).fit(scale="X2", maxiter=100)
    for nome in Xs.columns:
        rsem[f"coef_{nome}"] = float(rsem_fit.params[nome])
        rsem[f"z_{nome}"] = float(rsem_fit.tvalues[nome])
        rsem[f"p_{nome}"] = float(rsem_fit.pvalues[nome])
    salvar(pd.DataFrame([rsem]), "di_espacial_sem.csv")
    print("SEM: coef_pSup={:.4f} z={:.2f} | pSup×lat z={:.2f} | pSup×lon z={:.2f}".format(
        rsem["coef_pSup"], rsem["z_pSup"],
        rsem["z_pSup_x_lat"], rsem["z_pSup_x_lon"]))

    # resumo curto
    (RESULTADOS / "di_espacial_resumo.txt").write_text(
        "F3 invalidação diferencial (locais, 2º turno)\n"
        f"n={len(m)}\n"
        f"QB pInv~pSup: coef={rows[0]['coef_pSup']:.4f} z={rows[0]['z_pSup']:.2f} p={rows[0]['p_pSup']:.3g}\n"
        f"interação pSup×old: coef={r2['coef_interacao']:.4f} z={r2['z_interacao']:.2f} p={r2['p_interacao']:.3g}\n"
        f"Moran resíduo QB: I={mi.I:.3f} z={mi.z_norm:.1f}\n"
        f"GM_Error coef_pSup={esp.loc[2,'coef_pSup']:.5f} z={esp.loc[2,'estat']:.2f} λ={esp.loc[2,'espacial']:.3f}\n"
        f"SEM pSup×lat z={rsem['z_pSup_x_lat']:.2f} pSup×lon z={rsem['z_pSup_x_lon']:.2f}\n"
    )
    print("ok -> resultados/di_espacial_*.csv")


if __name__ == "__main__":
    main()
