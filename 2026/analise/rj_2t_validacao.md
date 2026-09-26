# Validação BU Web — RJ 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **34.068**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=RJ): **34.068** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 5.403.894 | 5.403.894 | 0 | 1.000000 |
| Lula (13) | 4.156.217 | 4.156.217 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/rj_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/rj_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
