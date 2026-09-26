# Trabalho 2026 — Auditoria estatística das eleições 2022

Retomada set/2026: calibragem de scores (VotoReal), controles T1/T2/T3, base por seção, análise geográfica (Forsberg caps. 6–7) e relatório ilustrado.

## Pastas

| Caminho | Conteúdo |
|---------|----------|
| `relatorio/` | Relatório MD + HTML autocontido + PDF (`build/`) |
| `analise/` | Calibragem, contraste UF, T1/T2/T3, CSVs |
| `geografia/` | Pacote espacial (Claude Opus externo) + F3 DI + Hidalgo/geobr |
| `dados/base_secoes/` | Base larga `secoes_2022_t*.csv.gz` / parquet |
| `dados/` | `urnas_pres_gov.parquet`, manifesto; zips BU **não** versionados |
| `docs/` | Forsberg PDF + notas Caps. 6–8 |
| `scripts/` | Geração de base, calibragem, figuras do relatório |
| `scores/`, `figuras/`, `notas/` | Auxiliares |
| `envio_calibragem_scores_johnrobson_*.zip` | Pacote enviado ao autor do site |

## O que entra no GitHub (e o que não)

**Versionado:** código, docs, resultados CSV, relatório, base `secoes_2022_t*.{csv.gz,parquet}`, `urnas_pres_gov.parquet`, geo Hidalgo/geobr, `modelo_urna_secao.csv.gz`.

**Fora do Git** (ver `2026/.gitignore`): `bweb_*.zip`, `buweb/`, `*.sqlite*`, caches `*.pkl`, `urnas_pres_gov.csv`, `por_uf/`. Regenerar BU → parquet com `scripts/`; geo com `geografia/.../00_baixar_dados.py`.

## Relatório

`relatorio/auditoria_eleicoes_2022.md` · `relatorio/build/*.html` · `relatorio/build/*.pdf`

## Status (2026-09-26)

- Indícios urna antiga × UE2020 atribuídos à **alocação**; no mesmo local ≈ 0 pp (com poder).
- R2 (calibragem) estabelecida; R4 (marca) não sustentada por T1/T2.
- Geografia: Moran alto; F3 (invalidação) iniciada; F4a–F4d em aberto.
