# 02 — Rede de proposições

Cada proposição recebe um indicador de 0 a 1 que mede a verdade do enunciado, dado o conjunto de evidências examinadas. Uma proposição demonstrada vale 1; uma refutada vale 0; uma que depende de outra não pode ter indicador maior que o da proposição de que depende. O indicador de uma proposição causal (por exemplo, "o modelo de urna causou a diferença") não mede a existência do indício: a distorção entre modelos existe, e o indicador baixo afirma que a sua atribuição à urna é quase certamente falsa.

## Relatório CMH (2º turno)

| Nº | Proposição | Indicador | Fundamento |
|---|---|---|---|
| P0 | O modelo de urna está entrelaçado com a localização e o perfil das seções, inclusive dentro das zonas (confundimento) | 1,00 | Premissa do relatório, confirmada em todos os níveis examinados |
| P1 | Há correlação agregada entre modelo e voto | 1,00 | R bruto 1,146; por estado 1,174 |
| P2 | Há diferença intrazonal nacional | 1,00 | +1,27 ponto, t = 5,4 com a seção como unidade |
| P2a | A diferença intrazonal é homogênea no país | 0,03 | Concentrada em SP; sem SP, R = 0,996. Localiza o fenômeno e não pesa contra P6b |
| P3 | Os p-valores do CMH por voto são válidos | 0,00 | z implícito de 65 contra 5,4; dispersão de 4,35. A rejeição de H0 sobrevive |
| P4 | Dentro das zonas, a alocação independe do perfil das seções | 0,00 | Negação de P0: aptos, numeração e blocos por prédio |
| P4′ | Dentro do mesmo local, seções antigas e UE2020 são comparáveis | 0,85 | Controles negativos equilibrados no prédio; aptos com pequena diferença |
| P5 | O modelo de urna causou a diferença | 0,03 | Nula dentro do prédio, com poder para 1% |
| P6a | Há fraude com acionamento uniforme nas urnas antigas | 0,02 | Efeito nulo fora de SP e dentro do prédio |
| P6b | Há fraude com acionamento seletivo, concentrado em SP, em escala detectável (≥ 1%) | 0,03 | Nula dentro do prédio em SP |
| P6c | A comparação intrazonal indica efeito das urnas antigas no Nordeste | 0,02 | R = 0,990 por município × zona; −0,23 ponto por seção |
| P7 | A evidência equivale à do tabagismo–câncer | 0,00 | Estatísticas de teste com N incomparáveis; razão de chances 1,05 |
| P8 | O R = 2,05 dos nove estados evidencia fraude | 0,02 | Seleção posterior; R intramunicipal de 1,03 |
| P9 | A Tabela 2 apresenta razões estratificadas | 0,00 | Razões brutas, dez rótulos trocados |
| P10 | A diferença inverte o resultado | 0,00 | Magnitude intramunicipal inferior à margem; fraude plantada de escala da margem produziria t de 21 a 65 |

## Scores do site votoreal (John Robson)

| Nº | Proposição | Indicador |
|---|---|---|
| R1 | A tabela subjetiva representa as taxas reais de transferência partido → presidente | 0,05 |
| R2 | Calibrada nas UE2020 de cada UF, a regra erra sistematicamente nas urnas antigas da mesma UF | 1,00 |
| R3 | O hold-out entre zonas UE2020 valida a aplicação da regra às urnas antigas | 0,00 |
| R4 | O erro de R2 decorre da marca da urna | 0,03 |

## Urnas com votação mínima

| Nº | Proposição | Indicador |
|---|---|---|
| U1 | As votações mínimas de Bolsonaro se concentram nas urnas antigas por efeito do modelo | 0,02 |
| U2 | Nas 27 seções do AM sem voto em Bolsonaro, o voto presidencial destoa dos demais cargos da mesma urna | 0,00 |

## Mecanismos (ver `06_limites_M1_a_M5.md`)

| Mecanismo | Situação com os dados de 2022 |
|---|---|
| M1. Manipulação após a urna | Excluída |
| M2. Transferência específica das urnas antigas | Excluída a partir de 1% dos votos de Bolsonaro nas urnas testadas |
| M3. Manipulação concentrada em poucas urnas, na escala da margem | Excluída |
| M4. Manipulação dispersa, com código que não reconhece o teste de integridade | Excluída com probabilidade ≥ 99,6% |
| M5. Manipulação dispersa, comum a todos os modelos, com código que reconhece o teste | Indeterminada |
| D-ext. Fraude restrita a municípios sem comparação interna | Em aberto; objeto da análise geográfica |
