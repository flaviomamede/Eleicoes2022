# Geografia / Forsberg Cap. 7+

Análises geográficas (invalidação × apoio, Moran, modelos espaciais).  
Separado da calibragem Positivo×Diebold enviada ao John Robson.

## Conteúdo desta pasta

| Caminho | O quê |
|---------|--------|
| `Eleicoes2022_2026.zip` | Pacote original do Claude Opus 5.5 (fora do Cursor) |
| `pipeline_auditoria/` | Docs 01–07, scripts 00–07, resultados |
| `../docs/Forsberg_notas_caps6_7_8.md` | Notas dos Caps. 6–8. O PDF da CRC não é versionado |

## Leitura rápida do pacote externo

- **Mesma linha** da auditoria urna/alocação (CMH, scores, cauda, protocolo).
- **Já espacial:** `scripts/06_espacial.py` + `docs/07_analise_geografica_projeto.md` + `resultados/espacial_*.csv`.
- Unidade = **local de votação** (~92k); coords Hidalgo; Moran k=8; MQO / SLM / erro espacial.
- Projeto Forsberg F1–F5 ainda em aberto (DI espacial, GWR/SLEM, calibração F4a).

Ver `PROGRESSO.md` (dados ligados, `06` reexecutado, F3 em `07_di_espacial.py`).

```bash
cd pipeline_auditoria/scripts
python3 00_baixar_dados.py   # já feito
python3 06_espacial.py
python3 07_di_espacial.py    # F3 Forsberg
```
