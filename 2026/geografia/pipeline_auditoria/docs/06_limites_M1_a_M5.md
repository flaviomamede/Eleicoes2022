# 06 — Limites da verificação: mecanismos M1 a M5

## 1. Onde cada verificação atua

O caminho de um voto passa por vários elos: a intenção do eleitor, o registro pelo software no momento da digitação, o RDV e os contadores gravados na memória, o boletim impresso e afixado na seção, a transmissão e a totalização. A comparação entre o boletim impresso e o publicado testa apenas os elos posteriores à urna. O RDV é gravado pelo mesmo software que produz o boletim; a concordância entre os dois demonstra coerência interna do equipamento, sem demonstrar fidelidade à intenção do eleitor. Em 2022 não havia registro do voto criado fora do software e conferido pelo eleitor, de modo que a contagem propriamente dita não tinha verificação pública independente.

## 2. Independência de software

Rivest e Wack (*Philosophical Transactions of the Royal Society A*, 2008) definem um sistema como independente de software quando uma alteração não detectada no software não pode produzir uma alteração não detectável no resultado. A urna eletrônica brasileira sem registro em papel não satisfaz esse critério. A garantia do registro repousa sobre controles aplicados ao próprio software: inspeção do código-fonte por entidades credenciadas, assinaturas digitais, cerimônias de carga, zerésima e teste de integridade.

O voto impresso tem histórico legislativo e judicial próprio. Por força da Lei 10.408/2002, parte das urnas imprimiu os votos em 2002, e no Distrito Federal e em Sergipe todas tiveram módulo de impressão. A impressão voltou a ser prevista em lei para 2018; o STF suspendeu a norma e, em setembro de 2020, declarou-a inconstitucional por unanimidade (ADI 5889), com o fundamento de risco ao sigilo do voto. Em agosto de 2021, a PEC 135/2019 teve 229 votos favoráveis e 218 contrários na Câmara, abaixo dos 308 exigidos, e foi arquivada.

## 3. Teste de integridade de 2022

No teste de integridade, urnas prontas para a eleição recebem votos em papel digitados em processo filmado, e o resultado é comparado ao boletim. Em 2022, segundo o TSE, 641 urnas passaram pelo teste, 58 delas, em 19 estados e no Distrito Federal, no projeto piloto com biometria sugerido pelas Forças Armadas. O relatório das Forças Armadas registrou 0% de inconsistência entre boletins e dados do TSE nas amostras de 442 e 501 urnas, considerou que o teste sem biometria atendeu aos requisitos e concluiu que o piloto com biometria não teve participantes suficientes para uma conclusão. O ofício do Ministério da Defesa de 9/11/2022 (cópia em `JohnRobson/Eleicoes2022/relatorios`) afirmou que, pelos testes realizados, não é possível afirmar que o sistema está isento da influência de um eventual código malicioso, e apontou o acesso dos computadores à rede do TSE durante a compilação. O TSE registrou que nenhuma entidade fiscalizadora apontou fraude ou inconsistência.

## 4. O que a estatística delimita

Inverter a margem exige transferir cerca de 1,07 milhão de votos. Mesmo transferindo todos os votos de Bolsonaro nas urnas em que ele foi mais votado, seriam necessárias pelo menos 4.113 urnas (0,87% do total); a amostra aleatória de 641 urnas do teste de integridade incluiria ao menos uma delas com probabilidade de 99,6%, condicionada a que o código não reconheça as condições do teste. Uma fraude mais dispersa exige ainda mais urnas. Uma fraude concentrada deixaria urnas com Bolsonaro próximo de zero onde o eleitorado vota à direita nos outros cargos; as 1.346 seções com esse perfil encontradas são redutos de deputados locais, coerentes no voto para senador (documento 05).

| Mecanismo | Situação com os dados de 2022 |
|---|---|
| M1. Manipulação após a urna (transmissão ou totalização) | Excluída: soma dos boletins igual ao resultado oficial; 0% de inconsistência nas amostras militares |
| M2. Transferência específica das urnas antigas | Excluída a partir de 1% dos votos de Bolsonaro nas urnas testadas (documento 01) |
| M3. Manipulação concentrada em poucas urnas, na escala da margem | Excluída: as anomalias entre cargos encontradas são redutos locais, coerentes no voto para senador |
| M4. Manipulação dispersa, com código que não reconhece o teste | Excluída com probabilidade ≥ 99,6% pela amostra do teste de integridade |
| M5. Manipulação dispersa, comum a todos os modelos, com código que reconhece o teste | Indeterminada com os registros de 2022 |

No conjunto M5, nenhuma distorção pode ser observada, porque não existe dentro dos dados uma referência que não tenha passado pelo mesmo software. A ausência de indício nesse conjunto nada informa. Uma fraude capaz de alterar o resultado só caberia em M5: dispersa por milhares de urnas, presente igualmente nos dois modelos e capaz de reconhecer e contornar o teste de integridade. Esse conjunto só se fecha com um registro criado fora do software e conferido pelo eleitor, acompanhado de contagem pública de uma amostra, o que é uma escolha de desenho do sistema eleitoral, fora do alcance da análise dos resultados.
