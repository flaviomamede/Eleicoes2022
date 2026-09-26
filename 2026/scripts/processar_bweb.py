#!/usr/bin/env python3
"""Processa Boletim de Urna Web (TSE) → artefatos compactos por seção.

Uso:
  python scripts/processar_bweb.py dados/bweb_1t_AC_051020221321.zip --turno 1 --uf AC
  # ou importar:
  from processar_bweb import process_zip
  process_zip(path_zip, turno=1, uf='AC')
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DADOS = ROOT / "dados"
BUWEB = DADOS / "buweb"
ANALISE = ROOT / "analise"
URNAS_PARQUET = DADOS / "urnas_pres_gov.parquet"

COLS_BU = [
    "SG_UF",
    "CD_MUNICIPIO",
    "NM_MUNICIPIO",
    "NR_ZONA",
    "NR_SECAO",
    "NR_LOCAL_VOTACAO",
    "DS_CARGO_PERGUNTA",
    "NR_PARTIDO",
    "SG_PARTIDO",
    "NM_PARTIDO",
    "QT_APTOS",
    "QT_COMPARECIMENTO",
    "QT_ABSTENCOES",
    "DS_TIPO_VOTAVEL",
    "NR_VOTAVEL",
    "NM_VOTAVEL",
    "QT_VOTOS",
]

CARGOS_PARTIDO = {
    "Governador",
    "Senador",
    "Deputado Federal",
    "Deputado Estadual",
    "Deputado Distrital",
}


def _extract_csv(path_zip: Path, extract_dir: Path) -> Path:
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path_zip, "r") as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            raise FileNotFoundError(f"Nenhum CSV em {path_zip}")
        # Preferir o maior CSV (boletim); ignorar extras se houver
        csv_names.sort(key=lambda n: zf.getinfo(n).file_size, reverse=True)
        target = csv_names[0]
        out = extract_dir / Path(target).name
        if not out.exists() or out.stat().st_size != zf.getinfo(target).file_size:
            zf.extract(target, extract_dir)
            extracted = extract_dir / target
            if extracted != out:
                extracted.rename(out)
        return out


def _chave_secao(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out.rename(
        columns={
            "SG_UF": "uf",
            "CD_MUNICIPIO": "municipio",
            "NM_MUNICIPIO": "nm_municipio",
            "NR_ZONA": "zona",
            "NR_SECAO": "secao",
            "NR_LOCAL_VOTACAO": "local",
            "DS_CARGO_PERGUNTA": "cargo",
            "NR_PARTIDO": "nr_partido",
            "SG_PARTIDO": "sg_partido",
            "NM_PARTIDO": "nm_partido",
            "DS_TIPO_VOTAVEL": "tipo_votavel",
            "NR_VOTAVEL": "nr_votavel",
            "NM_VOTAVEL": "nm_votavel",
            "QT_VOTOS": "qt_votos",
            "QT_APTOS": "qt_aptos",
            "QT_COMPARECIMENTO": "qt_comparecimento",
            "QT_ABSTENCOES": "qt_abstencoes",
        }
    )
    for c in ("municipio", "zona", "secao", "local", "nr_partido", "nr_votavel", "qt_votos"):
        out[c] = pd.to_numeric(out[c], errors="coerce").astype("Int64")
    return out


def _agregar_partidos(df: pd.DataFrame) -> pd.DataFrame:
    """Seção × cargo × partido (Nominal+Legenda) + Branco/Nulo."""
    leg = df[df["cargo"].isin(CARGOS_PARTIDO)].copy()
    if leg.empty:
        return pd.DataFrame()

    part = (
        leg[leg["tipo_votavel"].isin(["Nominal", "Legenda"])]
        .groupby(
            ["uf", "municipio", "nm_municipio", "zona", "secao", "local", "cargo", "nr_partido", "sg_partido"],
            as_index=False,
        )["qt_votos"]
        .sum()
    )
    part["tipo_votavel"] = "Partido"
    part["nr_votavel"] = -1
    part["nm_votavel"] = ""

    bn = (
        leg[leg["tipo_votavel"].isin(["Branco", "Nulo"])]
        .groupby(
            [
                "uf",
                "municipio",
                "nm_municipio",
                "zona",
                "secao",
                "local",
                "cargo",
                "tipo_votavel",
                "nr_votavel",
                "nm_votavel",
            ],
            as_index=False,
        )["qt_votos"]
        .sum()
    )
    bn["nr_partido"] = -1
    bn["sg_partido"] = bn["tipo_votavel"]

    cols = [
        "uf",
        "municipio",
        "nm_municipio",
        "zona",
        "secao",
        "local",
        "cargo",
        "tipo_votavel",
        "nr_partido",
        "sg_partido",
        "nr_votavel",
        "nm_votavel",
        "qt_votos",
    ]
    return pd.concat([part[cols], bn[cols]], ignore_index=True)


def _agregar_presidente(df: pd.DataFrame) -> pd.DataFrame:
    """Seção × NR_VOTAVEL (candidatos + branco/nulo)."""
    pres = df[df["cargo"] == "Presidente"].copy()
    if pres.empty:
        return pd.DataFrame()

    g = (
        pres.groupby(
            [
                "uf",
                "municipio",
                "nm_municipio",
                "zona",
                "secao",
                "local",
                "cargo",
                "tipo_votavel",
                "nr_partido",
                "sg_partido",
                "nr_votavel",
                "nm_votavel",
            ],
            as_index=False,
        )["qt_votos"]
        .sum()
    )
    return g


def _meta_secao(df: pd.DataFrame) -> pd.DataFrame:
    keys = ["uf", "municipio", "nm_municipio", "zona", "secao", "local"]
    meta = (
        df.groupby(keys, as_index=False)
        .agg(
            qt_aptos=("qt_aptos", "first"),
            qt_comparecimento=("qt_comparecimento", "first"),
            qt_abstencoes=("qt_abstencoes", "first"),
        )
    )
    return meta


def _presidente_largo(pres_long: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por seção com totais de presidente por número + branco/nulo."""
    if pres_long.empty:
        return pd.DataFrame()
    keys = ["uf", "municipio", "nm_municipio", "zona", "secao", "local"]
    piv = (
        pres_long.pivot_table(
            index=keys,
            columns="nr_votavel",
            values="qt_votos",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )
    ren = {}
    for c in piv.columns:
        if c in keys:
            continue
        n = int(c)
        if n == 95:
            ren[c] = "vPres_branco"
        elif n == 96:
            ren[c] = "vPres_nulo"
        else:
            ren[c] = f"vPres_{n}"
    piv = piv.rename(columns=ren)
    # totais conhecidos
    for col, alias in (("vPres_22", "vPres_bolsonaro"), ("vPres_13", "vPres_lula")):
        if col in piv.columns:
            piv[alias] = piv[col]
    vote_cols = [c for c in piv.columns if c.startswith("vPres_")]
    piv["vPres_total"] = piv[vote_cols].sum(axis=1)
    return piv


def _carregar_modelo(turno: int, uf: str) -> pd.DataFrame:
    if not URNAS_PARQUET.exists():
        raise FileNotFoundError(f"Ausente: {URNAS_PARQUET}")
    urnas = pd.read_parquet(URNAS_PARQUET)
    m = urnas[(urnas["turno"] == turno) & (urnas["estado"] == uf.upper())].copy()
    cols = [
        "municipio",
        "zona",
        "secao",
        "local",
        "modelUrna",
        "marca",
        "grupo_urna",
        "vPresA22",
        "vPresB13",
        "vPresC15",
        "vPresD12",
        "vPresNulo",
        "vPresBranco",
    ]
    available = [c for c in cols if c in m.columns]
    return m[available].copy()


def _validar_join(
    secao: pd.DataFrame, modelo: pd.DataFrame
) -> tuple[pd.DataFrame, dict]:
    """Cruza BU × modelo; reporta cobertura e diferença de totais presidente."""
    join_keys = ["municipio", "zona", "secao"]
    # local se necessário (1:1 no AC; mantém se existir nos dois)
    if "local" in secao.columns and "local" in modelo.columns:
        # tenta sem local primeiro; se cobertura piorar com ambiguidade, usa local
        pass

    merged = secao.merge(modelo, on=join_keys, how="left", suffixes=("", "_mod"))
    if "local_mod" in merged.columns:
        # se local diverge, preferir o do BU
        merged = merged.drop(columns=["local_mod"], errors="ignore")

    n_sec = len(secao)
    n_join = int(merged["modelUrna"].notna().sum()) if "modelUrna" in merged.columns else 0
    pct = 100.0 * n_join / n_sec if n_sec else 0.0

    bu22 = float(merged.get("vPres_22", merged.get("vPres_bolsonaro", pd.Series([0]))).sum())
    bu13 = float(merged.get("vPres_13", merged.get("vPres_lula", pd.Series([0]))).sum())
    jr22 = float(merged["vPresA22"].fillna(0).sum()) if "vPresA22" in merged.columns else float("nan")
    jr13 = float(merged["vPresB13"].fillna(0).sum()) if "vPresB13" in merged.columns else float("nan")

    # correlação seção a seção (onde há join)
    ok = merged["modelUrna"].notna() if "modelUrna" in merged.columns else pd.Series(False, index=merged.index)
    corr22 = corr13 = float("nan")
    if ok.any() and "vPres_22" in merged.columns and "vPresA22" in merged.columns:
        corr22 = float(merged.loc[ok, "vPres_22"].corr(merged.loc[ok, "vPresA22"]))
        corr13 = float(merged.loc[ok, "vPres_13"].corr(merged.loc[ok, "vPresB13"]))

    dif22 = bu22 - jr22
    dif13 = bu13 - jr13

    stats = {
        "n_secoes": n_sec,
        "n_join": n_join,
        "pct_join": pct,
        "bu_bolsonaro": bu22,
        "bu_lula": bu13,
        "jr_bolsonaro": jr22,
        "jr_lula": jr13,
        "dif_bolsonaro": dif22,
        "dif_lula": dif13,
        "corr_bolsonaro": corr22,
        "corr_lula": corr13,
        "cargos": [],
    }
    return merged, stats


def _fmt_int(x: float | int) -> str:
    return f"{int(round(x)):,}".replace(",", ".")


def _escrever_validacao(
    path: Path,
    uf: str,
    turno: int,
    stats: dict,
    cargos: list[str],
    path_partido: Path,
    path_secao: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    linhas = [
        f"# Validação BU Web — {uf} {turno}º turno",
        "",
        f"Fonte processada via `scripts/processar_bweb.py`.",
        "",
        "## Seções e cobertura",
        "",
        f"- Seções no boletim: **{_fmt_int(stats['n_secoes'])}**",
        f"- Join com modelo de urna (`urnas_pres_gov.parquet`, turno={turno}, estado={uf}): "
        f"**{_fmt_int(stats['n_join'])}** ({stats['pct_join']:.1f}%)",
        "",
        "## Presidente — totais BU vs base John",
        "",
        "| Candidato | BU Web | Base John | Diferença | Correlação (seção) |",
        "|-----------|--------|-----------|-----------|--------------------|",
        f"| Bolsonaro (22) | {_fmt_int(stats['bu_bolsonaro'])} | {_fmt_int(stats['jr_bolsonaro'])} | "
        f"{_fmt_int(stats['dif_bolsonaro'])} | {stats['corr_bolsonaro']:.6f} |",
        f"| Lula (13) | {_fmt_int(stats['bu_lula'])} | {_fmt_int(stats['jr_lula'])} | "
        f"{_fmt_int(stats['dif_lula'])} | {stats['corr_lula']:.6f} |",
        "",
        "## Cargos disponíveis no BU",
        "",
    ]
    for c in cargos:
        linhas.append(f"- {c}")
    linhas += [
        "",
        "## Artefatos",
        "",
        f"- `{path_partido.relative_to(ROOT)}` — longo (seção × cargo × partido/votável)",
        f"- `{path_secao.relative_to(ROOT)}` — largo (seção + presidente + modelo de urna)",
        "",
    ]
    path.write_text("\n".join(linhas), encoding="utf-8")


def process_zip(
    path_zip: str | Path,
    turno: int,
    uf: str,
    *,
    extract_dir: str | Path | None = None,
    cleanup_csv: bool = True,
) -> dict:
    """Processa um zip de BU Web e grava parquet + validação.

    Retorna dicionário com caminhos e estatísticas de validação.
    """
    path_zip = Path(path_zip)
    uf = uf.upper()
    BUWEB.mkdir(parents=True, exist_ok=True)
    ANALISE.mkdir(parents=True, exist_ok=True)

    tmp_owned = False
    if extract_dir is None:
        extract_dir = Path(tempfile.mkdtemp(prefix=f"bu_{uf.lower()}_"))
        tmp_owned = True
    else:
        extract_dir = Path(extract_dir)

    csv_path = _extract_csv(path_zip, extract_dir)

    bu = pd.read_csv(csv_path, sep=";", encoding="latin-1", usecols=COLS_BU)
    bu = _chave_secao(bu)

    # filtrar UF/turno se o arquivo trouxer outros (raro)
    if "uf" in bu.columns:
        bu = bu[bu["uf"].astype(str).str.upper() == uf]

    cargos = sorted(bu["cargo"].dropna().unique().tolist())
    partido_long = _agregar_partidos(bu)
    pres_long = _agregar_presidente(bu)
    longo = pd.concat([partido_long, pres_long], ignore_index=True)

    meta = _meta_secao(bu)
    pres_wide = _presidente_largo(pres_long)
    secao = meta.merge(pres_wide, on=["uf", "municipio", "nm_municipio", "zona", "secao", "local"], how="left")

    modelo = _carregar_modelo(turno, uf)
    secao_m, stats = _validar_join(secao, modelo)
    stats["cargos"] = cargos

    # dtypes compactos
    for c in ("municipio", "zona", "secao", "local"):
        if c in longo.columns:
            longo[c] = pd.to_numeric(longo[c], errors="coerce").astype("int32")
        if c in secao_m.columns:
            secao_m[c] = pd.to_numeric(secao_m[c], errors="coerce").astype("int32")
    if "qt_votos" in longo.columns:
        longo["qt_votos"] = pd.to_numeric(longo["qt_votos"], errors="coerce").fillna(0).astype("int32")

    uf_l = uf.lower()
    path_partido = BUWEB / f"{uf_l}_{turno}t_partido_secao.parquet"
    path_secao = BUWEB / f"{uf_l}_{turno}t_secao.parquet"
    path_val = ANALISE / f"{uf_l}_{turno}t_validacao.md"

    longo.to_parquet(path_partido, index=False)
    secao_m.to_parquet(path_secao, index=False)
    _escrever_validacao(path_val, uf, turno, stats, cargos, path_partido, path_secao)

    if cleanup_csv:
        try:
            size_mb = csv_path.stat().st_size / (1024 * 1024)
            if size_mb > 50 or tmp_owned:
                csv_path.unlink(missing_ok=True)
                # se diretório ficou só com PDF/leiame, pode limpar o tmp criado
                if tmp_owned:
                    shutil.rmtree(extract_dir, ignore_errors=True)
        except OSError:
            pass

    return {
        "path_partido": str(path_partido),
        "path_secao": str(path_secao),
        "path_validacao": str(path_val),
        **stats,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Processa BU Web TSE → parquet compacto")
    ap.add_argument("path_zip", type=Path, help="Caminho do .zip do boletim de urna web")
    ap.add_argument("--turno", type=int, required=True)
    ap.add_argument("--uf", type=str, required=True)
    ap.add_argument(
        "--extract-dir",
        type=Path,
        default=None,
        help="Pasta de extração (default: /tmp temporário)",
    )
    ap.add_argument("--keep-csv", action="store_true", help="Não apagar CSV extraído")
    args = ap.parse_args()

    res = process_zip(
        args.path_zip,
        turno=args.turno,
        uf=args.uf,
        extract_dir=args.extract_dir,
        cleanup_csv=not args.keep_csv,
    )
    print("OK")
    for k, v in res.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
