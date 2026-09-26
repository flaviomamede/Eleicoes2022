# Validação BU Web — RN 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **7.674**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=RN): **7.674** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 622.731 | 622.731 | 0 | 1.000000 |
| Lula (13) | 1.264.179 | 1.264.179 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/rn_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/rn_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
