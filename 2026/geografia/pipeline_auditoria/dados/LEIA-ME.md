# Pasta de dados

Esta pasta não é versionada (exceto este arquivo e `manifesto.json`). Conteúdo esperado:

| Arquivo | Origem | Como obter |
|---|---|---|
| `secoes_2022_t1.parquet`, `secoes_2022_t2.parquet` | Boletins de urna do TSE, uma linha por seção. É o formato versionado em `2026/dados/base_secoes/` | Atalho para essa pasta. O `.csv.gz` equivalente não entra no Git |
| `VOTOS_T1E2.xlsx` | Planilha por seção com o modelo de urna (campo `LOG_MODELO`), derivada do banco do projeto JohnRobson/Eleicoes2022 | Arquivo do autor, publicado como release |
| `modelo_urna_secao.csv.gz` | Gerado por `scripts/01_modelo_urna.py` | — |
| `geo/*` | Hidalgo v0.16 e geobr v2.0.0 | `scripts/00_baixar_dados.py` |
| `cache/*` | Pickles gerados pelos scripts | Automático |

`manifesto.json` registra tamanho e SHA-256 de cada arquivo usado (gerado por `00_baixar_dados.py`).
