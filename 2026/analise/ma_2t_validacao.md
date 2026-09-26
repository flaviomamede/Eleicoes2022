# Validação BU Web — MA 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **16.423**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=MA): **16.423** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 1.082.749 | 1.082.749 | 0 | 1.000000 |
| Lula (13) | 2.668.425 | 2.668.425 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/ma_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/ma_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
