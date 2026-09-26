# Validação BU Web — PA 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **18.235**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=PA): **18.235** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 2.073.895 | 2.073.895 | 0 | 1.000000 |
| Lula (13) | 2.509.084 | 2.509.084 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/pa_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/pa_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
