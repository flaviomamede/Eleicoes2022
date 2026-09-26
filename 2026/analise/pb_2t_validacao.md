# Validação BU Web — PB 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **9.602**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=PB): **9.602** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 802.502 | 802.502 | 0 | 1.000000 |
| Lula (13) | 1.601.953 | 1.601.953 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Governador
- Presidente

## Artefatos

- `dados/buweb/pb_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/pb_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
