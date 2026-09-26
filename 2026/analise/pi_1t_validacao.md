# Validação BU Web — PI 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **8.963**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=PI): **8.963** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 406.897 | 406.897 | 0 | 1.000000 |
| Lula (13) | 1.518.008 | 1.518.008 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/pi_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/pi_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
