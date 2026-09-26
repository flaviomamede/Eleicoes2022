# Validação BU Web — DF 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **6.748**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=DF): **6.748** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 910.397 | 910.397 | 0 | 1.000000 |
| Lula (13) | 649.534 | 649.534 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Distrital
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/df_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/df_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
