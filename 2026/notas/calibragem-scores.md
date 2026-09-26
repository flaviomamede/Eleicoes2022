# Calibragem objetiva dos scores

## Camadas (não são alternativas)

| Camada | Papel |
|--------|--------|
| Estimador | taxas ∈ [0,1]; **soma 1 por bloco/partido** (Bolsonaro+Lula+Outros+Branco/Nulo) |
| Unidade | UF; cargo a cargo; blocos partidários para reduzir colinearidade |
| Validação | hold-out **dentro do domínio de treino**; T1/T2/T3 para efeito de marca |

## O que o relatório Positivo→Diebold por UF estabeleceu

- A regra das UE2020 não se aplica bem às antigas da mesma UF (**R2**).
- A tabela subjetiva do JR diverge da calibrada em PP/Republicanos (**R1** fraco).
- O hold-out **não** autoriza concluir efeito de marca (**R3** = 0).
- Atribuir o erro à marca (**R4**) exige T1 e T2.

Detalhe: `critica-opus-relatorio-calibragem.md`, `plano-tarefas.md`.

## Premissa

Votos dos outros cargos = referência do perfil da seção. Sem isso, o resíduo
não se lê como desalinhamento “só do presidente”.
