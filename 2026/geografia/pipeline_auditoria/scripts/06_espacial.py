"""Primeira etapa da análise geográfica (Forsberg, cap. 7), com o local de votação
como unidade.

1. Coordenadas de Hidalgo (v0.16) casadas com os locais da base de boletins e
   validadas por ponto-no-polígono (municípios geobr 2022).
2. Alcance da comparação através das fronteiras municipais para os municípios
   que só tiveram urnas antigas.
3. Índice de Moran global (8 vizinhos mais próximos).
4. Efeito da fração de urnas antigas: MQO, defasagem espacial (GM_Lag) e erro
   espacial (GM_Error_Het), com composição legislativa e efeito fixo de UF.

Saídas em resultados/:
  espacial_validacao.csv, espacial_proximidade.csv, espacial_moran.csv,
  espacial_modelos.csv; e dados/cache/locais_espacial.pkl
"""
import gc

import geopandas as gpd
import libpysal
import numpy as np
import pandas as pd
import spreg
from esda import Moran
from scipy.spatial import cKDTree

from common import CACHE, GEO, base_com_modelo, carregar_base, salvar

CHAVE = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO"]


def locais():
    d = base_com_modelo(2)
    d = d[(d.PRES_13 + d.PRES_22) > 0]
    loc = d.groupby(CHAVE).agg(secoes=("ID_SECAO", "count"), n_old=("old", "sum"),
                               lula=("PRES_13", "sum"), bol=("PRES_22", "sum"),
                               branco2=("PRES_BRANCO", "sum"), nulo2=("PRES_NULO", "sum"),
                               comp2=("QT_COMPARECIMENTO", "sum")).reset_index()
    del d
    gc.collect()
    t1 = carregar_base(1)
    P = [c for c in t1.columns if c.startswith("DF_")]
    a1 = t1[t1.SG_UF != "ZZ"].groupby(CHAVE)[P + ["QT_COMPARECIMENTO"]].sum().reset_index()
    del t1
    gc.collect()
    return loc.merge(a1, on=CHAVE, how="left")


