# Validação BU Web — SP 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **101.073**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=SP): **101.073** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 14.216.587 | 14.216.587 | 0 | 1.000000 |
| Lula (13) | 11.519.882 | 11.519.882 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Governador
- Presidente

## Artefatos

- `dados/buweb/sp_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/sp_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
