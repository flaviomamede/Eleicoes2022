# Pasta de dados

Esta pasta não é versionada (exceto este arquivo e `manifesto.json`). Conteúdo esperado:

| Arquivo | Origem | Como obter |
|---|---|---|
| `secoes_2022_t1.csv.gz`, `secoes_2022_t2.csv.gz` | Boletins de urna do TSE (conjunto "Resultados – 2022 – Boletim de Urna"), convertidos para uma linha por seção | `scripts/01a_gerar_base_secoes.py` a partir dos arquivos `bweb_*` do TSE, ou arquivo de release deste repositório |
| `VOTOS_T1E2.xlsx` | Planilha por seção com o modelo de urna (campo `LOG_MODELO`), derivada do banco do projeto JohnRobson/Eleicoes2022 | Arquivo do autor, publicado como release |
| `modelo_urna_secao.csv.gz` | Gerado por `scripts/01_modelo_urna.py` | — |
| `geo/*` | Hidalgo v0.16 e geobr v2.0.0 | `scripts/00_baixar_dados.py` |
| `cache/*` | Pickles gerados pelos scripts | Automático |

`manifesto.json` registra tamanho e SHA-256 de cada arquivo usado (gerado por `00_baixar_dados.py`).
