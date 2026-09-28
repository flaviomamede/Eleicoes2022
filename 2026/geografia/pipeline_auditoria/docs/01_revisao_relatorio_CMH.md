# 01 — Revisão do relatório "Uma análise estatística do 2º turno das eleições de 2022 para presidente"

Script: `scripts/02_cmh_reproducao.py` e `scripts/03_secao_zona_local.py`. Resultados: `resultados/cmh_*.csv` e `resultados/secao_*.csv`.

## 1. O relatório

O relatório original aplica o teste de Cochran–Mantel–Haenszel (CMH) ao par modelo de urna (anteriores a 2020 × UE2020) e candidato (Lula × Bolsonaro), estratificado por zona, município, estado e região, e conclui que o tipo de urna influenciou o resultado. Nas planilhas, o "Candidato 1" é Lula; R > 1 significa chance de voto em Lula maior nas urnas antigas do que nas UE2020 do mesmo estrato.

## 2. Reprodução

A base por seção reproduz os resultados oficiais dos dois turnos, e a agregação por município × zona coincide com a planilha original em todos os 6.241 estratos. A Tabela 1 foi reproduzida; a única divergência é de 0,1% no CMH do recorte de municípios pequenos.

| Estratificação | Estratos com os dois modelos | R relatório | R recalculado | CMH recalculado |
|---|---|---|---|---|
| Município × zona | 942 | 1,055 | 1,0550 | 4.179,7 |
| Município | 581 | 1,047 | 1,0475 | 3.401,3 |
| Estado | 27 | 1,174 | 1,1745 | 176.735 |
| Região | 5 | 1,174 | 1,1738 | 176.895 |
| Municípios < 100 mil, por município | 434 | 1,106 | 1,1061 | 3.173,9 |

## 3. Achados

**Tabela 2.** A tabela apresenta a razão de chances bruta de cada estado, sem estratificação interna; a segunda coluna, também rotulada "R", é o erro-padrão de ln R. Dez estados estão com valores na linha errada: AM e AP trocados, MG e MT trocados, rotação entre PE, PI e PR e entre RO, RR e RS. Os rótulos verdadeiros foram confirmados pela proporção de Lula de cada estado no resultado oficial. A razão bruta real de Rondônia é 0,84.

**Tabela 3.** O R conjunto de 2,054 e o CMH de 677.018 foram calculados sobre os estados corretos (AM, PB, AL, RR, CE, PE, RN, SE e MA); só os rótulos do texto foram deslocados. Estratificando esses nove estados por município, R cai para 1,033 e o CMH para 65: 96% de ln R desaparece. Nesses estados, as capitais votaram com 0,5% a 2,2% de urnas antigas (16,6% em Manaus, zero em Boa Vista), e o interior, com 44% a 100%.

**Concentração em São Paulo.** São Paulo concentra 14,1 dos 15,6 milhões de votos em urnas antigas dos municípios que tinham os dois modelos. Sem SP, a razão intramunicipal é 0,996 (CMH = 3,55). O Nordeste tem razão intramunicipal de 0,994 e, por município × zona, de 0,990.

**Unidade de análise.** O CMH trata cada voto como observação independente, mas o modelo de urna é atribuído à seção inteira. Dentro das zonas, as seções variam 4,35 vezes mais do que o modelo de votos independentes admite. Com a seção como unidade, efeito fixo de zona e erro-padrão agrupado por zona, a diferença é de +1,27 ponto percentual com t = 5,4, contra z ≈ 65 implícito no CMH.

**Alocação dentro das zonas.** Dentro da mesma zona, as seções com urna antiga têm em média 6,9 eleitores aptos a mais (t = 4,9) e numeração mais alta (t = 7,5), duas variáveis definidas pelo cadastro e que a urna não altera. Em São Paulo, seções consecutivas trocam de modelo 25.100 vezes, contra 43.429 esperadas numa alocação aleatória: os modelos foram distribuídos por prédio. Nas zonas paulistas mistas há 9.585 locais de votação, dos quais 5.787 só com urnas antigas, 3.429 só com UE2020 e 369 com os dois modelos.

**Efeito ajustado.** Diferença das urnas antigas na proporção de Lula (pontos percentuais; t entre parênteses).

| Comparação | SP | Brasil |
|---|---|---|
| Mesma zona, sem covariáveis | +1,37 (5,6) | +1,27 (5,4) |
| Mesma zona, com composição legislativa | +0,26 (3,6) | +0,24 (2,5) |
| Mesmo local, sem covariáveis | +0,10 (0,5) | +0,07 (0,7) |
| Mesmo local, com composição legislativa | −0,06 (−0,4) | +0,01 (0,1) |

**Controles negativos.** Dentro das zonas paulistas, as seções com urna antiga votaram 0,98 ponto menos no PL para deputado federal (t = −7,0), desfecho que uma transferência restrita ao voto presidencial não altera. Dentro do mesmo local, a diferença é de −0,10 ponto (t = −0,7).

**Poder.** Uma transferência de 1% dos votos de Bolsonaro nas urnas antigas de SP (87 mil votos) seria detectada dentro do prédio com t = 4,0; uma transferência capaz de inverter a margem (≈ 1,07 milhão de votos) produziria t entre 21 e 65, conforme o recorte.

**Magnitude.** Igualar, em cada município misto, a proporção de Lula nas urnas antigas à das UE2020 exige deslocar 177.781 votos, praticamente todos em São Paulo. Estendendo essa taxa a todas as urnas antigas, chega-se a cerca de 1,53 milhão de votos de margem, abaixo dos 2,14 milhões da margem oficial.

## 4. Correções ao relatório

Rotular a Tabela 2 como razões brutas e corrigir os dez rótulos; identificar o Candidato 1 como Lula; corrigir o p-valor impresso pelo R para 2,2 × 10⁻¹⁶; retirar a comparação com tabagismo e câncer, que compara estatísticas de teste com tamanhos amostrais incomparáveis (a força de uma associação é medida pela razão de chances: > 2 no exemplo citado, 1,05 aqui); e substituir a conclusão de prova estatística pela classificação da seção 5.

## 5. Conclusão

A diferença agregada entre modelos existe e é um indício. A análise o atribui à alocação: a associação cai 96% nos estados destacados quando se compara dentro do município, a alocação dentro das zonas é comprovadamente não aleatória, os controles negativos acompanham a diferença e, dentro do mesmo prédio, a diferença é nula com poder para detectar transferências de 1% dos votos de Bolsonaro.
