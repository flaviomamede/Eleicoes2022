# Validação BU Web — MA 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **16.423**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=MA): **16.423** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 983.861 | 983.861 | 0 | 1.000000 |
| Lula (13) | 2.603.454 | 2.603.454 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/ma_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/ma_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
