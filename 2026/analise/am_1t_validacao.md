# Validação BU Web — AM 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **7.453**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=AM): **7.453** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 880.198 | 880.198 | 0 | 1.000000 |
| Lula (13) | 1.019.684 | 1.019.684 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/am_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/am_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
