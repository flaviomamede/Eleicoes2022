# Validação BU Web — MS 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **6.912**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=MS): **6.912** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 794.206 | 794.206 | 0 | 1.000000 |
| Lula (13) | 588.323 | 588.323 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/ms_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/ms_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
