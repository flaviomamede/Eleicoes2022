# Validação BU Web — SP 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **101.073**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=SP): **101.073** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 12.239.989 | 12.239.989 | 0 | 1.000000 |
| Lula (13) | 10.490.032 | 10.490.032 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/sp_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/sp_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
