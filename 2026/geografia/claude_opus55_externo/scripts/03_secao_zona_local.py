"""Efeito do modelo de urna com a seção como unidade, dentro da zona e dentro do
local de votação; controles negativos; alocação em blocos; poder por fraude plantada.

Variável dependente: proporção de Lula entre Lula+Bolsonaro no 2º turno, por seção.
Composição legislativa: participação de cada partido no voto a deputado federal e
estadual do 1º turno, na mesma seção.

Saídas em resultados/:
  secao_dispersao.csv, secao_efeitos.csv, secao_controles_negativos.csv,
  secao_blocos.csv, secao_poder.csv
"""
import gc

import numpy as np
import pandas as pd

from common import (PRES_T1, base_com_modelo, carregar_base, colunas_composicao,
                    composicao_legislativa, efeito_fixo, estratos_mistos, salvar)

RNG = np.random.default_rng(7)


def preparar():
    d = base_com_modelo(2)
    t1 = carregar_base(1)
    extra = composicao_legislativa(t1)
    comp1 = t1.QT_COMPARECIMENTO.replace(0, np.nan)
    extra["abst1"] = t1.QT_ABSTENCOES / t1.QT_APTOS.replace(0, np.nan)
    extra["outros1"] = t1[[c for c in PRES_T1 if c not in ("PRES_13", "PRES_22")]].sum(axis=1) / comp1
    extra["bn1"] = (t1.PRES_BRANCO + t1.PRES_NULO) / comp1
    d = d.merge(extra, on="ID_SECAO", how="left")
    d["n"] = d.PRES_13 + d.PRES_22
    d = d[d.n > 0].copy()
    d["p"] = d.PRES_13 / d.n
    d["aptos100"] = d.QT_APTOS / 100
    d["secrank_z"] = d.groupby("mz").NR_SECAO.rank(pct=True)
    d["secrank_l"] = d.groupby("lv").NR_SECAO.rank(pct=True)
    d["grupo"] = np.where(d.SG_UF == "SP", "SP", np.where(d.REGIAO == "N", "Norte", "demais"))
    manter = (["ID_SECAO", "SG_UF", "grupo", "mz", "lv", "NR_SECAO", "old", "n", "p",
               "PRES_13", "PRES_22", "aptos100", "secrank_z", "secrank_l", "abst1",
               "outros1", "bn1", "DF_PL", "DF_ESQ", "DF_DIR", "DE_ESQ"] + colunas_composicao(d))
    return d[manter].copy()


def especificacoes(comp):
    return [
        ("zona", "sem covariáveis", ["old"]),
        ("zona", "+ cadastro", ["old", "aptos100", "secrank_z"]),
        ("zona", "+ cadastro + composição legislativa", ["old", "aptos100", "secrank_z"] + comp),
        ("local", "sem covariáveis", ["old"]),
        ("local", "+ cadastro", ["old", "aptos100", "secrank_l"]),
        ("local", "+ cadastro + composição legislativa", ["old", "aptos100", "secrank_l"] + comp),
    ]


def plantar(d, f, frac=1.0):
    x = d[["old", "n", "PRES_13", "PRES_22", "mz", "lv", "aptos100", "secrank_z",
           "secrank_l"] + colunas_composicao(d)].copy()
    sel = x.old.to_numpy() == 1
    if frac < 1:
        sel &= RNG.random(len(x)) < frac
    b22 = x.PRES_22.to_numpy().copy()
    b13 = x.PRES_13.to_numpy().copy()
    k = RNG.binomial(b22[sel], f)
    b13[sel] += k
    b22[sel] -= k
    x["PRES_13"], x["PRES_22"] = b13, b22
    x["p"] = b13 / x.n.to_numpy()
    return x, int(k.sum())


