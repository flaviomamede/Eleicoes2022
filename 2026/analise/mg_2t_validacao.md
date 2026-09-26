# Validação BU Web — MG 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **49.981**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=MG): **49.981** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 6.141.310 | 6.141.310 | 0 | 1.000000 |
| Lula (13) | 6.190.960 | 6.190.960 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/mg_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/mg_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
