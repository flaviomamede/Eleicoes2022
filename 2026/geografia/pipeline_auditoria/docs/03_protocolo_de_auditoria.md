# 03 — Protocolo de auditoria

## 1. Terminologia

O Código de Processo Penal define indício, no art. 239, como a circunstância conhecida e provada que, tendo relação com o fato, autoriza concluir por indução a existência de outra ou outras circunstâncias. O Código de Processo Penal Militar (arts. 382 e 383) exige, para que o indício constitua prova, relação de causalidade entre o fato indicante e o fato indicado e coincidência com outros indícios ou com provas diretas. O inglês *evidence* cobre tanto o indício quanto a prova; neste projeto, os termos são usados no sentido do direito brasileiro.

Toda distorção real e estatisticamente estabelecida entre grupos de urnas é um **indício**. A análise decide, para cada indício, um de três destinos: **atribuído à alocação**, **atribuído à fraude** ou **indeterminado**. O indício é **discriminante** quando a sua relação causal com a urna sobrevive aos testes de mesmo local, controles negativos e confirmação em amostra independente; é **forte** quando converge com indícios independentes, como concentração por sessão de carga ou por fatores humanos. A **prova** exige ainda coincidência com prova direta, isto é, com um registro independente do software.

## 2. Elementos do protocolo

**Hipótese de mecanismo explícita.** Cada mecanismo de fraude deixa uma impressão digital própria nos dados. Uma hipótese sem mecanismo acomoda qualquer padrão e não pode ser testada.

**Poder do teste.** Antes de interpretar a ausência de sinal, injeta-se nos dados reais uma fraude sintética conhecida e mede-se a taxa de detecção. Se o teste detecta com poder de 90% ou mais uma fraude capaz de alterar o resultado e não encontra sinal nos dados reais, o mecanismo fica excluído naquela escala.

**Controles negativos.** O mesmo contraste é aplicado a desfechos que o mecanismo alegado não toca (voto para deputado, aptos, numeração da seção). Um contraste presente também nesses desfechos mede perfil; um deslocamento restrito ao voto presidencial, descontada a composição legislativa, é a impressão digital exclusiva da transferência.

**Pré-registro e confirmação.** Estatística, unidade, estratos, limiar e correção para comparações múltiplas são fixados antes da execução; a amostra é dividida entre exploração e confirmação; todos os testes executados são relatados.

**Do indício à prova.** O produto da auditoria é uma lista de unidades (seções, urnas, sessões de carga) sinalizadas por critério pré-registrado, para confronto com registros independentes.

## 3. Mecanismos e impressões digitais

| Mecanismo | Impressão digital | Situação |
|---|---|---|
| Transferência no software de parte das urnas | Deslocamento do voto presidencial dentro do mesmo local, descontada a composição legislativa | Testado: nulo em SP e no país |
| Inserção de votos | Comparecimento atípico concentrado num candidato; padrão de Klimek et al. (PNAS, 2012); excesso de eleitores liberados sem biometria | Dados disponíveis |
| Manipulação na totalização | Soma dos boletins diferente do resultado oficial | Testado: a soma reproduz o resultado oficial voto a voto |
| Manipulação na preparação e carga | Anomalias agrupadas por sessão de carga ou flashcard | Dados disponíveis |
| Atuação humana na seção | Deslocamento associado a liberação sem biometria ou horários atípicos | Dados disponíveis |

## 4. Indícios examinados

| Indício | Distorção | Destino | Fundamento |
|---|---|---|---|
| I1. Diferença agregada entre modelos | R = 1,17 por estado | Alocação | R = 1,05 dentro do município; UE2020 concentradas nas capitais |
| I2. Diferença dentro da zona | +1,27 ponto, t = 5,4 | Alocação | Concentrada em SP; nula dentro do local; controles negativos com o mesmo sinal |
| I3. Resíduo paulista entre prédios da mesma zona | +0,26 ponto, t = 3,6 | Alocação | Nulo dentro do prédio; uma fraude na urna produziria o mesmo efeito dentro e entre prédios (simulação) |
| I4. Erro da calibragem por UF | 26% a 46% em sete estados nordestinos | Alocação | Placebo capital → interior com urnas UE2020 reproduz 16% a 31% |
| I5. Zero voto em Bolsonaro em 27 urnas antigas do AM | Real | Alocação e alinhamento local | Municípios só com urnas antigas; PL com 0,5% para o Senado nessas seções |
| I6. PL alto para deputado e Bolsonaro abaixo de 10% (1.346 seções) | Real | Alinhamento local | PL com 1,8% para o Senado, contra 38,7% para deputado |
| I7. Mais brancos e nulos nas urnas antigas dentro da zona | +0,28 ponto no 1º turno, t = 6,6 | Alocação | Dentro do mesmo local: −0,07 ponto (t = −1,8) |
| I8. Razão intramunicipal elevada em Roraima | R = 1,77 | A examinar | Não significativa no Norte com a seção como unidade; falta teste específico por local |

## 5. Níveis e critérios de decisão

| Nível | Critério |
|---|---|
| Indício | Distorção real e significativa relacionada ao fato |
| Indício discriminante | Relação causal com a urna sobrevive ao teste de mesmo local, aos controles negativos e à confirmação |
| Indício forte | Discriminante e convergente com indícios independentes (carga, flashcard, fatores humanos), com magnitude acima do limiar detectável |
| Prova | Forte e coincidente com prova direta (boletim impresso × digital, RDV × boletim, hash) nas unidades específicas |
| Exclusão de mecanismo | Teste com poder ≥ 90% para fraude capaz de alterar o resultado, sem sinal |

Situação atual: há indícios; todos os examinados, exceto I8, foram atribuídos à alocação; nenhum se tornou discriminante a favor de fraude; não há prova de fraude; o conjunto M5 permanece indeterminado.
