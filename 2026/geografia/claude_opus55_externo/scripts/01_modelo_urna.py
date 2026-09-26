"""Extrai o modelo de urna de cada seção da planilha VOTOS_T1E2.xlsx.

A planilha (aba VOTOS_T1E2, ~470 mil linhas, 627 MB de XML) foi montada a partir
do banco do projeto John Robson (github.com/JohnRobson/Eleicoes2022), que obteve
o modelo de cada urna nos logs publicados pelo TSE. A leitura é feita em fluxo
(lxml.iterparse) para caber em memória.

Saída: dados/modelo_urna_secao.csv.gz com
  ID_SECAO, LOG_MODELO, LOG_FG2020 (1 = UE2020), REGIAO, FX_APTOS_MUNICIPIO,
  FG_CAPITAL, CODMUN_IBGE
"""
import csv
import gzip
import re
import zipfile

from lxml import etree

from common import DADOS

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
MANTER = ["ID_SECAO", "LOG_MODELO", "LOG_FG2020", "REGIAO",
          "FX_APTOS_MUNICIPIO", "FG_CAPITAL", "CODMUN_IBGE"]


def indice_coluna(ref: str) -> int:
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def localizar_aba(z: zipfile.ZipFile, nome: str) -> str:
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    rels = etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid = None
    for s in wb.iter(NS + "sheet"):
        if s.get("name") == nome:
            rid = s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
    for r in rels:
        if r.get("Id") == rid:
            return "xl/" + r.get("Target").lstrip("/").replace("xl/", "")
    raise ValueError(f"aba {nome} não encontrada")


def main():
    xlsx = sorted(DADOS.glob("VOTOS_T1E2*.xlsx"))
    if not xlsx:
        raise FileNotFoundError("Coloque VOTOS_T1E2.xlsx em dados/.")
    z = zipfile.ZipFile(xlsx[0])
    sst = []
    for _, el in etree.iterparse(z.open("xl/sharedStrings.xml"), tag=NS + "si"):
        sst.append("".join(el.itertext()))
        el.clear()
    aba = localizar_aba(z, "VOTOS_T1E2")
    saida = DADOS / "modelo_urna_secao.csv.gz"
    cab_idx = None
    n = 0
    with gzip.open(saida, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(MANTER)
        for _, row in etree.iterparse(z.open(aba), tag=NS + "row"):
            vals = {}
            for c in row.iterfind(NS + "c"):
                v = c.find(NS + "v")
                if v is None:
                    continue
                vals[indice_coluna(c.get("r"))] = sst[int(v.text)] if c.get("t") == "s" else v.text
            if cab_idx is None:
                if "ID_SECAO" in vals.values():          # linha de cabeçalho
                    cab_idx = {nome: i for i, nome in vals.items()}
            else:
                w.writerow([vals.get(cab_idx[c], "") for c in MANTER])
                n += 1
            row.clear()
            while row.getprevious() is not None:
                del row.getparent()[0]
    print(f"{n} seções gravadas em {saida}")


if __name__ == "__main__":
    main()
