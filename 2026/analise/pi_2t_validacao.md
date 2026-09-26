# Validação BU Web — PI 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **8.963**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=PI): **8.963** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 467.065 | 467.065 | 0 | 1.000000 |
| Lula (13) | 1.551.383 | 1.551.383 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/pi_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/pi_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
