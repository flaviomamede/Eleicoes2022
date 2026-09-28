# 07 — Análise geográfica: fontes, primeiros resultados e projeto

Script: `scripts/06_espacial.py`. Resultados: `resultados/espacial_*.csv`.

**Projeto:** ELEIÇÕES 2022 · **Data:** 26/09/2026 · **Referência metodológica:** Forsberg, *Understanding Elections through Statistics*, caps. 6 e 7

## 1. Objetivo

Estender ao espaço geográfico a auditoria estatística das contagens de 2022. O capítulo 7 de Forsberg parte de uma constatação que os nossos testes já confirmaram: o voto é um fenômeno espacial, eleitores próximos votam de forma parecida, e ignorar a geografia produz resíduos correlacionados e efeitos que variam no território. A análise geográfica tem dois papéis no projeto. O primeiro é aplicar os testes de invalidação diferencial dos capítulos 6 e 7 com controle espacial. O segundo é alcançar o domínio que os testes intrazonais e intralocais não cobrem: os municípios que só tiveram urnas antigas, com 44% dos votos válidos do país, onde não existe comparação interna com a UE2020.

## 2. Avaliação do projeto anterior (mapaseleitorais.zip)

O pacote contém uma cópia do repositório do workshop *Mapas Eleitorais com R* (FGV-CEPESP, Coda.Br 2023, `GV-CEPESP/mapaseleitorais2023`) e scripts R derivados que agregam a votação de 2022 por zona e produzem mapas temáticos. O material é um exercício de visualização e não contém nenhum procedimento de estatística espacial: não há matriz de vizinhança, índice de Moran, modelo de defasagem espacial, regressão geograficamente ponderada ou teste de hipótese.

Os scripts derivados têm três problemas que invalidam os mapas produzidos. Os dados agregados por município são unidos aos polígonos de estados (`read_state` + `left_join` por UF), de modo que cada estado recebe várias linhas de municípios. O percentual de Lula é calculado como a fração de zonas vencidas, e não como a fração de votos. Os códigos de município do TSE não são convertidos para os códigos do IBGE usados pelo `geobr`. O aproveitamento útil do pacote é a indicação da base de locais de votação geocodificados de Daniel Hidalgo (MIT), que passou a cobrir 2022 e é a fonte principal desta análise. A recomendação é não dar continuidade a esses scripts e adotar o fluxo em Python descrito abaixo.

## 3. Fontes encontradas e situação de acesso

### 3.1 Baixadas e validadas

| Fonte | Arquivo | Tamanho | Conteúdo |
|---|---|---|---|
| Hidalgo, `fdhidalgo/geocode_br_polling_stations`, release v0.16 | `geocoded_polling_stations.csv.gz` | 53,7 MB | Coordenadas de locais de votação 2006–2024; 93.561 locais em 2022; códigos TSE e IBGE; limite de erro calibrado `conf_dist_km` |
| idem | `section_panel_mapping.csv.gz` | 18,6 MB | Seção → identificador de painel do local, todas as eleições (4,37 milhões de registros) |
| idem | `panel_ids.csv.gz` | 6,0 MB | Identificador do mesmo local ao longo das eleições |
| geobr (IPEA), `ipea/geobr_prep_data`, release v2.0.0 | `municipalities_2022_simplified.parquet` | 20,6 MB | 5.572 polígonos municipais 2022 |
| idem | `pollingplaces_2022.parquet` | 16,3 MB | 88.168 locais de 2022, coordenadas do TSE (82.005) ou do geocodebr (6.163) |
| idem | `urbanareas_2022_simplified.parquet` | 31,6 MB | Manchas urbanas 2022 com classe de densidade |

As notas da versão 0.16 do conjunto de Hidalgo informam erro mediano fora da amostra de 28 m e 85,1% dos locais a menos de 500 m da posição verdadeira; `conf_dist_km` é um limite superior de erro válido para ao menos 90% dos locais, igual a zero quando a coordenada vem do TSE.

**Casamento com a nossa base de boletins.** O conjunto de Hidalgo casa 92.359 dos 92.361 locais de votação da base (100,0%) pela chave município TSE × zona × número do local; 78,2% têm coordenada fornecida pelo TSE e 93,4% têm limite de erro de até 1 km. O `geobr` casa 94,4% dos locais. Adota-se Hidalgo como fonte principal e o `geobr` como verificação cruzada.

**Validação ponto-no-polígono.** 99,08% dos locais caem dentro do próprio município. Dos 850 que caem fora, a distância mediana ao município é de 0,53 km (efeito da simplificação dos polígonos); 162 estão a mais de 5 km e são excluídos por coordenada provavelmente errada.

