# Validação BU Web — PA 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **18.235**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=PA): **18.235** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 1.884.673 | 1.884.673 | 0 | 1.000000 |
| Lula (13) | 2.443.730 | 2.443.730 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/pa_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/pa_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
