# Progresso geografia — 2026-09-26

## Feito neste ambiente (Cursor)

1. **Dados ligados** em `pipeline_auditoria/dados/`:
   - symlinks `secoes_2022_t{1,2}.csv.gz` → `2026/dados/base_secoes/`
   - `modelo_urna_secao.csv.gz` gerado de `urnas_pres_gov.parquet` (sem VOTOS_T1E2.xlsx)
   - Hidalgo + geobr baixados (`scripts/00_baixar_dados.py`)

2. **`06_espacial.py` reexecutado** — resultados coerentes com o zip externo:

| Modelo (efeito fração urna antiga → % Lula) | coef_pp |
|---|---:|
| MQO | +3,29 |
| GM_Lag (ρ≈0,38) | +2,11 |
| GM_Error_Het (λ≈0,85) | +1,39 |
| Ref. no mesmo local (139 locais) | −0,10 pp (t = −0,5) |

Moran: Lula 0,85 · invalidação 0,56 · resíduo legislativo 0,64 · urna antiga 0,87.

3. **F3 iniciada** — `scripts/07_di_espacial.py` (Forsberg 6+7):
   - Quasi-binomial: `pInv ~ pSup` e com `old` + interação
   - Moran nos resíduos QB ainda alto (**I≈0,57**)
   - SLM / erro espacial em `pInv ~ pSup + old`
   - SEM linear (efeito × lat/lon)
   - Saídas: `resultados/di_espacial_*.csv` + `di_espacial_resumo.txt`

## Leitura preliminar F3

Há associação estatística entre invalidação e apoio a Lula (n muito grande → z enormes no GLM). Resíduos continuam espacialmente agrupados → o Cap. 6 sem geografia **não basta**. Coeficientes espaciais de `pSup` em escala de proporção são pequenos (~0,1–0,4 pp por unidade de pSup); SEM indica variação geográfica forte do efeito (lat/lon). Interpretação causal (DI vs demografia/alfabetização) e calibração F4a ficam para a sequência.

## Próximos

- F4a feita (`resultados/f4a_calibracao.csv`): erro espacial nos municípios mistos +0,44 pp (z = 5,2) e nas zonas mistas +0,46 pp (z = 5,4). Não reproduz a referência −0,10 pp (t = −0,5) do mesmo local. O +1,4 pp nacional não se transporta. GM_Lag nesse recorte não se identifica (grafo desconexo).
- F4b: GWR / SLEM (`mgwr`).
- F4c: pares cross-border 5/10/20 km.
- Documentar F3 em `docs/08_di_espacial.md` quando estabilizar.
