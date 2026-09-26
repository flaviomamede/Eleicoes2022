"""Calibragem objetiva dos "scores" partidários do site votoreal (John Robson) e
testes de controle da calibragem por UF.

1. Taxas de transferência voto a deputado federal (1º turno) → voto presidencial,
   estimadas por regressão ecológica restrita (0 ≤ taxa ≤ 1), estado a estado,
   e comparadas com a tabela subjetiva do site.
2. Regra aprendida nas UE2020 e aplicada às urnas antigas da mesma UF (desenho do
   relatório de calibragem) e placebo com urnas da mesma marca: regra da capital
   aplicada ao interior.

Saídas em resultados/:
  scores_taxas_calibradas.csv, scores_placebo_capital_interior.csv,
  scores_regra_UE2020_para_antigas.csv
"""
import gc

import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear
from scipy.stats import spearmanr

from common import (BLOCO_DIR, BLOCO_ESQ, base_com_modelo, carregar_base, carregar_modelo,
                    cmh, salvar, tabela_2x2)

# Tabela do site votoreal (percentuais): Bolsonaro 1T, Bolsonaro 2T, Lula 1T, Lula 2T.
SCORES_JR = {
    "22": ("PL", 100, 100, 0, 0), "20": ("PSC", 90, 95, 10, 5),
    "10": ("REPUBLICANOS", 91.7, 91.7, 8.3, 8.3), "11": ("PP", 91.7, 91.7, 8.3, 8.3),
    "14": ("PTB", 85, 90, 15, 10), "51": ("PATRIOTA", 82, 87, 18, 13),
    "28": ("PRTB", 75, 75, 25, 25), "35": ("PMB", 66.7, 66.7, 33.3, 33.3),
    "30": ("NOVO", 58.3, 75, 41.7, 25), "27": ("DC", 50, 58.3, 50, 41.7),
    "44": ("UNIÃO", 50, 58.3, 50, 41.7), "19": ("PODE", 50, 50, 50, 50),
    "33": ("PMN", 50, 50, 50, 50), "45": ("PSDB", 50, 50, 50, 50),
    "55": ("PSD", 50, 50, 50, 50), "15": ("MDB", 50, 41.7, 50, 58.3),
    "23": ("CIDADANIA", 50, 41.7, 50, 58.3), "12": ("PDT", 50, 33.3, 50, 66.7),
    "90": ("PROS", 35, 40, 65, 60), "29": ("PCO", 16.7, 8.3, 83.3, 91.7),
    "36": ("AGIR", 16.7, 8.3, 83.3, 91.7), "70": ("AVANTE", 16.7, 8.3, 83.3, 91.7),
    "77": ("SOLIDARIEDADE", 16.7, 8.3, 83.3, 91.7), "18": ("REDE", 8.3, 8.3, 91.7, 91.7),
    "40": ("PSB", 8.3, 8.3, 91.7, 91.7), "43": ("PV", 8.3, 8.3, 91.7, 91.7),
    "50": ("PSOL", 8.3, 8.3, 91.7, 91.7), "65": ("PCdoB", 8.3, 8.3, 91.7, 91.7),
    "16": ("PSTU", 8.3, 0, 91.7, 100), "21": ("PCB", 8.3, 0, 91.7, 100),
    "80": ("UP", 8.3, 0, 91.7, 100), "13": ("PT", 0, 0, 100, 100),
}
BLOCOS = ["B_PL", "B_DIR", "B_CEN", "B_ESQ", "B_BN"]


def taxas_por_uf(t1, t2):
    """Taxas estado a estado; alvo: presidente no 1º e no 2º turno (mesma seção)."""
    P = [c for c in t1.columns if c.startswith("DF_") and c.split("_")[1].isdigit()] + ["DF_BRANCO", "DF_NULO"]
    alvo = t1[["ID_SECAO", "SG_UF"] + P + ["PRES_13", "PRES_22"]].merge(
        t2[["ID_SECAO", "PRES_13", "PRES_22"]].rename(columns={"PRES_13": "L2", "PRES_22": "B2"}), on="ID_SECAO")
    alvo = alvo[alvo.SG_UF != "ZZ"]
    acum = {}
    for uf, s in alvo.groupby("SG_UF"):
        A = s[P].to_numpy(float)
        keep = A.sum(0) > 0
        for nome, col in (("B1", "PRES_22"), ("L1", "PRES_13"), ("B2", "B2"), ("L2", "L2")):
            x = np.zeros(len(P))
            x[keep] = lsq_linear(A[:, keep], s[col].to_numpy(float), bounds=(0, 1)).x
            for p, v, w in zip(P, x, A.sum(0)):
                acum.setdefault((p, nome), []).append((v, w))
    linhas = []
    for num, (sigla, b1, b2, l1, l2) in SCORES_JR.items():
        p = f"DF_{num}"
        lin = {"numero": num, "partido": sigla, "JR_B1": b1, "JR_B2": b2, "JR_L1": l1, "JR_L2": l2}
        for nome in ("B1", "L1", "B2", "L2"):
            arr = np.array(acum.get((p, nome), [(np.nan, 0)]))
            lin[f"cal_{nome}"] = 100 * (arr[:, 0] * arr[:, 1]).sum() / max(arr[:, 1].sum(), 1)
        linhas.append(lin)
    return pd.DataFrame(linhas)


