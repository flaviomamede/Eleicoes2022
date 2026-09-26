# Validação BU Web — SC 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **16.242**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=SC): **16.242** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 3.047.630 | 3.047.630 | 0 | 1.000000 |
| Lula (13) | 1.351.918 | 1.351.918 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Governador
- Presidente

## Artefatos

- `dados/buweb/sc_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/sc_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
