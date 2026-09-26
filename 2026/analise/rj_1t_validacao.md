# Validação BU Web — RJ 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **34.068**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=RJ): **34.068** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 4.831.246 | 4.831.246 | 0 | 1.000000 |
| Lula (13) | 3.847.143 | 3.847.143 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/rj_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/rj_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