def main():
    loc = locais()
    g = pd.read_csv(GEO / "geocoded_polling_stations.csv.gz", low_memory=False)
    g = g[g.ano == 2022][["cd_localidade_tse", "nr_zona", "nr_locvot", "cod_localidade_ibge",
                          "long", "lat", "conf_dist_km", "tse_lat"]]
    m = loc.merge(g, left_on=["CD_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO"],
                  right_on=["cd_localidade_tse", "nr_zona", "nr_locvot"], how="left")
    mun = gpd.read_parquet(GEO / "municipalities_2022_simplified.parquet")[["code_muni", "geometry"]]
    ok = m.lat.notna()
    pts = gpd.GeoDataFrame(m[ok], geometry=gpd.points_from_xy(m[ok].long, m[ok].lat), crs=mun.crs)
    j = gpd.sjoin(pts, mun, how="left", predicate="within")
    j = j[~j.index.duplicated()]
    dentro = (j.code_muni == j.cod_localidade_ibge)
    munp = mun.set_index("code_muni").to_crs(5880)
    fora = j[~dentro]
    fp = gpd.GeoSeries(fora.geometry, crs=mun.crs).to_crs(5880)
    dist = [fp.iloc[i].distance(munp.geometry.get(c)) / 1000 if c in munp.index else np.nan
            for i, c in enumerate(fora.cod_localidade_ibge)]
    m["dist_mun_km"] = np.nan
    m.loc[j.index, "dist_mun_km"] = 0.0
    m.loc[fora.index, "dist_mun_km"] = dist
    salvar(pd.DataFrame([{
        "locais_base": len(m), "com_coordenada": int(ok.sum()),
        "coordenada_TSE_pct": 100 * m.tse_lat.notna().mean(),
        "erro_ate_1km_pct": 100 * (m.conf_dist_km <= 1).mean(),
        "dentro_do_municipio_pct": 100 * dentro.mean(),
        "fora_mais_5km": int((m.dist_mun_km > 5).sum())}]), "espacial_validacao.csv")

    m = m[ok & (m.dist_mun_km <= 5)].copy()
    xy = gpd.GeoSeries(gpd.points_from_xy(m.long, m.lat), crs=4674).to_crs(5880)
    m["x"], m["y"] = xy.x.to_numpy(), xy.y.to_numpy()
    m["old_frac"] = m.n_old / m.secoes
    m["mun"] = m.SG_UF + "_" + m.CD_MUNICIPIO.astype(str)
    m["frac_old_mun"] = m.mun.map(m.groupby("mun").apply(lambda s: s.n_old.sum() / s.secoes.sum()))

    # Proximidade através das fronteiras
    novas = m[m.old_frac < 1]
    alvo = m[m.frac_old_mun == 1]
    dkm, _ = cKDTree(novas[["x", "y"]].to_numpy()).query(alvo[["x", "y"]].to_numpy(), k=1)
    dkm = dkm / 1000
    v = (alvo.lula + alvo.bol).to_numpy()
    salvar(pd.DataFrame([{"raio_km": r, "locais_pct": 100 * (dkm <= r).mean(),
                          "votos_pct": 100 * v[dkm <= r].sum() / v.sum()} for r in (2, 5, 10, 20)]),
           "espacial_proximidade.csv")

    # Variáveis e resíduo do modelo legislativo
    m = m[(m.QT_COMPARECIMENTO > 0)].reset_index(drop=True)
    m["p"] = m.lula / (m.lula + m.bol)
    m["inval"] = (m.branco2 + m.nulo2) / m.comp2
    P = [c for c in m.columns if c.startswith("DF_") and c.split("_")[1].isdigit()]
    S = m[P + ["DF_BRANCO", "DF_NULO"]].div(m.QT_COMPARECIMENTO, axis=0).drop(columns=["DF_22"])
    S = S.loc[:, S.std() > 0.002]
    UF = pd.get_dummies(m.SG_UF, drop_first=True).astype(float)
    X0 = pd.concat([S, UF], axis=1)
    X0.insert(0, "const", 1.0)
    w = (m.lula + m.bol).to_numpy(float)
    b = np.linalg.lstsq(X0.to_numpy() * np.sqrt(w)[:, None], m.p.to_numpy() * np.sqrt(w), rcond=None)[0]
    m["res"] = m.p - X0.to_numpy() @ b

    W = libpysal.weights.KNN.from_array(m[["x", "y"]].to_numpy(), k=8)
    W.transform = "r"
    mor = []
    for var, rot in (("p", "proporção de Lula, 2º turno"), ("inval", "brancos e nulos para presidente, 2º turno"),
                     ("res", "resíduo do modelo legislativo com efeito fixo de UF"),
                     ("old_frac", "fração de seções com urna antiga")):
        mi = Moran(m[var].to_numpy(), W, permutations=99)
        mor.append({"variavel": rot, "I": mi.I, "z": mi.z_norm})
    salvar(pd.DataFrame(mor), "espacial_moran.csv")
    print(pd.DataFrame(mor).round(3).to_string(index=False))

    X = pd.concat([m[["old_frac"]], S, UF], axis=1)
    y = m[["p"]].to_numpy()
    ols = spreg.OLS(y, X.to_numpy())
    lag = spreg.GM_Lag(y, X.to_numpy(), w=W, w_lags=1)
    err = spreg.GM_Error_Het(y, X.to_numpy(), w=W)
    mod = pd.DataFrame([
        {"modelo": "MQO", "coef_pp": 100 * ols.betas[1][0], "ep_pp": 100 * ols.std_err[1], "estat": ols.t_stat[1][0], "espacial": np.nan},
        {"modelo": "defasagem espacial (GM_Lag)", "coef_pp": 100 * lag.betas[1][0], "ep_pp": 100 * lag.std_err[1], "estat": lag.z_stat[1][0], "espacial": lag.betas[-1][0]},
        {"modelo": "erro espacial (GM_Error_Het)", "coef_pp": 100 * err.betas[1][0], "ep_pp": 100 * err.std_err[1], "estat": err.z_stat[1][0], "espacial": err.betas[-1][0]},
    ])
    salvar(mod, "espacial_modelos.csv")
    print(mod.round(3).to_string(index=False))
    m.drop(columns=[c for c in m.columns if c.startswith("DF_")]).to_pickle(CACHE / "locais_espacial.pkl")


if __name__ == "__main__":
    main()
