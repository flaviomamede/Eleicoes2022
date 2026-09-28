"""Baixa as bases geográficas públicas e registra o manifesto dos dados.

Fontes (releases do GitHub, sem autenticação):
  - Hidalgo, geocode_br_polling_stations, v0.16: locais de votação geocodificados 2006–2024
  - geobr (IPEA), geobr_prep_data, v2.0.0: municípios, locais de votação e manchas urbanas de 2022

As bases do TSE (boletins de urna) e o arquivo VOTOS_T1E2.xlsx não são baixados aqui;
ver README, seção "Dados".
"""
import hashlib
import json
import urllib.request

from common import DADOS, GEO

ARQUIVOS = {
    "geocoded_polling_stations.csv.gz":
        "https://github.com/fdhidalgo/geocode_br_polling_stations/releases/download/v0.16/geocoded_polling_stations.csv.gz",
    "section_panel_mapping.csv.gz":
        "https://github.com/fdhidalgo/geocode_br_polling_stations/releases/download/v0.16/section_panel_mapping.csv.gz",
    "panel_ids.csv.gz":
        "https://github.com/fdhidalgo/geocode_br_polling_stations/releases/download/v0.16/panel_ids.csv.gz",
    "municipalities_2022_simplified.parquet":
        "https://github.com/ipea/geobr_prep_data/releases/download/v2.0.0/municipalities_2022_simplified.parquet",
    "pollingplaces_2022.parquet":
        "https://github.com/ipea/geobr_prep_data/releases/download/v2.0.0/pollingplaces_2022.parquet",
    "urbanareas_2022_simplified.parquet":
        "https://github.com/ipea/geobr_prep_data/releases/download/v2.0.0/urbanareas_2022_simplified.parquet",
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def main():
    for nome, url in ARQUIVOS.items():
        destino = GEO / nome
        if destino.exists():
            print(f"já existe: {nome}")
            continue
        print(f"baixando {nome} ...")
        urllib.request.urlretrieve(url, destino)

    manifesto = {}
    for p in sorted(list(GEO.glob("*")) + list(DADOS.glob("secoes_2022_t*")) +
                    list(DADOS.glob("VOTOS_T1E2*.xlsx")) + list(DADOS.glob("modelo_urna_secao*"))):
        if p.is_file():
            manifesto[str(p.relative_to(DADOS))] = {"bytes": p.stat().st_size, "sha256": sha256(p)}
    (DADOS / "manifesto.json").write_text(json.dumps(manifesto, indent=2, ensure_ascii=False))
    faltando = [n for n in ("secoes_2022_t1.parquet", "secoes_2022_t2.parquet")
                if not (DADOS / n).exists() and not (DADOS / n.replace(".parquet", ".csv.gz")).exists()]
    if faltando:
        print("Atenção: base larga do TSE ausente:", faltando)
    if not list(DADOS.glob("VOTOS_T1E2*.xlsx")) and not (DADOS / "modelo_urna_secao.csv.gz").exists():
        print("Atenção: VOTOS_T1E2.xlsx (modelo de urna por seção) ausente.")
    print(f"manifesto gravado em {DADOS / 'manifesto.json'}")


if __name__ == "__main__":
    main()
