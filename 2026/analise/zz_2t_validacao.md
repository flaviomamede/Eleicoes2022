# Validação BU Web — ZZ 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **1.018**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=ZZ): **1.017** (99.9%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 145.264 | 145.264 | 0 | 1.000000 |
| Lula (13) | 152.905 | 152.905 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/zz_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/zz_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