### 3.2 Disponíveis, ainda não baixadas

| Fonte | Tamanho | Uso previsto |
|---|---|---|
| `censustracts_2022_simplified.parquet` (geobr) | 380 MB | Polígonos dos setores censitários, para área e densidade em torno de cada local |
| `weightingareas_2022_simplified.parquet` (geobr) | 114 MB | Áreas de ponderação, unidade intermediária para controles socioeconômicos |
| `neighborhoods_2022` (geobr) | — | Bairros, onde oficialmente definidos |

### 3.3 Não acessíveis deste ambiente

A API do GitHub atingiu o limite de requisições anônimas; o download das releases foi feito pelas páginas HTML, sem prejuízo. Os domínios do TSE, do IBGE e da Base dos Dados continuam bloqueados neste ambiente. Os atributos dos setores censitários de 2022 (população, renda, idade), publicados pelo IBGE como *Agregados por setores censitários*, só estão disponíveis no site do IBGE e precisam ser baixados manualmente se forem usados como controles socioeconômicos. O portal CEPESP Data, recomendado por Hidalgo para resultados por local, não foi testado porque a base de boletins já cobre essa necessidade.

### 3.4 Território das seções

A seção eleitoral não tem território. A unidade espacial natural é o local de votação, representado por um ponto. Quando uma área for necessária (densidade, contiguidade), ela será construída por tesselação de Voronoi dos locais, recortada pelo polígono municipal e, nas cidades, pela mancha urbana; os setores censitários servem para validar essa aproximação.

## 4. Primeiros resultados

Todos os cálculos abaixo usam o local de votação como unidade (92 mil locais), o 2º turno para o voto presidencial e o 1º turno para a composição de voto a deputado federal, com matriz de vizinhança dos 8 vizinhos mais próximos, padronizada por linha.

### 4.1 Alcance da comparação através das fronteiras municipais

Nos municípios que só tiveram urnas antigas há 56.233 locais e 51,6 milhões de votos válidos. A fração desses votos com um local UE2020 próximo, em outro município, é:

| Raio | Votos com local UE2020 no raio |
|---|---|
| 2 km | 1,4% |
| 5 km | 4,1% |
| 10 km | 10,3% |
| 20 km | 22,6% |

Uma comparação de vizinhança através das fronteiras alcança, portanto, entre 4% e 23% do domínio não coberto pelos testes anteriores, conforme o raio aceito. O restante depende de modelos espaciais com coeficientes variáveis.

### 4.2 Autocorrelação espacial global (índice de Moran)

| Variável por local | I de Moran |
|---|---|
| Proporção de Lula no 2º turno | 0,853 |
| Brancos e nulos para presidente no 2º turno | 0,563 |
| Resíduo do modelo de composição legislativa com efeito fixo de UF | 0,639 |
| Fração de seções com urna antiga no local | 0,863 |

Todos os valores têm z acima de 360. O modelo não espacial deixa resíduos fortemente agrupados no território, e a distribuição das urnas antigas é ela mesma espacialmente agrupada. As duas coisas juntas configuram confundimento espacial: qualquer coeficiente da urna estimado sem estrutura espacial adequada mistura efeito do equipamento e efeito do lugar.

### 4.3 Primeira estimação espacial do efeito da urna

Modelo: proporção de Lula por local em função da fração de urnas antigas, da composição partidária do voto a deputado federal e do efeito fixo de UF.

| Especificação | Coeficiente da fração de urnas antigas | Estatística |
|---|---|---|
| Mínimos quadrados sem estrutura espacial | +3,28 pontos | t = 36 |
| Defasagem espacial (SLM, GM_Lag), ρ = 0,38 | +2,10 pontos | z = 28 |
| Erro espacial (GM_Error_Het), λ = 0,85 | +1,34 pontos | z = 11,5 |
| Referência: mesmo local de votação, com composição legislativa | +0,01 ponto | t = 0,13 |

Cada estrutura espacial adicionada reduz o coeficiente, mas os modelos globais de coeficiente constante ficam longe da referência obtida dentro do prédio. O coeficiente positivo desses modelos é um indício; o seu destino depende da calibração descrita na fase F4a. A diferença entre +1,34 e +0,01 mede o viés que resta num modelo espacial que supõe taxas de transferência iguais em todo o país, exatamente a limitação que o capítulo 7 aponta e que a regressão geograficamente ponderada e o método de expansão tratam.

## 5. Projeto da análise

### F1. Base espacial

