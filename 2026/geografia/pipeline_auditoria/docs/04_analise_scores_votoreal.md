# 04 — Análise dos scores partidários do site votoreal

Script: `scripts/04_calibragem_scores.py` (e `03_secao_zona_local.py` para o teste por local). Resultados: `resultados/scores_*.csv`.

## 1. O método do site

O site votoreal.org, de John Robson, atribui a cada partido quatro percentuais (Bolsonaro e Lula, 1º e 2º turnos) que representam a fração dos eleitores do partido em cada cargo que votaria em cada candidato a presidente. Aplicados aos votos de deputado estadual, deputado federal, senador e governador de cada urna, esses percentuais geram uma estimativa do voto presidencial esperado, comparada depois com o registrado, por modelo de urna. A tabela foi montada a critério do autor.

## 2. Calibragem objetiva

A tabela de transferência pode ser estimada a partir dos próprios resultados por regressão ecológica restrita (Goodman; taxas entre 0 e 1), estado a estado, usando a variação entre as cerca de 470 mil seções. Taxas médias ponderadas entre estados, voto a deputado federal no 1º turno → voto presidencial:

| Partido | Site: Bolsonaro 1T | Calibrado: Bolsonaro 1T | Site: Lula 1T | Calibrado: Lula 1T |
|---|---|---|---|---|
| PL | 100 | 82 | 0 | 13 |
| PP | 92 | 42 | 8 | 48 |
| Republicanos | 92 | 50 | 8 | 41 |
| PSC | 90 | 54 | 10 | 37 |
| MDB | 50 | 43 | 50 | 47 |
| PSD | 50 | 41 | 50 | 50 |
| União | 50 | 41 | 50 | 44 |
| PT | 0 | 5 | 100 | 93 |

As taxas de partidos pequenos são instáveis, porque a regressão ecológica mistura o efeito de partidos que costumam aparecer juntos na mesma urna; as dos partidos grandes são robustas. No 1º turno, todos os pares do site somam 100%, o que atribui zero aos demais candidatos, embora MDB (Simone Tebet), PDT (Ciro Gomes), União Brasil (Soraya Thronicke), NOVO (Felipe d'Avila), PTB (Padre Kelmon), DC (Eymael), PSTU, PCB e UP tivessem candidatura própria.

## 3. Regra das UE2020 aplicada às urnas antigas

Calibrada nas seções UE2020 de cada estado e aplicada às seções com urna antiga do mesmo estado, a regra subestima a votação de Bolsonaro nas urnas antigas em 26% a 46% em sete estados do Nordeste (AL, CE, MA, PB, PE, RN, SE). A ordenação dos estados por esse erro acompanha a razão de chances bruta estadual (correlação de postos de −0,89) e quase não acompanha a razão intramunicipal (−0,21).

**Placebo com a mesma marca.** Nas capitais nordestinas, 97,8% a 99,6% dos votos foram registrados em UE2020; no interior, 61% a 84% em urnas antigas. Aprendida nas UE2020 da capital e aplicada às UE2020 do interior, a regra erra a votação de Bolsonaro entre 16% e 31% em sete dos nove estados nordestinos. A diferença aparece sem nenhuma troca de modelo de urna.

**Teste dentro do prédio.** Nos 1.353 locais de votação do país com os dois modelos, descontada a composição legislativa de cada seção, a diferença entre urnas antigas e UE2020 na proporção de Lula é de +0,01 ponto no país e −0,06 ponto em São Paulo.

## 4. Conclusão

A regra partidária detecta uma diferença real entre modelos de urna. A diferença decorre de onde cada modelo foi instalado, capitais e cidades maiores de um lado, interior e municípios menores de outro, e do voto dividido entre partidos de campos opostos, comum no interior. Onde os dois modelos podem ser comparados em condições iguais, eles registram o mesmo resultado.

---

## Texto para leitores

**O que a comparação entre o voto para deputado e o voto para presidente revela sobre as urnas de 2022**

O site votoreal.org, criado por John Robson, propõe um teste engenhoso. Quem vota em partidos de direita para deputado, senador ou governador tende a votar em Bolsonaro para presidente, e quem vota em partidos de esquerda tende a votar em Lula. A partir de uma tabela de percentuais por partido, o site estima quantos votos cada candidato deveria ter recebido em cada urna e compara essa estimativa com o resultado registrado. A conclusão apresentada é que as urnas de modelos anteriores a 2020 entregaram a Bolsonaro menos votos do que o esperado, em comparação com as urnas novas. A ideia de verificar a coerência entre os votos dados na mesma cabine para cargos diferentes é uma ferramenta legítima de auditoria, e o trabalho do site em organizar os dados públicos do TSE tornou possível a verificação descrita a seguir.

Esta análise usou os boletins de urna publicados pelo TSE para as cerca de 472 mil seções eleitorais do país, nos dois turnos. O primeiro passo foi substituir os percentuais definidos a critério do autor por percentuais estimados a partir dos próprios resultados, estado por estado. No 1º turno, cerca de 80% dos eleitores que votaram no PL para deputado federal votaram em Bolsonaro; o site supõe 100%. Entre os eleitores de PP e Republicanos, a proporção fica entre 40% e 50%; o site supõe cerca de 92%. O voto dividido entre partidos de campos opostos é comum no Brasil, sobretudo no interior do Nordeste.

Mesmo com percentuais estimados de forma objetiva, o sinal apontado pelo site reaparece no nível estadual: quando a regra é aprendida nas urnas novas de um estado e aplicada às urnas antigas do mesmo estado, as urnas antigas de vários estados do Nordeste mostram de 26% a 46% menos votos de Bolsonaro do que a regra prevê. A causa está na localização das urnas. Nas capitais dos estados do Nordeste, quase todos os votos foram registrados em urnas novas; no interior, a maioria em urnas antigas. Usando apenas urnas novas, a regra aprendida na capital erra a votação de Bolsonaro no interior entre 16% e 31% em sete dos nove estados nordestinos. A diferença aparece sem nenhuma troca de modelo de urna e mede a distância política entre capital e interior.

A comparação mais justa possível é entre urnas instaladas no mesmo local de votação, levando em conta o voto para deputado de cada seção. Nos 1.353 locais do país com os dois modelos lado a lado, a diferença entre urnas antigas e novas é estatisticamente igual a zero. Para verificar se o método seria capaz de detectar uma fraude real, foram inseridas fraudes simuladas nos dados verdadeiros: desviar 1% dos votos de Bolsonaro nas urnas antigas de São Paulo já seria detectado, e uma fraude do tamanho necessário para mudar o resultado produziria um sinal dezenas de vezes maior que a flutuação estatística normal. Os dados reais não mostram nada parecido.

A diferença entre urnas antigas e novas existe nos totais e decorre de onde cada modelo foi instalado. Onde os dois modelos podem ser comparados em condições iguais, eles registram o mesmo resultado. A comparação exige os dois modelos no mesmo lugar, e cerca de 44% dos votos do país foram dados em municípios que só tinham urnas antigas; para essas áreas, a análise geográfica está em andamento. Para o aperfeiçoamento do método do site, duas mudanças tornariam as suas conclusões mais sólidas: substituir os percentuais definidos a critério por percentuais estimados a partir dos dados de cada região e comparar urnas dentro do mesmo local de votação.
