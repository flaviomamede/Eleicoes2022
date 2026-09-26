#!/usr/bin/env python3
"""2º turno: partidos do 1º turno (mesmo município/zona/seção) → presidente 2º turno."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "cal", ROOT / "scripts" / "calibragem_partido_pres.py"
)
cal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cal)

BUWEB = ROOT / "dados" / "buweb"
OUT = ROOT / "analise"
FIG = ROOT / "figuras"
CARGO = "Deputado Federal"


def main() -> None:
    ufs = sorted(
        {
            p.name.split("_")[0].upper()
            for p in BUWEB.glob("*_2t_secao.parquet")
        }
    )
    all_resid, all_rates, all_hold = [], [], []
    siglas = {}

    for uf in ufs:
        p1 = cal.load_uf(uf, 1, CARGO)
        if p1 is None and uf == "DF":
            p1 = cal.load_uf(uf, 1, "Deputado Distrital")
        p2sec = BUWEB / f"{uf.lower()}_2t_secao.parquet"
        if p1 is None or not p2sec.exists():
            print("skip", uf)
            continue
        part1, _sec1 = p1
        sec2 = pd.read_parquet(p2sec)
        # matriz partidária do 1T
        # precisa comparecimento e presidente do 2T → montar matrix com sec2
        # build_matrix espera part+sec do mesmo turno; adaptamos:
        keys = ["uf", "municipio", "zona", "secao"]
        # local pode divergir entre turnos — juntar sem local
        part1 = part1.copy()
        for _, r in part1[part1["tipo_votavel"] == "Partido"][
            ["nr_partido", "sg_partido"]
        ].drop_duplicates().iterrows():
            try:
                siglas[int(r["nr_partido"])] = r["sg_partido"]
            except Exception:
                pass

        # reutilizar build_matrix mas trocando sec pelo 2T (com N e votos 2T)
        # build_matrix faz merge part×sec por keys+local — alinhar local via merge sem local
        part_noloc = part1.drop(columns=["local"], errors="ignore")
        # agregar local fora
        pp = part_noloc[part_noloc["tipo_votavel"] == "Partido"].copy()
        pp["nr_partido"] = pd.to_numeric(pp["nr_partido"], errors="coerce").fillna(-1).astype(int)
        bn = part_noloc[part_noloc["tipo_votavel"].isin(["Branco", "Nulo"])].copy()
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
        for n in cal.PARTIDOS_REF:
            if n not in piv.columns:
                piv[n] = 0
        known = set(cal.PARTIDOS_REF) | set(keys)
        outros = [c for c in piv.columns if c not in known and not isinstance(c, str)]
        piv[0] = piv[outros].sum(axis=1) if outros else 0
        piv = piv.drop(columns=outros, errors="ignore")

        sec2k = sec2.drop(columns=["local"], errors="ignore")
        # se houver duplicata de chave (raro), somar presidente
        vote_cols = [c for c in sec2k.columns if c.startswith("vPres_") or c in ("qt_comparecimento",)]
        meta = ["grupo_urna", "modelUrna", "marca"]
        agg = {c: "sum" for c in vote_cols if c in sec2k.columns}
        for c in meta:
            if c in sec2k.columns:
                agg[c] = "first"
        sec2k = sec2k.groupby(keys, as_index=False).agg(agg)

        m = piv.merge(sec2k, on=keys, how="inner")
        m = m[m["grupo_urna"].isin(["Positivo", "Diebold"])].copy()
        m["N"] = m["qt_comparecimento"].replace(0, pd.NA)
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
        m["local"] = 0  # placeholder p/ holdout API
        m = m.dropna(subset=["N"])
        m = m[m["N"] > 0]

        pc = cal.party_cols(m)
        result = cal.calibrate_and_apply(m, pc)
        if not result:
            print("sem cal", uf)
            continue
        for row in result["residuos"]:
            row.update({"uf": uf, "turno": 2, "cargo": f"{CARGO} (1T→2T)"})
            all_resid.append(row)
        for row in result["taxas"]:
            row.update(
                {
                    "uf": uf,
                    "turno": 2,
                    "cargo": f"{CARGO} (1T→2T)",
                    "sg_partido": siglas.get(row["nr_partido"], str(row["nr_partido"])),
                }
            )
            all_rates.append(row)
        ho = cal.holdout_positivo(m, pc)
        if ho:
            ho.update({"uf": uf, "turno": 2, "cargo": f"{CARGO} (1T→2T)"})
            all_hold.append(ho)
        print(uf, "ok", result["n_positivo"], result["n_diebold"])

    tag = "2t_dep_federal_1t"
    resid = pd.DataFrame(all_resid)
    rates = pd.DataFrame(all_rates)
    hold = pd.DataFrame(all_hold)
    resid.to_csv(OUT / f"residuos_partido_{tag}.csv", index=False)
    rates.to_csv(OUT / f"taxas_partido_{tag}.csv", index=False)
    hold.to_csv(OUT / f"holdout_partido_{tag}.csv", index=False)

    if resid.empty:
        return
    piv = resid.pivot_table(
        index="uf", columns="marca", values=["erro_pct_Bolsonaro", "erro_pct_Lula", "urnas"]
    )
    contr = pd.DataFrame(
        {
            "uf": piv.index,
            "erro_pct_Bolsonaro_Positivo": piv[("erro_pct_Bolsonaro", "Positivo")],
            "erro_pct_Bolsonaro_Diebold": piv[("erro_pct_Bolsonaro", "Diebold")],
            "delta_Bolsonaro": piv[("erro_pct_Bolsonaro", "Diebold")]
            - piv[("erro_pct_Bolsonaro", "Positivo")],
            "erro_pct_Lula_Positivo": piv[("erro_pct_Lula", "Positivo")],
            "erro_pct_Lula_Diebold": piv[("erro_pct_Lula", "Diebold")],
            "delta_Lula": piv[("erro_pct_Lula", "Diebold")] - piv[("erro_pct_Lula", "Positivo")],
        }
    ).reset_index(drop=True)
    contr.to_csv(OUT / f"contraste_partido_{tag}.csv", index=False)
    br = resid.groupby("marca", as_index=False)[
        ["urnas", "votos_Bolsonaro", "votos_Lula", "est_Bolsonaro", "est_Lula", "res_Bolsonaro", "res_Lula"]
    ].sum()
    br["erro_pct_Bolsonaro"] = 100 * br["res_Bolsonaro"] / br["est_Bolsonaro"].abs().clip(lower=1)
    br["erro_pct_Lula"] = 100 * br["res_Lula"] / br["est_Lula"].abs().clip(lower=1)
    br.to_csv(OUT / f"residuos_brasil_partido_{tag}.csv", index=False)

    import matplotlib.pyplot as plt

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.axhline(0, color="#666", lw=0.8)
    ax.axvline(0, color="#666", lw=0.8)
    ax.scatter(contr["delta_Bolsonaro"], contr["delta_Lula"], s=60, alpha=0.8)
    for _, r in contr.iterrows():
        ax.annotate(r["uf"], (r["delta_Bolsonaro"], r["delta_Lula"]), fontsize=8)
    ax.set_xlabel("Δ erro % Bolsonaro (Diebold − Positivo)")
    ax.set_ylabel("Δ erro % Lula (Diebold − Positivo)")
    ax.set_title("2º turno · partidos do Dep. Federal (1T) → presidente (2T)\nCalibrado nas UE2020")
    fig.tight_layout()
    fig.savefig(FIG / f"contraste_partido_{tag}.png", dpi=140)
    plt.close()
    print(br.to_string(index=False))
    print("OK", OUT)


if __name__ == "__main__":
    main()
