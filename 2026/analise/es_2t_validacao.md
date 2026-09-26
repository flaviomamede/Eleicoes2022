# Validação BU Web — ES 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **9.239**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=ES): **9.239** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 1.282.145 | 1.282.145 | 0 | 1.000000 |
| Lula (13) | 926.767 | 926.767 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Governador
- Presidente

## Artefatos

- `dados/buweb/es_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/es_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
