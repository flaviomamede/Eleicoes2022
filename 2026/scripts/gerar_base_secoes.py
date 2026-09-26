#!/usr/bin/env python3
"""Base larga por seção (TSE BU Web 2022) — parquet por UF, retomável.

Uso:
  python scripts/gerar_base_secoes.py              # processa o que falta + finaliza
  python scripts/gerar_base_secoes.py --so-final   # só concatena parquets já ok
  python scripts/gerar_base_secoes.py --uf SP --turno 1
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DADOS = ROOT / "dados"
OUT = DADOS / "base_secoes"
POR_UF = OUT / "por_uf"
OUT.mkdir(parents=True, exist_ok=True)
POR_UF.mkdir(parents=True, exist_ok=True)
MANIFEST = OUT / "manifesto.json"

META_COLS = [
    "ID_SECAO",
    "NR_TURNO",
    "SG_UF",
    "CD_MUNICIPIO",
    "NM_MUNICIPIO",
    "NR_ZONA",
    "NR_SECAO",
    "NR_LOCAL_VOTACAO",
    "QT_APTOS",
    "QT_COMPARECIMENTO",
    "QT_ABSTENCOES",
    "CD_TIPO_URNA",
    "DS_TIPO_URNA",
    "NR_URNA_EFETIVADA",
    "CD_CARGA_1_URNA_EFETIVADA",
    "CD_CARGA_2_URNA_EFETIVADA",
    "CD_FLASHCARD_URNA_EFETIVADA",
    "DS_AGREGADAS",
    "DT_ABERTURA",
    "DT_ENCERRAMENTO",
    "QT_ELEITORES_BIOMETRIA_NH",
    "DT_EMISSAO_BU",
    "DUPLICADO_ID_SECAO",
]

CARGO_MAP = {
    "Presidente": "PRES",
    "Governador": "GOV",
    "Senador": "SEN",
    "Deputado Federal": "DF",
    "Deputado Estadual": "DE",
    "Deputado Distrital": "DE",
}

USECOLS = [
    "SG_UF",
    "CD_MUNICIPIO",
    "NM_MUNICIPIO",
    "NR_ZONA",
    "NR_SECAO",
    "NR_LOCAL_VOTACAO",
    "CD_CARGO_PERGUNTA",
    "DS_CARGO_PERGUNTA",
    "NR_PARTIDO",
    "SG_PARTIDO",
    "NM_PARTIDO",
    "QT_APTOS",
    "QT_COMPARECIMENTO",
    "QT_ABSTENCOES",
    "CD_TIPO_URNA",
    "DS_TIPO_URNA",
    "DS_TIPO_VOTAVEL",
    "NR_VOTAVEL",
    "NM_VOTAVEL",
    "QT_VOTOS",
    "NR_URNA_EFETIVADA",
    "CD_CARGA_1_URNA_EFETIVADA",
    "CD_CARGA_2_URNA_EFETIVADA",
    "CD_FLASHCARD_URNA_EFETIVADA",
    "DS_AGREGADAS",
    "DT_ABERTURA",
    "DT_ENCERRAMENTO",
    "QT_ELEITORES_BIOMETRIA_NH",
    "DT_EMISSAO_BU",
    "NR_TURNO",
]

KEYS = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_LOCAL_VOTACAO"]


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {
        "header_real": None,
        "tipo_votavel": {},
        "tipo_urna": {},
        "outros_tipos": {},
        "ufs": {},
        "partidos": [],
        "candidatos": [],
    }


def save_manifest(m: dict) -> None:
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2, default=str))


def id_secao(uf, mun, zona, secao) -> str:
    return f"{uf}_{int(mun)}_{int(zona)}_{int(secao)}"


def partido_de_linha(nr_partido, nr_votavel) -> int | None:
    try:
        p = int(nr_partido)
        if p > 0:
            return p
    except Exception:
        pass
    try:
        v = int(nr_votavel)
        if v >= 10:
            return int(str(abs(v))[:2])
        if 0 < v < 10:
            return v
    except Exception:
        pass
    return None


def find_zip(turno: int, uf: str) -> Path | None:
    pats = list(DADOS.glob(f"bweb_{turno}t_{uf}_*.zip"))
    return pats[0] if pats else None


def extract_csv(zip_path: Path, dest: Path) -> Path:
    with zipfile.ZipFile(zip_path, "r") as zf:
        csvs = sorted(
            [n for n in zf.namelist() if n.lower().endswith(".csv")],
            key=lambda n: zf.getinfo(n).file_size,
            reverse=True,
        )
        name = csvs[0]
        zf.extract(name, dest)
        extracted = dest / name
        out = dest / Path(name).name
        if extracted != out:
            extracted.replace(out)
        return out


META_SRC = [
    "NM_MUNICIPIO",
    "QT_APTOS",
    "QT_COMPARECIMENTO",
    "QT_ABSTENCOES",
    "CD_TIPO_URNA",
    "DS_TIPO_URNA",
    "NR_URNA_EFETIVADA",
    "CD_CARGA_1_URNA_EFETIVADA",
    "CD_CARGA_2_URNA_EFETIVADA",
    "CD_FLASHCARD_URNA_EFETIVADA",
    "DS_AGREGADAS",
    "DT_ABERTURA",
    "DT_ENCERRAMENTO",
    "QT_ELEITORES_BIOMETRIA_NH",
    "DT_EMISSAO_BU",
    "NR_TURNO",
]


def _assign_vote_col(df: pd.DataFrame, turno: int, stats: dict) -> pd.Series:
    """Vetor de nomes de coluna de voto alinhado ao índice de df."""
    df = df.copy()
    df["cargo_cod"] = df["DS_CARGO_PERGUNTA"].map(CARGO_MAP)
    if turno == 2:
        df = df[df["cargo_cod"].isin(["PRES", "GOV"])]
    else:
        df = df[df["cargo_cod"].notna()]

    col = pd.Series(index=df.index, dtype=object)

    m = df["cargo_cod"] == "PRES"
    mn = m & (df["DS_TIPO_VOTAVEL"] == "Nominal")
    if mn.any():
        col.loc[mn] = "PRES_" + df.loc[mn, "NR_VOTAVEL"].astype(int).astype(str)
    for tipo, suf in (("Branco", "PRES_BRANCO"), ("Nulo", "PRES_NULO")):
        mt = m & (df["DS_TIPO_VOTAVEL"] == tipo)
        col.loc[mt] = suf
    mo = m & ~df["DS_TIPO_VOTAVEL"].isin(["Nominal", "Branco", "Nulo"])
    if mo.any():
        stats["outros_tipos"].update(df.loc[mo, "DS_TIPO_VOTAVEL"].astype(str))
        col.loc[mo] = "PRES_OUTROS_TIPOS"

    for cargo, pref in (("GOV", "GOV"), ("SEN", "SEN"), ("DF", "DF"), ("DE", "DE")):
        if turno == 2 and cargo in ("SEN", "DF", "DE"):
            continue
        m = df["cargo_cod"] == cargo
        if not m.any():
            continue
        mp = m & df["DS_TIPO_VOTAVEL"].isin(["Nominal", "Legenda"])
        if mp.any():
            pnum = [
                partido_de_linha(a, b)
                for a, b in zip(df.loc[mp, "NR_PARTIDO"], df.loc[mp, "NR_VOTAVEL"])
            ]
            pmap = {i: p for i, p in zip(df.index[mp], pnum) if p is not None}
            if pmap:
                idx = list(pmap.keys())
                col.loc[idx] = [f"{pref}_{pmap[i]}" for i in idx]
        for tipo, suf in (("Branco", f"{pref}_BRANCO"), ("Nulo", f"{pref}_NULO")):
            mt = m & (df["DS_TIPO_VOTAVEL"] == tipo)
            col.loc[mt] = suf
        mo = m & ~df["DS_TIPO_VOTAVEL"].isin(["Nominal", "Legenda", "Branco", "Nulo"])
        if mo.any():
            stats["outros_tipos"].update(df.loc[mo, "DS_TIPO_VOTAVEL"].astype(str))
            col.loc[mo] = f"{pref}_OUTROS_TIPOS"
    return col


def _finalize_wide(meta: pd.DataFrame, votos: pd.DataFrame, turno: int) -> pd.DataFrame:
    wide = votos.pivot_table(
        index=KEYS, columns="_col", values="QT_VOTOS", aggfunc="sum", fill_value=0
    ).reset_index()
    wide.columns.name = None
    out = meta.merge(wide, on=KEYS, how="outer")
    vote_cols = [c for c in out.columns if c not in KEYS and c not in META_SRC]
    for c in vote_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(np.int32)
    out = out.copy()
    out["ID_SECAO"] = [
        id_secao(u, m, z, s)
        for u, m, z, s in zip(
            out["SG_UF"], out["CD_MUNICIPIO"], out["NR_ZONA"], out["NR_SECAO"]
        )
    ]
    if "NR_TURNO" not in out.columns:
        out["NR_TURNO"] = turno
    else:
        out["NR_TURNO"] = pd.to_numeric(out["NR_TURNO"], errors="coerce").fillna(turno).astype(int)
    out["DUPLICADO_ID_SECAO"] = out["ID_SECAO"].duplicated(keep=False).astype(np.int8)
    return out


def wide_from_df(df: pd.DataFrame, turno: int) -> tuple[pd.DataFrame, dict]:
    stats = {
        "tipo_votavel": Counter(df["DS_TIPO_VOTAVEL"].astype(str)),
        "tipo_urna": Counter(df["DS_TIPO_URNA"].astype(str)),
        "outros_tipos": Counter(),
    }
    meta_src = [c for c in META_SRC if c in df.columns]
    meta = df.groupby(KEYS, as_index=False)[meta_src].first()
    col = _assign_vote_col(df, turno, stats)
    tmp = df.loc[col.dropna().index, KEYS + ["QT_VOTOS"]].copy()
    tmp["_col"] = col.dropna()
    votos = tmp.groupby(KEYS + ["_col"], as_index=False)["QT_VOTOS"].sum()
    return _finalize_wide(meta, votos, turno), stats


def wide_from_csv_chunked(csv_path: Path, cols: list[str], turno: int, chunksize: int = 400_000) -> tuple[pd.DataFrame, dict]:
    """Para SP/MG: agrega votos e metadados em pedaços sem carregar o CSV inteiro."""
    stats = {"tipo_votavel": Counter(), "tipo_urna": Counter(), "outros_tipos": Counter(), "n_linhas": 0}
    meta_parts = []
    vote_parts = []
    num_cols = [
        "CD_MUNICIPIO",
        "NR_ZONA",
        "NR_SECAO",
        "NR_LOCAL_VOTACAO",
        "NR_PARTIDO",
        "NR_VOTAVEL",
        "QT_VOTOS",
        "QT_APTOS",
        "QT_COMPARECIMENTO",
        "QT_ABSTENCOES",
        "NR_TURNO",
        "CD_TIPO_URNA",
        "NR_URNA_EFETIVADA",
        "QT_ELEITORES_BIOMETRIA_NH",
    ]
    reader = pd.read_csv(
        csv_path,
        sep=";",
        encoding="latin-1",
        usecols=cols,
        chunksize=chunksize,
        low_memory=True,
    )
    for i, chunk in enumerate(reader):
        stats["n_linhas"] += len(chunk)
        for c in num_cols:
            if c in chunk.columns:
                chunk[c] = pd.to_numeric(chunk[c], errors="coerce")
        stats["tipo_votavel"].update(chunk["DS_TIPO_VOTAVEL"].astype(str))
        stats["tipo_urna"].update(chunk["DS_TIPO_URNA"].astype(str))
        meta_src = [c for c in META_SRC if c in chunk.columns]
        meta_parts.append(chunk.groupby(KEYS, as_index=False)[meta_src].first())
        col = _assign_vote_col(chunk, turno, stats)
        tmp = chunk.loc[col.dropna().index, KEYS + ["QT_VOTOS"]].copy()
        tmp["_col"] = col.dropna().astype(str)
        vote_parts.append(tmp.groupby(KEYS + ["_col"], as_index=False)["QT_VOTOS"].sum())
        print(f"    chunk {i+1} linhas={len(chunk):,}", flush=True)
        del chunk, tmp, col

    meta = pd.concat(meta_parts, ignore_index=True)
    meta = meta.groupby(KEYS, as_index=False).first()
    votos = pd.concat(vote_parts, ignore_index=True)
    votos = votos.groupby(KEYS + ["_col"], as_index=False)["QT_VOTOS"].sum()
    return _finalize_wide(meta, votos, turno), stats


def process_one(turno: int, uf: str, manifest: dict) -> dict:
    key = f"{uf}_{turno}t"
    out_pq = POR_UF / f"{uf.lower()}_{turno}t.parquet"
    if out_pq.exists() and manifest.get("ufs", {}).get(key, {}).get("status") == "ok":
        print(f"  skip {key} (já ok)")
        return manifest

    zp = find_zip(turno, uf)
    if zp is None:
        print(f"  sem zip {key}")
        return manifest

    tmp = Path(tempfile.mkdtemp(prefix=f"bu_{uf}_{turno}_"))
    try:
        print(f"  processando {zp.name} …")
        csv_path = extract_csv(zp, tmp)
        header = pd.read_csv(csv_path, sep=";", encoding="latin-1", nrows=0).columns.tolist()
        cols = [c for c in USECOLS if c in header]
        csv_mb = csv_path.stat().st_size / 1e6
        if csv_mb >= 800:  # SP/MG-class: leitura em pedaços
            print(f"  CSV {csv_mb:.0f} MB → modo chunked")
            wide, stats = wide_from_csv_chunked(csv_path, cols, turno)
            # partidos/candidatos: amostra via segundo passe leve só dessas colunas
            part_cols = [c for c in ["NR_PARTIDO", "SG_PARTIDO", "NM_PARTIDO"] if c in header]
            cand_cols = [
                c
                for c in [
                    "SG_UF",
                    "NR_TURNO",
                    "DS_CARGO_PERGUNTA",
                    "NR_VOTAVEL",
                    "NM_VOTAVEL",
                    "NR_PARTIDO",
                    "SG_PARTIDO",
                    "DS_TIPO_VOTAVEL",
                ]
                if c in header
            ]
            part = pd.DataFrame()
            cand = pd.DataFrame()
            for chunk in pd.read_csv(
                csv_path, sep=";", encoding="latin-1", usecols=list(set(part_cols + cand_cols)),
                chunksize=500_000, low_memory=True,
            ):
                if part_cols:
                    p = chunk[part_cols].dropna(subset=["NR_PARTIDO"]).drop_duplicates()
                    p["NR_PARTIDO"] = pd.to_numeric(p["NR_PARTIDO"], errors="coerce")
                    p = p[p["NR_PARTIDO"] > 0]
                    part = pd.concat([part, p], ignore_index=True)
                if set(cand_cols) <= set(chunk.columns):
                    c = chunk[
                        chunk["DS_CARGO_PERGUNTA"].isin(["Governador", "Senador"])
                        & (chunk["DS_TIPO_VOTAVEL"] == "Nominal")
                    ][[x for x in cand_cols if x != "DS_TIPO_VOTAVEL"]].drop_duplicates()
                    c = c.rename(columns={"DS_CARGO_PERGUNTA": "cargo"})
                    cand = pd.concat([cand, c], ignore_index=True)
            part = part.drop_duplicates()
            cand = cand.drop_duplicates()
            n_linhas_bu = int(stats.get("n_linhas", 0))
        else:
            df = pd.read_csv(
                csv_path,
                sep=";",
                encoding="latin-1",
                usecols=cols,
                low_memory=False,
            )
            for c in [
                "CD_MUNICIPIO",
                "NR_ZONA",
                "NR_SECAO",
                "NR_LOCAL_VOTACAO",
                "NR_PARTIDO",
                "NR_VOTAVEL",
                "QT_VOTOS",
                "QT_APTOS",
                "QT_COMPARECIMENTO",
                "QT_ABSTENCOES",
                "NR_TURNO",
                "CD_TIPO_URNA",
                "NR_URNA_EFETIVADA",
                "QT_ELEITORES_BIOMETRIA_NH",
            ]:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")

            wide, stats = wide_from_df(df, turno)
            part = (
                df[["NR_PARTIDO", "SG_PARTIDO", "NM_PARTIDO"]]
                .dropna(subset=["NR_PARTIDO"])
                .drop_duplicates()
            )
            part["NR_PARTIDO"] = pd.to_numeric(part["NR_PARTIDO"], errors="coerce")
            part = part[part["NR_PARTIDO"] > 0]
            cand = df[
                df["DS_CARGO_PERGUNTA"].isin(["Governador", "Senador"])
                & (df["DS_TIPO_VOTAVEL"] == "Nominal")
            ][
                [
                    "SG_UF",
                    "NR_TURNO",
                    "DS_CARGO_PERGUNTA",
                    "NR_VOTAVEL",
                    "NM_VOTAVEL",
                    "NR_PARTIDO",
                    "SG_PARTIDO",
                ]
            ].drop_duplicates()
            cand = cand.rename(columns={"DS_CARGO_PERGUNTA": "cargo"})
            n_linhas_bu = len(df)
            del df

        wide.to_parquet(out_pq, index=False)

        if manifest.get("header_real") is None:
            manifest["header_real"] = header

        def _acc(dest: str, counter: Counter):
            d = manifest.setdefault(dest, {})
            for k, v in counter.items():
                d[k] = d.get(k, 0) + int(v)

        _acc("tipo_votavel", stats["tipo_votavel"])
        _acc("tipo_urna", stats["tipo_urna"])
        _acc("outros_tipos", stats["outros_tipos"])

        for rec in part.to_dict(orient="records"):
            rec["NR_PARTIDO"] = int(rec["NR_PARTIDO"])
            if not any(
                p.get("NR_PARTIDO") == rec["NR_PARTIDO"]
                and p.get("SG_PARTIDO") == rec["SG_PARTIDO"]
                for p in manifest["partidos"]
            ):
                manifest["partidos"].append(rec)

        for rec in cand.to_dict(orient="records"):
            manifest["candidatos"].append(rec)

        vote_cols = [
            c
            for c in wide.columns
            if c.startswith(("PRES_", "GOV_", "SEN_", "DF_", "DE_"))
        ]
        manifest.setdefault("ufs", {})[key] = {
            "status": "ok",
            "arquivo": zp.name,
            "n_secoes": int(len(wide)),
            "n_linhas_bu": int(n_linhas_bu),
            "n_duplicados": int((wide["DUPLICADO_ID_SECAO"] == 1).sum()),
            "vote_cols": vote_cols,
            "parquet": str(out_pq.relative_to(OUT)),
            "pres_13": int(wide["PRES_13"].sum()) if "PRES_13" in wide.columns else 0,
            "pres_22": int(wide["PRES_22"].sum()) if "PRES_22" in wide.columns else 0,
        }
        save_manifest(manifest)
        print(
            f"  → {key} seções={len(wide)} dup={manifest['ufs'][key]['n_duplicados']} "
            f"cols_voto={len(vote_cols)} ({out_pq.stat().st_size/1e6:.1f} MB)"
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return manifest


def order_vote_cols(cols: list[str]) -> list[str]:
    def key(c: str):
        m = re.match(r"^(PRES|GOV|SEN|DF|DE)_(.+)$", c)
        if not m:
            return (9, c)
        pref = {"PRES": 0, "GOV": 1, "SEN": 2, "DF": 3, "DE": 4}[m.group(1)]
        rest = m.group(2)
        if rest == "BRANCO":
            return (pref, 9000, rest)
        if rest == "NULO":
            return (pref, 9001, rest)
        if rest == "OUTROS_TIPOS":
            return (pref, 9002, rest)
        try:
            return (pref, int(rest), rest)
        except ValueError:
            return (pref, 8000, rest)

    return sorted(cols, key=key)


def finalize(turno: int, manifest: dict) -> None:
    print(f"\n=== finalizando turno {turno} ===")
    keys = sorted(
        k for k, v in manifest.get("ufs", {}).items() if k.endswith(f"_{turno}t") and v.get("status") == "ok"
    )
    if not keys:
        print("  nada a concatenar")
        return

    all_votes = sorted(
        {
            c
            for k in keys
            for c in manifest["ufs"][k].get("vote_cols", [])
        }
    )
    all_votes = order_vote_cols(all_votes)
    schema = META_COLS + all_votes
    print(f"  UFs={len(keys)} colunas={len(schema)}")

    frames = []
    for k in keys:
        pq = OUT / manifest["ufs"][k]["parquet"]
        df = pd.read_parquet(pq)
        # alinhar schema sem inserts fragmentados
        missing = [c for c in schema if c not in df.columns]
        if missing:
            add = pd.DataFrame(
                {
                    c: (
                        0
                        if c.startswith(("PRES_", "GOV_", "SEN_", "DF_", "DE_"))
                        or c == "DUPLICADO_ID_SECAO"
                        else pd.NA
                    )
                    for c in missing
                },
                index=df.index,
            )
            df = pd.concat([df, add], axis=1)
        df = df.reindex(columns=schema)
        frames.append(df)
        del df

    full = pd.concat(frames, ignore_index=True)
    del frames
    for c in all_votes:
        full[c] = pd.to_numeric(full[c], errors="coerce").fillna(0).astype(np.int32)

    # metadados problemáticos (cargas com pontos) → string
    for c in (
        "CD_CARGA_1_URNA_EFETIVADA",
        "CD_CARGA_2_URNA_EFETIVADA",
        "CD_FLASHCARD_URNA_EFETIVADA",
        "DS_AGREGADAS",
        "DS_TIPO_URNA",
        "NM_MUNICIPIO",
        "DT_ABERTURA",
        "DT_ENCERRAMENTO",
        "DT_EMISSAO_BU",
        "ID_SECAO",
        "SG_UF",
    ):
        if c in full.columns:
            full[c] = full[c].astype("string")

    pq_out = OUT / f"secoes_2022_t{turno}.parquet"
    full.to_parquet(pq_out, index=False)
    print(f"  parquet {pq_out.stat().st_size/1e6:.1f} MB  linhas={len(full)}")

    gz = OUT / f"secoes_2022_t{turno}.csv.gz"
    full.to_csv(gz, sep=";", index=False, encoding="utf-8", compression="gzip")
    print(f"  csv.gz  {gz.stat().st_size/1e6:.1f} MB")

    # validação
    rep = {
        "n_secoes": int(len(full)),
        "n_id_unicos": int(full["ID_SECAO"].nunique()),
        "n_duplicados_flag": int((full["DUPLICADO_ID_SECAO"] == 1).sum()),
        "secoes_por_uf": {str(k): int(v) for k, v in full.groupby("SG_UF").size().items()},
        "total_Lula": int(full["PRES_13"].sum()) if "PRES_13" in full.columns else 0,
        "total_Bolsonaro": int(full["PRES_22"].sum()) if "PRES_22" in full.columns else 0,
    }
    prefixes = ["PRES", "GOV"] if turno == 2 else ["PRES", "GOV", "SEN", "DF", "DE"]
    div_frames = []
    for pref in prefixes:
        cols = [c for c in all_votes if c.startswith(pref + "_")]
        if not cols:
            continue
        soma = full[cols].sum(axis=1)
        diff = soma - full["QT_COMPARECIMENTO"].astype(float)
        bad = diff != 0
        rep[f"divergencias_{pref}"] = int(bad.sum())
        if bad.any():
            sample = full.loc[bad, ["ID_SECAO", "SG_UF", "QT_COMPARECIMENTO"]].head(30).copy()
            sample["soma_cargo"] = soma[bad].values[: len(sample)]
            sample["diff"] = diff[bad].values[: len(sample)]
            sample["cargo"] = pref
            div_frames.append(sample)

    (OUT / f"validacao_t{turno}.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2)
    )
    pd.DataFrame(
        [{"SG_UF": u, "NR_TURNO": turno, "n_secoes": n} for u, n in rep["secoes_por_uf"].items()]
    ).to_csv(OUT / f"secoes_por_uf_t{turno}.csv", sep=";", index=False, encoding="utf-8")

    if div_frames:
        pd.concat(div_frames, ignore_index=True).to_csv(
            OUT / f"divergencias_comparecimento_t{turno}.csv",
            sep=";",
            index=False,
            encoding="utf-8",
        )

    # totais por UF × coluna (amostra útil, não explode: só PRES + agregados)
    tot_rows = []
    for c in all_votes:
        if not c.startswith(("PRES_", "GOV_", "SEN_", "DF_", "DE_")):
            continue
        cargo = c.split("_", 1)[0]
        g = full.groupby("SG_UF", observed=True)[c].sum()
        for uf, val in g.items():
            if val == 0:
                continue
            tot_rows.append(
                {
                    "SG_UF": uf,
                    "NR_TURNO": turno,
                    "cargo": cargo,
                    "coluna": c,
                    "partido_ou_candidato": c.split("_", 1)[1],
                    "total_votos": int(val),
                }
            )
    pd.DataFrame(tot_rows).to_csv(
        OUT / f"validacao_totais_t{turno}.csv", sep=";", index=False, encoding="utf-8"
    )
    print(
        f"  validação: seções={rep['n_secoes']} Lula={rep['total_Lula']:,} "
        f"Bolso={rep['total_Bolsonaro']:,}"
    )
    del full


def write_aux(manifest: dict) -> None:
    part = pd.DataFrame(manifest.get("partidos", []))
    if len(part):
        part["federacao"] = ""
        part = part.drop_duplicates(subset=["NR_PARTIDO", "SG_PARTIDO"]).sort_values("NR_PARTIDO")
        part.to_csv(OUT / "dicionario_partidos.csv", sep=";", index=False, encoding="utf-8")

    cand = pd.DataFrame(manifest.get("candidatos", []))
    if len(cand):
        cand = cand.drop_duplicates()
        cand.to_csv(OUT / "candidatos_gov_sen.csv", sep=";", index=False, encoding="utf-8")

    # sqlite
    import sqlite3

    db = OUT / "bu2022.sqlite"
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    for turno in (1, 2):
        pq = OUT / f"secoes_2022_t{turno}.parquet"
        if not pq.exists():
            continue
        t = pd.read_parquet(pq)
        t.to_sql(f"t{turno}", con, index=False, if_exists="replace")
        con.execute(f"CREATE INDEX IF NOT EXISTS ix_t{turno}_id ON t{turno}(ID_SECAO)")
        con.execute(f"CREATE INDEX IF NOT EXISTS ix_t{turno}_uf ON t{turno}(SG_UF)")
        del t
    con.close()
    zpath = OUT / "bu2022.sqlite.zip"
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(db, arcname="bu2022.sqlite")
    print(f"sqlite zip {zpath.stat().st_size/1e6:.1f} MB")


def write_readme(manifest: dict) -> None:
    v1 = json.loads((OUT / "validacao_t1.json").read_text()) if (OUT / "validacao_t1.json").exists() else {}
    v2 = json.loads((OUT / "validacao_t2.json").read_text()) if (OUT / "validacao_t2.json").exists() else {}
    header = manifest.get("header_real") or []
    tv = manifest.get("tipo_votavel", {})
    tu = manifest.get("tipo_urna", {})
    ot = manifest.get("outros_tipos", {})
    ref = {
        1: {"Lula": 57259504, "Bolsonaro": 51072345},
        2: {"Lula": 60345999, "Bolsonaro": 58206354},
    }
    lines = [
        "# Base de seções — Boletim de Urna TSE 2022",
        "",
        "Gerada por `scripts/gerar_base_secoes.py` (parquet por UF + concatenação).",
        "",
        "## Cabeçalho real",
        "",
        "Codificação: **latin-1**. Separador: **`;`**.",
        "",
        f"Colunas ({len(header)}):",
        "",
        "```",
        "\n".join(header),
        "```",
        "",
        "## DS_TIPO_VOTAVEL",
        "",
        "| Valor | Ocorrências |",
        "|-------|------------:|",
    ]
    for k, v in sorted(tv.items(), key=lambda x: -x[1]):
        lines.append(f"| {k} | {v} |")
    lines += [
        "",
        f"Outros tipos → `*_OUTROS_TIPOS`: {ot or '(nenhum)'}.",
        "",
        "## DS_TIPO_URNA",
        "",
        "| Valor | Ocorrências |",
        "|-------|------------:|",
    ]
    for k, v in sorted(tu.items(), key=lambda x: -x[1]):
        lines.append(f"| {k} | {v} |")
    lines += [
        "",
        "## Chave",
        "",
        "`ID_SECAO = SG_UF_CD_MUNICIPIO_NR_ZONA_NR_SECAO` (inteiros sem zero à esquerda).",
        "`NR_LOCAL_VOTACAO` nos metadados. Duplicados de ID (locais distintos) mantidos com `DUPLICADO_ID_SECAO=1`.",
        "",
        "## Arquivos",
        "",
        "| Arquivo | Descrição |",
        "|---------|-----------|",
        "| `secoes_2022_t1.csv.gz` / `_t2.csv.gz` | base larga |",
        "| `secoes_2022_t1.parquet` / `_t2.parquet` | idem |",
        "| `por_uf/*.parquet` | checkpoint por UF |",
        "| `bu2022.sqlite.zip` | tabelas t1/t2 |",
        "| `dicionario_partidos.csv` | partidos |",
        "| `candidatos_gov_sen.csv` | Gov/Sen nominais |",
        "| `validacao_totais_t*.csv` | totais UF×coluna |",
        "| `manifesto.json` | status por UF |",
        "",
        "## Validação",
        "",
        "### Soma cargo = QT_COMPARECIMENTO",
        "",
        "| Turno | Cargo | Divergências |",
        "|------:|-------|-------------:|",
    ]
    for t, v in ((1, v1), (2, v2)):
        for pref in ("PRES", "GOV", "SEN", "DF", "DE"):
            if f"divergencias_{pref}" in v:
                lines.append(f"| {t} | {pref} | {v[f'divergencias_{pref}']} |")
    lines += [
        "",
        "### Totais presidente",
        "",
        "| Turno | Candidato | Referência | Base | Diff |",
        "|------:|-----------|----------:|-----:|-----:|",
    ]
    for t, v in ((1, v1), (2, v2)):
        for nome, col in (("Lula", "total_Lula"), ("Bolsonaro", "total_Bolsonaro")):
            base = v.get(col, 0)
            r = ref[t][nome]
            lines.append(f"| {t} | {nome} | {r:,} | {base:,} | {base - r:,} |")
    lines += [
        "",
        "### Seções",
        "",
        "| Turno | Linhas | ID únicos | Flag duplicado |",
        "|------:|-------:|----------:|---------------:|",
        f"| 1 | {v1.get('n_secoes','—')} | {v1.get('n_id_unicos','—')} | {v1.get('n_duplicados_flag','—')} |",
        f"| 2 | {v2.get('n_secoes','—')} | {v2.get('n_id_unicos','—')} | {v2.get('n_duplicados_flag','—')} |",
        "",
        "Referência VOTOS_T1E2: 472.027 seções. Modelo de urna não incluso (cruzar por ID_SECAO).",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print("README ok")


def list_ufs(turno: int) -> list[str]:
    ufs = sorted({p.name.split("_")[2] for p in DADOS.glob(f"bweb_{turno}t_*.zip")})
    # processar grandes por último
    late = [u for u in ("RJ", "BA", "MG", "SP") if u in ufs]
    early = [u for u in ufs if u not in late]
    return early + late


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--uf", default=None)
    ap.add_argument("--turno", type=int, default=None)
    ap.add_argument("--so-final", action="store_true")
    args = ap.parse_args()

    manifest = load_manifest()

    if not args.so_final:
        turnos = [args.turno] if args.turno else [1, 2]
        for turno in turnos:
            ufs = [args.uf] if args.uf else list_ufs(turno)
            print(f"\n=== turno {turno}: {len(ufs)} UFs ===")
            for uf in ufs:
                manifest = process_one(turno, uf, manifest)

    # finalizar só se todos os zips do turno estiverem ok
    for turno in (1, 2):
        expected = set(list_ufs(turno))
        done = {
            k.split("_")[0]
            for k, v in manifest.get("ufs", {}).items()
            if k.endswith(f"_{turno}t") and v.get("status") == "ok"
        }
        missing = expected - done
        if missing and not args.so_final:
            print(f"turno {turno}: faltam {sorted(missing)} — não finalizo ainda")
            continue
        if not done:
            continue
        finalize(turno, manifest)

    if (OUT / "secoes_2022_t1.parquet").exists() and (OUT / "secoes_2022_t2.parquet").exists():
        write_aux(manifest)
        write_readme(manifest)
    save_manifest(manifest)
    print("fim")


if __name__ == "__main__":
    main()
