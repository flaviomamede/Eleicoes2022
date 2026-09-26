# Validação BU Web — AC 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **2.124**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=AC): **2.124** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 275.582 | 275.582 | 0 | 1.000000 |
| Lula (13) | 129.022 | 129.022 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/ac_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/ac_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
