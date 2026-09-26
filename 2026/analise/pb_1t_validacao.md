# Validação BU Web — PB 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **9.602**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=PB): **9.602** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 717.416 | 717.416 | 0 | 1.000000 |
| Lula (13) | 1.554.868 | 1.554.868 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/pb_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/pb_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
