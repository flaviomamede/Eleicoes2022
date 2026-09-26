# Validação BU Web — PR 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **25.721**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=PR): **25.721** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 3.628.612 | 3.628.612 | 0 | 1.000000 |
| Lula (13) | 2.363.492 | 2.363.492 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/pr_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/pr_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
