"""Reprodução e revisão do relatório "Uma análise estatística do 2º turno das
eleições de 2022 para presidente" (teste CMH, modelo de urna × candidato).

Saídas em resultados/:
  cmh_tabela1.csv           R e CMH por nível de estratificação
  cmh_tabela2_estados.csv   razão bruta, razão intramunicipal e rótulos do relatório
  cmh_tabela3_nove.csv      nove estados de maior razão bruta
  cmh_decomposicao.csv      SP × resto, região × porte de município
  cmh_magnitude.csv         votos necessários para anular a associação intramunicipal
"""
import numpy as np
import pandas as pd

from common import MARGEM_2T, base_com_modelo, cmh, salvar, tabela_2x2

# Valores da Tabela 2 como impressos no relatório original (R por estado).
TAB2_RELATORIO = {"DF": .973, "GO": 1.277, "MT": 1.150, "MS": 1.216, "AC": 1.226,
                  "AP": 2.632, "AM": 1.323, "PA": .884, "RO": 2.325, "RR": .869,
                  "TO": 1.118, "AL": 2.418, "BA": 1.189, "CE": 2.164, "MA": 1.702,
                  "PB": 2.464, "PE": 1.442, "PI": 1.020, "RN": 1.770, "SE": 1.725,
                  "PR": 1.934, "RS": .840, "SC": .908, "ES": 1.212, "MG": .710,
                  "RJ": .839, "SP": 1.054}
PEQUENOS = {"6 50K-100K", "7 <50K"}


def main():
    d = base_com_modelo(2)
    d = d[(d.PRES_13 + d.PRES_22) > 0]
    tab = tabela_2x2(d)
    tot = tab.sum()
    print(f"Totais: Lula {tot.A + tot.C:,.0f}  Bolsonaro {tot.B + tot.D:,.0f}")

    # Tabela 1
    peq = d.FX_APTOS_MUNICIPIO.isin(PEQUENOS)
    linhas = []
    for rotulo, chave, filtro in [
        ("município × zona", "mz", None), ("município", "mun", None),
        ("estado", "SG_UF", None), ("região", "REGIAO", None),
        ("municípios < 100 mil, por município", "mun", peq),
        ("municípios < 100 mil, por estado", "SG_UF", peq),
        ("municípios < 100 mil, por região", "REGIAO", peq),
    ]:
        dd = d if filtro is None else d[filtro]
        r = cmh(tabela_2x2(dd), dd[chave])
        linhas.append({"estratificacao": rotulo, **r})
    t1 = pd.DataFrame(linhas)
    salvar(t1, "cmh_tabela1.csv")
    print(t1.round(4).to_string(index=False))

    # Tabela 2: por estado
    linhas = []
    for uf, g in d.groupby("SG_UF"):
        tg = tabela_2x2(g).sum()
        bruto = tg.A * tg.D / (tg.B * tg.C)
        se = np.sqrt(1 / tg.A + 1 / tg.B + 1 / tg.C + 1 / tg.D)
        intra = cmh(tabela_2x2(g), g.mun)["R"]
        linhas.append({"UF": uf, "R_relatorio": TAB2_RELATORIO.get(uf), "R_bruto": bruto,
                       "EP_lnR_bruto": se, "R_intramunicipal": intra,
                       "lula_pct": (tg.A + tg.C) / tg.sum()})
    t2 = pd.DataFrame(linhas)
    # rótulo do relatório que contém o valor bruto verdadeiro de cada estado
    rel = {round(v, 3): k for k, v in TAB2_RELATORIO.items()}
    t2["rotulo_no_relatorio"] = t2.R_bruto.round(3).map(rel)
    t2["rotulo_trocado"] = t2.rotulo_no_relatorio != t2.UF
    salvar(t2, "cmh_tabela2_estados.csv")
    print(t2.round(3).to_string(index=False))

    # Tabela 3: nove estados de maior razão bruta
    nove = t2.nlargest(9, "R_bruto").UF.tolist()
    dn = d[d.SG_UF.isin(nove)]
    t3 = pd.DataFrame([
        {"estados": " ".join(nove), "estrato": "estado", **cmh(tabela_2x2(dn), dn.SG_UF)},
        {"estados": " ".join(nove), "estrato": "município", **cmh(tabela_2x2(dn), dn.mun)},
    ])
    salvar(t3, "cmh_tabela3_nove.csv")
    print(t3.round(4).to_string(index=False))

    # Decomposição
    grandes = ~peq
    linhas = []
    for rotulo, filtro in [("Brasil", slice(None)), ("só SP", d.SG_UF == "SP"),
                           ("sem SP", d.SG_UF != "SP"),
                           ("sem SP, >= 100 mil", (d.SG_UF != "SP") & grandes)]:
        dd = d[filtro]
        linhas.append({"recorte": rotulo, **cmh(tabela_2x2(dd), dd.mun)})
    for reg in sorted(d.REGIAO.dropna().unique()):
        dd = d[(d.REGIAO == reg) & peq & (d.SG_UF != "SP")]
        if len(dd):
            linhas.append({"recorte": f"{reg}, < 100 mil, sem SP", **cmh(tabela_2x2(dd), dd.mun)})
    t4 = pd.DataFrame(linhas)
    salvar(t4, "cmh_decomposicao.csv")
    print(t4.round(4).to_string(index=False))

    # Magnitude: votos a mover (Lula→Bolsonaro nas antigas) para igualar as proporções
    g = tabela_2x2(d).groupby(d.mun.values).sum()
    n1, n2 = g.A + g.B, g.C + g.D
    ok = (n1 > 0) & (n2 > 0)
    x = (g.A - n1 * g.C / n2)[ok]
    antigas_mistos = n1[ok].sum()
    antigas_total = (tab.A + tab.B).sum()
    sp = d.SG_UF == "SP"
    gsp = tabela_2x2(d[sp]).groupby(d[sp].mun.values).sum()
    n1s, n2s = gsp.A + gsp.B, gsp.C + gsp.D
    oks = (n1s > 0) & (n2s > 0)
    t5 = pd.DataFrame([{
        "transferencias_intramunicipais": x.sum(),
        "transferencias_intramunicipais_SP": (gsp.A - n1s * gsp.C / n2s)[oks].sum(),
        "votos_antigas_municipios_mistos": antigas_mistos,
        "taxa": x.sum() / antigas_mistos,
        "extrapolacao_todas_antigas": x.sum() / antigas_mistos * antigas_total,
        "efeito_margem_extrapolado": 2 * x.sum() / antigas_mistos * antigas_total,
        "margem_oficial": MARGEM_2T,
    }])
    salvar(t5, "cmh_magnitude.csv")
    print(t5.round(4).T.to_string())


if __name__ == "__main__":
    main()
