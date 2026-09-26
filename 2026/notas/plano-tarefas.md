# Plano de tarefas (ajustado 2026-09-26)

## Prioridade 1 — Base larga por seção (entrega para o Claude)

Especificação em `dados/DOWNLOADS_BUWEB.md` / prompt Opus (1 linha = 1 seção × turno).

Otimizações acordadas:
- parquet por UF + manifesto retomável;
- duas passagens (schema → gravação);
- SP/MG isolados; limpar `/tmp` a cada UF;
- não agregar seções; flag `DUPLICADO_ID_SECAO`.

Saída: `dados/base_secoes/secoes_2022_t{1,2}.csv.gz` (+ parquet/sqlite),
dicionários, `validacao_totais`, README com totais oficiais e reconciliação
de contagem de modelos (UE2020 vs Positivo do relatório).

**Nesta etapa não entra modelo de urna** (cruzamento posterior por `ID_SECAO`).

## Prioridade 2 — Testes de controle da calibragem (T1, T2, T3)

Depois da base (ou em paralelo se o Claude rodar aí). Ver
`notas/critica-opus-relatorio-calibragem.md`.

Ajustes de especificação em relação ao pipeline antigo:
- blocos partidários (não dezenas de partidos soltos);
- soma 1 por bloco;
- métricas: erro relativo % **e** diferença em pontos percentuais da proporção;
- T1/T2 separam geografia de marca (R4).

## O que o relatório atual já vale (não descartar)

- R2: regra das UE2020 por UF não reproduz as antigas — **sim**.
- R1: tabela JR ≠ calibrada sobretudo em PP/Republicanos — **sim**.
- R3/R4: hold-out **não** valida marca; Δ atual **não** isola marca.

Corrigenda no próprio relatório: `analise/relatorio_calibragem.md` (seção no topo).

## O que não fazer agora

- Tratar o Δ UF Positivo→Diebold como prova de efeito de marca.
- Recalibrar dezenas de partidos sem restrição de soma e sem T1/T2.