def blocos(d):
    P = [c for c in d.columns if c.startswith("DF_") and c.split("_")[1].isdigit()]
    d = d.copy()
    d["B_PL"] = d["DF_22"]
    d["B_DIR"] = d[[c for c in P if c.split("_")[1] in BLOCO_DIR]].sum(axis=1)
    d["B_ESQ"] = d[[c for c in P if c.split("_")[1] in BLOCO_ESQ]].sum(axis=1)
    d["B_CEN"] = d[[c for c in P if c.split("_")[1] not in BLOCO_DIR | BLOCO_ESQ | {"22"}]].sum(axis=1)
    d["B_BN"] = d.DF_BRANCO + d.DF_NULO
    return d


def erro_rel(treino, teste, alvo="PRES_22"):
    if len(treino) < 30 or len(teste) == 0:
        return np.nan
    fit = lsq_linear(treino[BLOCOS].to_numpy(float), treino[alvo].to_numpy(float), bounds=(0, 1))
    pred = (teste[BLOCOS].to_numpy(float) @ fit.x).sum()
    return 100 * (teste[alvo].sum() - pred) / pred


def main():
    t1, t2 = carregar_base(1), carregar_base(2)
    tx = taxas_por_uf(t1, t2)
    salvar(tx, "scores_taxas_calibradas.csv")
    print(tx.round(1).to_string(index=False))

    P = [c for c in t1.columns if c.startswith("DF_")]
    d = blocos(t1[["ID_SECAO", "SG_UF", "CD_MUNICIPIO", "QT_COMPARECIMENTO", "PRES_22"] + P])
    d = d[["ID_SECAO", "SG_UF", "QT_COMPARECIMENTO", "PRES_22"] + BLOCOS]
    del t1, t2
    gc.collect()
    d = d.merge(carregar_modelo()[["ID_SECAO", "old", "FG_CAPITAL"]], on="ID_SECAO")
    d = d[d.SG_UF != "ZZ"]
    d["cap"] = d.FG_CAPITAL.astype(str).isin(["1", "1.0", "S", "True"])
    linhas = []
    for uf, s in d.groupby("SG_UF"):
        cap_novas = s[s.cap & (s.old == 0)]
        lin = {"UF": uf,
               "frac_antigas_capital": (s[s.cap].old * s[s.cap].QT_COMPARECIMENTO).sum() / max(s[s.cap].QT_COMPARECIMENTO.sum(), 1),
               "frac_antigas_interior": (s[~s.cap].old * s[~s.cap].QT_COMPARECIMENTO).sum() / max(s[~s.cap].QT_COMPARECIMENTO.sum(), 1),
               "erro_capital_UE2020_para_interior_UE2020": erro_rel(cap_novas, s[~s.cap & (s.old == 0)]),
               "erro_capital_UE2020_para_interior_antigas": erro_rel(cap_novas, s[~s.cap & (s.old == 1)])}
        linhas.append(lin)
    pl = pd.DataFrame(linhas)
    salvar(pl, "scores_placebo_capital_interior.csv")
    print(pl.round(3).to_string(index=False))

    # Regra UE2020 → antigas por UF, comparada à razão bruta e à intramunicipal
    d2 = base_com_modelo(2)[["SG_UF", "mun", "old", "PRES_13", "PRES_22"]]
    linhas = []
    for uf, s in d.groupby("SG_UF"):
        s2 = d2[d2.SG_UF == uf]
        tg = tabela_2x2(s2).sum()
        linhas.append({"UF": uf,
                       "erro_UE2020_para_antigas": erro_rel(s[s.old == 0], s[s.old == 1]),
                       "lnR_bruto": np.log(tg.A * tg.D / (tg.B * tg.C)),
                       "lnR_intramunicipal": np.log(cmh(tabela_2x2(s2), s2.mun)["R"])})
    rg = pd.DataFrame(linhas).dropna()
    salvar(rg, "scores_regra_UE2020_para_antigas.csv")
    print(rg.round(3).to_string(index=False))
    print("Spearman erro × lnR bruto: %.2f | erro × lnR intramunicipal: %.2f" % (
        spearmanr(rg.erro_UE2020_para_antigas, rg.lnR_bruto)[0],
        spearmanr(rg.erro_UE2020_para_antigas, rg.lnR_intramunicipal)[0]))


if __name__ == "__main__":
    main()
