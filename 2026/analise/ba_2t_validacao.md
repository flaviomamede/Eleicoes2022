# Validação BU Web — BA 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **34.424**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=BA): **34.424** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 2.357.028 | 2.357.028 | 0 | 1.000000 |
| Lula (13) | 6.097.815 | 6.097.815 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Governador
- Presidente

## Artefatos

- `dados/buweb/ba_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/ba_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
