# Validação BU Web — AL 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **6.626**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=AL): **6.626** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 687.827 | 687.827 | 0 | 1.000000 |
| Lula (13) | 976.831 | 976.831 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Governador
- Presidente

## Artefatos

- `dados/buweb/al_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/al_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
