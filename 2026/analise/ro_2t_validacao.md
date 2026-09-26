# Validação BU Web — RO 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **4.198**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=RO): **4.198** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 633.236 | 633.236 | 0 | 1.000000 |
| Lula (13) | 262.904 | 262.904 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Governador
- Presidente

## Artefatos

- `dados/buweb/ro_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/ro_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
