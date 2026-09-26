# Validação BU Web — SE 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **5.498**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=SE): **5.498** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 378.610 | 378.610 | 0 | 1.000000 |
| Lula (13) | 828.716 | 828.716 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/se_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/se_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
