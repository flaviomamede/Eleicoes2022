"""Cauda da distribuição: urnas com votação mínima de Bolsonaro (página "Urnas com
Menos Votos" do votoreal) e coerência entre cargos na mesma urna.

Saídas em resultados/:
  cauda_AM_faixas.csv, cauda_AM_27_secoes_municipios.csv, cauda_AM_27_cargos.csv,
  cauda_nacional_taxas.csv, cauda_PL_deputado_vs_bolsonaro.csv
"""
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

from common import PRES_T1, base_com_modelo, carregar_base, salvar


def tipo_municipio(d):
    f = d.groupby("mun").old.mean()
    return d.mun.map(f).map(lambda x: "só antigas" if x == 1 else ("só UE2020" if x == 0 else "misto"))


def main():
    d = base_com_modelo(1)
    d["tipo_mun"] = tipo_municipio(d)
    fl = d.groupby("lv").old.agg(["min", "max"])
    d["lv_misto"] = d.lv.isin(fl.index[(fl["min"] == 0) & (fl["max"] == 1)])

    # Amazonas, 1º turno
    am = d[d.SG_UF == "AM"]
    salvar(pd.DataFrame([{"limite_votos_bolsonaro": k,
                          "secoes_antigas": int(((am.PRES_22 <= k) & (am.old == 1)).sum()),
                          "secoes_UE2020": int(((am.PRES_22 <= k) & (am.old == 0)).sum())}
                         for k in (0, 1, 2, 5, 10)]), "cauda_AM_faixas.csv")
    z = am[(am.PRES_22 == 0) & (am.old == 1)]
    mun = am[am.mun.isin(z.mun.unique())].groupby("NM_MUNICIPIO").agg(
        secoes=("ID_SECAO", "count"), frac_antigas=("old", "mean"),
        comparecimento=("QT_COMPARECIMENTO", "sum"), lula=("PRES_13", "sum"), bolsonaro=("PRES_22", "sum"))
    mun["secoes_zero_bolsonaro"] = z.groupby("NM_MUNICIPIO").size()
    salvar(mun.reset_index(), "cauda_AM_27_secoes_municipios.csv")
    print(f"AM: {len(z)} seções antigas com zero voto em Bolsonaro; Lula {z.PRES_13.sum()}")
    print(f"UE2020 do AM fora de Manaus: {int(((am.old == 0) & (am.NM_MUNICIPIO != 'MANAUS')).sum())}")

    P = [c for c in d.columns if c.startswith("DF_") and c.split("_")[1].isdigit()] + ["DF_BRANCO", "DF_NULO"]
    A = am[P].to_numpy(float)
    keep = A.sum(0) > 0
    x = np.zeros(len(P))
    x[keep] = lsq_linear(A[:, keep], am.PRES_22.to_numpy(float), bounds=(0, 1)).x
    comp = z.QT_COMPARECIMENTO.sum()
    comp_am = am.QT_COMPARECIMENTO.sum()
    linhas = [{"item": "Bolsonaro esperado com taxas calibradas no AM", "nas_27": float((z[P].to_numpy(float) @ x).sum()), "no_AM": np.nan}]
    for col in ("DF_22", "DF_55", "DF_44", "DF_10", "SEN_22", "SEN_55", "GOV_44", "GOV_15"):
        linhas.append({"item": col + " (% do comparecimento)", "nas_27": 100 * z[col].sum() / comp,
                       "no_AM": 100 * am[col].sum() / comp_am})
    cg = pd.DataFrame(linhas)
    salvar(cg, "cauda_AM_27_cargos.csv")
    print(cg.round(2).to_string(index=False))

    # Nacional: votação mínima por tipo de município e em locais mistos
    val = d[PRES_T1].sum(axis=1)
    d["baixo"] = (d.PRES_22 <= 0.02 * val) & (val > 0)
    d["zero"] = d.PRES_22 == 0
    linhas = []
    for rot, s in (("municípios mistos", d[d.tipo_mun == "misto"]), ("locais mistos", d[d.lv_misto]),
                   ("municípios só antigas", d[d.tipo_mun == "só antigas"]),
                   ("municípios só UE2020", d[d.tipo_mun == "só UE2020"])):
        for m, g in s.groupby("old"):
            linhas.append({"recorte": rot, "modelo": "antiga" if m == 1 else "UE2020", "secoes": len(g),
                           "zero_bolsonaro": int(g.zero.sum()),
                           "bolsonaro_ate_2pct_por_mil": 1000 * g.baixo.mean()})
    tx = pd.DataFrame(linhas)
    salvar(tx, "cauda_nacional_taxas.csv")
    print(tx.round(2).to_string(index=False))
    del d

    # PL alto para deputado (1º turno) e Bolsonaro baixo (2º turno), mesma seção
    t1 = carregar_base(1)[["ID_SECAO", "QT_COMPARECIMENTO", "DF_22", "SEN_22"]]
    t2 = base_com_modelo(2)[["ID_SECAO", "SG_UF", "NM_MUNICIPIO", "mun", "old", "PRES_13", "PRES_22"]]
    x2 = t2.merge(t1, on="ID_SECAO")
    x2 = x2[(x2.QT_COMPARECIMENTO > 0) & (x2.PRES_13 + x2.PRES_22 > 0)]
    x2["bol2"] = x2.PRES_22 / (x2.PRES_13 + x2.PRES_22)
    x2["pl_df"] = x2.DF_22 / x2.QT_COMPARECIMENTO
    x2["pl_sen"] = x2.SEN_22 / x2.QT_COMPARECIMENTO
    s = x2[(x2.bol2 < 0.10) & (x2.pl_df > 0.20)]
    f = x2.groupby("mun").old.mean()
    mix = x2[x2.mun.map(f).between(1e-9, 1 - 1e-9)]
    flag = (mix.bol2 < 0.10) & (mix.pl_df > 0.20)
    res = pd.DataFrame([{
        "secoes": len(s), "antigas": int(s.old.sum()), "UE2020": int((s.old == 0).sum()),
        "PL_deputado_pct_medio": 100 * s.pl_df.mean(), "PL_senado_pct_medio": 100 * s.pl_sen.mean(),
        "UFs": "; ".join(f"{k}:{v}" for k, v in s.SG_UF.value_counts().head(8).items()),
        "por_mil_mistos_UE2020": 1000 * flag[mix.old == 0].mean(),
        "por_mil_mistos_antigas": 1000 * flag[mix.old == 1].mean()}])
    salvar(res, "cauda_PL_deputado_vs_bolsonaro.csv")
    print(res.round(2).T.to_string())


if __name__ == "__main__":
    main()
