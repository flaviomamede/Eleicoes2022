# Crítica Opus ao relatório de calibragem (2026-09-26)

Fonte: comentário do Claude após ler `analise/relatorio_calibragem.md`.

## Tese

O Δ (aplicar regra das UE2020 nas urnas antigas, por UF) **reproduz o contraste
capital × interior**, com a mesma geografia da razão de chances bruta estadual
(correlação de postos ≈ −0,88 com a Tabela 2). A razão **intramunicipal** correlaciona
só ≈ −0,23. Nos estados de maior Δ (PB, AL, PE, AM, RN, SE, MA, CE), as capitais votam
quase só em UE2020; o interior concentra as urnas antigas. A regra é aprendida num
domínio e extrapolada a outro com pouca interseção.

Sinais em PA e MT (urnas antigas com *mais* Bolsonaro que o previsto) acompanham
interior agrícola à direita da capital — incompatível com mecanismo uniforme pró-Lula.

## O que o hold-out valida

Só o domínio UE2020. Não valida extrapolação ao interior / urnas antigas.

## Taxas individuais

PSOL→Bolsonaro ~49%, NOVO→Lula ~0% etc. mostram especificação frágil sem soma 1
por partido e com colinearidade. Resíduos sistemáticos podem ser artefato de
extrapolação, não efeito de marca.

## Correções factuais ao relatório

1. “Erro %” é **erro relativo** (real/previsto − 1), não pontos percentuais da
   proporção. Corrigir a abertura do relatório.
2. Contagens: relatório 192.640 Positivo / 278.357 Diebold (1T) vs VOTOS_T1E2
   191.317 UE2020 / 280.710 antigas. Reconciliar ~1.323 seções (provável: seções
   sem modelo no log / classificação Outro).

## Rede de proposições (análise 1 JR)

| Nº | Proposição | Indicador sugerido |
|----|------------|--------------------|
| R1 | Tabela subjetiva JR = taxas reais | ~0,05 (afasta-se em PP/Republicanos) |
| R2 | Regra UE2020 por UF erra nas antigas da mesma UF | ~1,00 (estabelecido) |
| R3 | Hold-out 70/30 valida aplicação às antigas | 0,00 (não valida) |
| R4 | Erro de R2 decorre do modelo de urna | ≤0,05, **pendente T1/T2** |

## Testes de controle (próxima análise, após base por seção)

Blocos: PL | DIREITA_ALIADA | CENTRO | ESQUERDA | BRANCO_NULO.
Taxas ∈ [0,1], soma 1 por bloco (Bolsonaro+Lula+Outros+Branco/Nulo).

- **T1** Placebo capital→interior: calibrar UE2020 da capital → aplicar UE2020 do interior.
- **T2** Intramunicipal: ≥30 seções de cada marca no município; calibrar UE2020 → antigas *do mesmo município*.
- **T3** Direção inversa: calibrar antigas → aplicar UE2020.

Previsão geográfica: T1 com Δ grandes no NE; T2 colapsa.
Previsão marca: T1 ~0; T2 preserva Δ.