def main():
    d = preparar()
    comp = colunas_composicao(d)
    chaves = {"zona": "mz", "local": "lv"}

    # Sobredispersão dentro das zonas mistas
    mz = estratos_mistos(d, "mz")
    pz = mz.groupby("mz").PRES_13.transform("sum") / mz.groupby("mz").n.transform("sum")
    chi = ((mz.PRES_13 - mz.n * pz) ** 2 / (mz.n * pz * (1 - pz))).sum()
    phi = chi / (len(mz) - mz.mz.nunique())
    salvar(pd.DataFrame([{"secoes": len(mz), "zonas_mistas": mz.mz.nunique(), "phi_pearson": phi}]),
           "secao_dispersao.csv")
    print(f"dispersão de Pearson dentro das zonas: {phi:.2f}")

    # Efeitos
    linhas = []
    recortes = {"Brasil": d, "SP": d[d.grupo == "SP"], "Norte": d[d.grupo == "Norte"],
                "demais": d[d.grupo == "demais"]}
    for rec, dd in recortes.items():
        for nivel, rot, X in especificacoes(comp):
            k = chaves[nivel]
            r = efeito_fixo(estratos_mistos(dd, k), "p", X, k)
            linhas.append({"recorte": rec, "nivel": nivel, "especificacao": rot,
                           "efeito_pp": 100 * r["coef"], "ep_pp": 100 * r["ep"], "t": r["t"],
                           "secoes": r["n"], "clusters": r["clusters"]})
    ef = pd.DataFrame(linhas)
    salvar(ef, "secao_efeitos.csv")
    print(ef.round(3).to_string(index=False))

    # Controles negativos e balanço (peso igual por seção)
    linhas = []
    for rec in ("SP", "Brasil"):
        dd = recortes[rec]
        for y in ["DF_PL", "DF_ESQ", "DF_DIR", "DE_ESQ", "aptos100", "secrank_z",
                  "abst1", "outros1", "bn1"]:
            for nivel in ("zona", "local"):
                k = chaves[nivel]
                yy = "secrank_l" if (y == "secrank_z" and nivel == "local") else y
                r = efeito_fixo(estratos_mistos(dd, k), yy, ["old"], k, peso=None)
                linhas.append({"recorte": rec, "variavel": yy, "nivel": nivel,
                               "diferenca": r["coef"], "t": r["t"]})
    cn = pd.DataFrame(linhas)
    salvar(cn, "secao_controles_negativos.csv")
    print(cn.round(4).to_string(index=False))

    # Alocação em blocos: trocas de modelo entre seções consecutivas da mesma zona
    linhas = []
    for rec, dd in (("SP", recortes["SP"]), ("fora de SP", d[d.SG_UF != "SP"])):
        m = estratos_mistos(dd, "mz").sort_values(["mz", "NR_SECAO"])
        o, s = m.old.to_numpy(), m.mz.to_numpy()
        trocas = ((o[1:] != o[:-1]) & (s[1:] == s[:-1])).sum()
        g = m.groupby("mz").old.agg(["sum", "count"])
        esperado = (2 * g["sum"] * (g["count"] - g["sum"]) / g["count"]).sum()
        lv = estratos_mistos(dd, "mz").groupby("lv").old.agg(["min", "max"])
        linhas.append({"recorte": rec, "trocas_observadas": trocas, "trocas_esperadas": esperado,
                       "razao": trocas / esperado, "locais_em_zonas_mistas": len(lv),
                       "locais_so_antigas": int((lv["min"] == 1).sum()),
                       "locais_so_UE2020": int((lv["max"] == 0).sum()),
                       "locais_mistos": int(((lv["min"] == 0) & (lv["max"] == 1)).sum())})
    bl = pd.DataFrame(linhas)
    salvar(bl, "secao_blocos.csv")
    print(bl.round(3).to_string(index=False))

    # Poder: fraudes plantadas
    margem_votos = 1_069_823
    sp = recortes["SP"]
    f_sp = margem_votos / sp[sp.old == 1].PRES_22.sum()
    f_br = margem_votos / d[d.old == 1].PRES_22.sum()
    cenarios = [("SP, todas as antigas", sp, 0.005, 1.0), ("SP, todas as antigas", sp, 0.01, 1.0),
                ("SP, 30% das antigas", sp, f_sp, 0.3), ("SP, todas as antigas (inverte a margem)", sp, f_sp, 1.0),
                ("Brasil, 30% das antigas", d, f_br, 0.3), ("Brasil, todas as antigas (inverte a margem)", d, f_br, 1.0)]
    linhas = []
    for rot, base, f, frac in cenarios:
        x, k = plantar(base, f, frac)
        for nivel in ("zona", "local"):
            ch = chaves[nivel]
            X = ["old", "aptos100", "secrank_z" if nivel == "zona" else "secrank_l"] + comp
            r = efeito_fixo(estratos_mistos(x, ch), "p", X, ch)
            linhas.append({"cenario": rot, "f": f, "fracao_urnas": frac, "votos_transferidos": k,
                           "nivel": nivel, "efeito_pp": 100 * r["coef"], "t": r["t"]})
        print(rot, f"f={f:.3f}", k)
        del x
        gc.collect()
    pw = pd.DataFrame(linhas)
    salvar(pw, "secao_poder.csv")
    print(pw.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