Tabela única por local de votação com coordenadas (Hidalgo, com `conf_dist_km`), validação ponto-no-polígono, votos dos dois turnos por candidato e por partido em cada cargo, brancos e nulos, aptos, comparecimento, fração de urnas antigas, sessões de carga e flashcards, eleitores liberados sem biometria e horários. Tesselação de Voronoi recortada para as variáveis de área. Matrizes de vizinhança em três versões (k vizinhos, faixa de distância e contiguidade de Voronoi) para teste de sensibilidade, seguindo a recomendação do livro de preferir medidas de distância.

### F2. Exploração espacial

Índice de Moran global e indicadores locais (LISA) para proporção de Lula, invalidação, fração de urnas antigas e resíduos do modelo legislativo; estatística Gi* de Getis-Ord para pontos quentes. Mapas por estado. O produto é a localização dos agrupamentos de resíduos e a verificação de se eles coincidem com fronteiras de alocação das urnas, com sessões de carga ou com geografia contínua.

### F3. Invalidação diferencial com controle espacial (caps. 6 e 7)

Variável dependente: taxa de brancos e nulos para presidente por local. Variáveis explicativas: proporção de Lula, fração de urnas antigas e a interação entre as duas. Sequência do livro: regressão binomial e beta-binomial (sobredispersão), modelo de defasagem espacial, expansão de Casetti, regressão geograficamente ponderada e o método combinado de defasagem e expansão (SLEM), que é o que o autor indica para teste de hipótese. A pergunta é dupla: se a invalidação depende do candidato apoiado, depois de controlada a geografia, e se essa dependência muda com o modelo de urna. O indício I7 (mais brancos e nulos nas urnas antigas dentro da zona) já foi atribuído à alocação onde há comparação dentro do prédio; esta fase estende o exame ao domínio sem comparação interna.

### F4. Efeito da urna com controle espacial

**F4a. Calibração do método.** Antes de aplicar qualquer modelo espacial ao domínio sem comparação interna, ele é aplicado às zonas mistas, onde o resultado de referência é conhecido pelo teste dentro do prédio (≈ 0). Um modelo que não reproduz essa referência não é usado para concluir nada fora dela. Nenhum modelo espacial é considerado válido sem passar por esta etapa.

**F4b. Regressão geograficamente ponderada e SLEM.** Taxas de transferência do voto legislativo para o presidencial variando continuamente no espaço; coeficiente da urna antiga testado sobre esse fundo.

**F4c. Comparação de vizinhança através das fronteiras.** Pares de locais a até 5, 10 e 20 km, de modelos de urna diferentes e em municípios diferentes, condicionados à composição legislativa de cada um. É o análogo espacial do teste dentro do prédio e alcança de 4% a 23% dos votos do domínio sem comparação interna.

**F4d. Poder.** Fraudes sintéticas injetadas nas urnas antigas dos municípios sem comparação interna, com a mesma bateria de testes, para medir a menor fraude detectável nesse domínio.

### F5. Anomalias locais e fatores humanos

Agrupamento espacial dos resíduos cruzado com sessão de carga, flashcard, proporção de eleitores liberados sem biometria e horários de abertura e encerramento. O produto é a lista de unidades sinalizadas por critério pré-registrado, conforme o protocolo de auditoria.

### Regras de decisão

Cada teste é registrado antes da execução, com estatística, unidade, vizinhança, limiar e correção para comparações múltiplas. A terminologia segue a do projeto: toda distorção real e significativa é um **indício**; o indício é **discriminante** quando a sua relação causal com a urna sobrevive à calibração F4a, aos controles negativos e à confirmação em amostra independente; é **forte** quando converge com indícios independentes (carga, fatores humanos); e a **prova** exige coincidência com registro independente do software. Cada indício recebe um de três destinos: atribuído à alocação, atribuído à fraude ou indeterminado.

## 6. Limites conhecidos

O erro das coordenadas é pequeno na mediana, mas não desprezível em áreas rurais; os resultados serão repetidos excluindo locais com `conf_dist_km` acima de 1 km. A escolha da matriz de vizinhança e a escala de agregação afetam os coeficientes, e por isso entram como teste de sensibilidade. A regressão geograficamente ponderada não tem teste de hipótese nativo, e o SLEM depende da forma funcional correta, ambos limites reconhecidos por Forsberg. Nenhuma análise espacial alcança o conjunto M5 (manipulação dispersa, comum a todos os modelos e capaz de reconhecer o teste de integridade), que permanece indeterminado com os registros de 2022.

## 7. Ferramentas

Python com `geopandas`, `shapely`, `pyarrow`, `libpysal`, `esda`, `spreg` e `mgwr`, já instalados e testados neste ambiente; os mesmos pacotes rodam no Cursor. As bases geográficas da seção 3.1 são baixadas por `scripts/00_baixar_dados.py`.
