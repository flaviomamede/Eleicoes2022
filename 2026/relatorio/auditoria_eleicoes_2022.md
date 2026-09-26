# Auditoria estatística das contagens — Eleições 2022

**Autor:** Flávio Mamede Pereira Gomes  
**Data:** 26 de setembro de 2026  
**Escopo:** 1º e 2º turnos da eleição presidencial; boletins de urna do TSE; modelo de urna por seção (logs TSE / projeto John Robson); coordenadas de locais (Hidalgo v0.16); polígonos municipais (geobr).  
**Referências metodológicas:** Cochran–Mantel–Haenszel; regressão ecológica (Goodman); Forsberg, *Understanding Elections through Statistics* (CRC, 2021), caps. 6–7.

---

## Sumário executivo

Há diferença agregada entre a proporção de votos de Lula e Bolsonaro nas urnas anteriores a 2020 e nas urnas UE2020. Esse contraste é um **indício real**. Neste relatório ele é atribuído à **alocação dos equipamentos** (capitais e cidades maiores receberam UE2020; o interior, em maior medida, urnas antigas), e não a manipulação do software por modelo de urna.

Nos **1.353 locais de votação** do país que tiveram os dois modelos lado a lado, descontada a composição do voto a deputado federal de cada seção, a diferença entre modelos é de **+0,01 ponto percentual** (t = 0,13). O mesmo aparelho detectaria, com folga, a transferência de 1% dos votos de Bolsonaro nas urnas antigas de São Paulo.

A calibragem objetiva dos scores do site VotoReal confirma que a regra aprendida nas UE2020 **não se reproduz** nas urnas antigas da mesma UF (proposição R2). Os controles T1/T2 mostram que esse desajuste se comporta como contraste **geográfico** (capital × interior), não como efeito de marca (R4 refutada neste desenho).

A análise espacial (Forsberg cap. 7) mostra autocorrelação forte do voto, da invalidação e da própria alocação de urnas. Modelos espaciais de coeficiente constante reduzem, mas não eliminam, o viés espacial; a referência intramunicipal permanece o padrão-ouro onde há comparação interna. Permanecem em aberto: municípios só com urnas antigas (cerca de 44% dos votos válidos), objeto da análise geográfica em curso; e o mecanismo M5 (manipulação dispersa comum a todos os modelos), indeterminado com os registros de 2022.

**Conclusão para o leitor:** com os dados e os testes deste relatório, **não há prova de fraude** por modelo de urna, e os indícios examinados foram atribuídos à alocação (exceto I8, ainda a examinar em Roraima).

---

## 1. Conceitos e fundamentos

### 1.1 Indício, indício discriminante e prova

![Protocolo](figuras/10_esquema_protocolo.png)

*Figura 1 — Do indício ao destino (protocolo de auditoria).*

Neste trabalho os termos seguem o sentido do direito brasileiro (CPP art. 239; CPPM arts. 382–383), e não o inglês *evidence*:

| Nível | Critério |
|-------|----------|
| **Indício** | Distorção real e significativa relacionada ao fato |
| **Indício discriminante** | A relação causal com a urna sobrevive ao teste de mesmo local, aos controles negativos e à confirmação |
| **Indício forte** | Discriminante e convergente com indícios independentes (carga, flashcard, fatores humanos) |
| **Prova** | Forte e coincidente com registro independente do software |
| **Exclusão de mecanismo** | Teste com poder ≥ 90% para fraude capaz de alterar o resultado, sem sinal |

Cada indício recebe um de três destinos: **atribuído à alocação**, **atribuído à fraude** ou **indeterminado**.

### 1.2 Confundimento espacial (P0)

O modelo de urna não foi sorteado. As UE2020 concentram-se em capitais e municípios maiores; as antigas, no interior. Dentro das zonas, a alocação ainda corre por prédio de votação. Qualquer contraste bruto entre marcas mistura **lugar** e **equipamento**.

![Mapas Lula e urnas](figuras/08_mapa_lula_e_urnas.png)

*Figura 2 — Geografia do voto (Lula, 2º turno) e da alocação (fração de urnas antigas), por município. Os dois mapas não são independentes.*

### 1.3 Taxas de transferência e scores

A ideia por trás dos scores do VotoReal é uma **tabela de transferência**: dado o voto em deputado (ou partido), que fração “iria” a Bolsonaro ou a Lula. A calibragem objetiva estima essas taxas por regressão ecológica restrita **somente nas seções UE2020** de cada UF e aplica a mesma tabela às seções com urna antiga. O erro relativo resultante mede desajuste de domínio — não, por si, fraude.

### 1.4 Invalidação diferencial (Forsberg, cap. 6)

Sob a hipótese de eleição livre e justa, a taxa de brancos e nulos deve ser **independente** do apoio ao candidato. Relação significativa entre invalidação e apoio é evidência de *unfairness* (que pode ser fraude, desenho de cédula, alfabetização, demografia). O cap. 7 exige controle espacial porque o voto é autocorrelacionado.

![Invalidação](figuras/09_mapa_invalidacao.png)

*Figura 3 — Taxa de brancos+nulos (2º turno) por município.*

### 1.5 Autocorrelação espacial (Forsberg, cap. 7)

![Moran](figuras/04_moran.png)

*Figura 4 — Índice de Moran global (8 vizinhos mais próximos) nos ~92 mil locais de votação. Valores altos e z > 360: voto, invalidação, resíduos legislativos e alocação de urnas estão espacialmente agrupados.*

---

## 2. Dados e unidade de análise

| Fonte | Uso |
|-------|-----|
| Boletins de urna TSE (`bweb_*`) → base larga `secoes_2022_t{1,2}` | 472.028 seções; totais Lula/Bolsonaro batem com a referência oficial |
| Modelo de urna por seção (logs TSE / John Robson) | UE2020 (= Positivo) vs anteriores (= Diebold, em regra) |
| Hidalgo `geocode_br_polling_stations` v0.16 | Coordenadas de ~92,3 mil locais; 99,1% dentro do município IBGE |
| geobr municípios 2022 | Polígonos; validação ponto-no-polígono |

Unidades usadas neste relatório: **seção**, **local de votação** (prédio), **município**, **UF**.

---

## 3. Hierarquia de contrastes: o efeito encolhe

![Hierarquia](figuras/03b_hierarquia_efeitos.png)

*Figura 5 — Efeito associado à urna antiga (pontos percentuais a favor de Lula) em sucessivos níveis de controle.*

| Nível | Efeito (pp) | Leitura |
|-------|------------:|---------|
| Dentro da zona (Brasil, sem covariáveis) | +1,27 (t = 5,4) | Indício I2 |
| Mesmo local + composição legislativa | **+0,01 (t = 0,13)** | Comparação no prédio |
| MQO espacial (locais, k=8) | +3,29 | Ainda mistura geografia |
| Erro espacial (λ ≈ 0,85) | +1,39 | Reduz, não chega a 0,01 |

A diferença entre +1,39 (erro espacial global) e +0,01 (mesmo local) mede o viés que resta quando se força um coeficiente único no país — limitação que Forsberg aponta e que GWR/SLEM tratam.

---

## 4. Proposições: o que ficou estabelecido ou refutado

![Rede](figuras/07_rede_proposicoes.png)

*Figura 6 — Indicadores de verdade (0 = refutada; 1 = estabelecida).*

### 4.1 Relatório CMH / modelo de urna

| Nº | Proposição | Indicador | Fundamento |
|----|------------|----------:|------------|
| P0 | Modelo de urna entrelaçado com localização e perfil | **1,00** | Premissa confirmada em todos os níveis |
| P1 | Há correlação agregada modelo × voto | **1,00** | R bruto ≈ 1,15–1,17 |
| P2 | Há diferença intrazonal nacional | **1,00** | +1,27 pp, t = 5,4 |
| P2a | Essa diferença é homogênea no país | **0,03** | Concentrada em SP |
| P3 | p-valores CMH por voto são válidos como reportados | **0,00** | Dispersão; a rejeição de H0 sobrevive com a seção |
| P4 | Dentro das zonas, alocação independe do perfil | **0,00** | Negação de P0 |
| P4′ | No mesmo local, seções antigas e UE2020 são comparáveis | **0,85** | Controles negativos equilibrados |
| P5 | O modelo de urna **causou** a diferença | **0,03** | Nulo no prédio, com poder para 1% |
| P6a/b | Fraude detectable (≥ 1%) nas antigas | **0,02–0,03** | Nulo no prédio (Brasil e SP) |
| P6c | Intrazonal aponta efeito das antigas no Nordeste | **0,02** | Sinal contrário / nulo |
| P7 | Evidência equivalente a tabagismo–câncer | **0,00** | Analogia inválida |
| P10 | A diferença inverte o resultado | **0,00** | Magnitude intramunicipal ≪ margem |

### 4.2 Scores VotoReal

| Nº | Proposição | Indicador | Fundamento |
|----|------------|----------:|------------|
| R1 | Tabela subjetiva JR = taxas reais | **0,05** | Afasta-se em PP, Republicanos, PSOL, NOVO… |
| R2 | Regra UE2020 por UF erra nas antigas da mesma UF | **1,00** | Erro relativo estável 1º↔2º turno |
| R3 | Hold-out 70/30 valida extrapolação às antigas | **0,00** | Valida só dentro das Positivo |
| R4 | Erro de R2 = efeito de marca | **0,03** | T1 grande com mesma marca; T2 ≈ 0 |

### 4.3 Cauda de votação mínima

| Nº | Proposição | Indicador |
|----|------------|----------:|
| U1 | Mínimos de Bolsonaro nas antigas por efeito do modelo | **0,02** |
| U2 | Nas 27 seções do AM sem Bolsonaro, o voto destoa dos demais cargos | **0,00** |

### 4.4 Mecanismos M1–M5

| Mecanismo | Situação |
|-----------|----------|
| M1 Manipulação após a urna (totalização) | **Excluída** (soma dos BUs = resultado oficial) |
| M2 Transferência específica das urnas antigas (≥ 1% nos testados) | **Excluída** com poder demonstrado |
| M3 Manipulação concentrada na escala da margem | **Excluída** |
| M4 Dispersa sem reconhecer teste de integridade | **Excluída** (prob. ≥ 99,6% no desenho do pacote) |
| M5 Dispersa, comum a todos os modelos, reconhecendo o teste | **Indeterminada** |
| D-ext Só em municípios sem comparação interna | **Em aberto** (análise geográfica) |

---

## 5. Calibragem dos scores e controles T1/T2/T3

### 5.1 Contraste Positivo → Diebold por UF

![Contraste UF](figuras/01_contraste_uf_1t.png)

*Figura 7 — Δ de erro relativo (Diebold − Positivo) após calibrar nas UE2020. PB, AL, PE, AM, CE… ultrapassam 20–30% em Bolsonaro. SP, MG, DF ficam perto de zero.*

Atenção: nos estados de maior Δ, capital ≈ UE2020 e interior ≈ antigas. O Δ **mistura** capital/interior com eventual efeito de marca. Por isso os controles abaixo.

### 5.2 Scores subjetivos × calibrados

![Scores](figuras/06_scores_jr_vs_calibrado.png)

*Figura 8 — No eixo x, o score do site; no y, a taxa média calibrada (Dep. Federal, 1º turno). A diagonal é a concordância perfeita. PL e PT apontam o mesmo lado; PP, Republicanos, PSOL e NOVO afastam-se bastante.*

### 5.3 Controles: T1 grande, T2 colapsa

![T1 T2](figuras/02_controles_T1_T2.png)

*Figura 9 — **T1** (UE2020 capital → UE2020 interior): erros relativos grandes no NE, *com a mesma marca*. **T2** (UE2020 → antigas no mesmo município, ≥30+30 seções): 165 municípios (155 em SP); erro médio ≈ −0,9%.*

Leitura alinhada a Forsberg e à crítica metodológica: o padrão favorece a hipótese **geográfica**. R4 (erro = marca) não se sustenta neste desenho.

---

## 6. Análise geográfica (em curso)

### 6.1 Alcance além do prédio

![Proximidade](figuras/05_proximidade_fronteira.png)

*Figura 10 — Nos municípios só com urnas antigas, fração dos votos que têm um local UE2020 a ≤ r km em outro município. A 5 km: ~4%; a 20 km: ~23%. O restante exige modelo espacial ou permanece fora do análogo do “mesmo prédio”.*

### 6.2 Invalidação diferencial com espaço (F3)

![DI espacial](figuras/11_di_espacial_coefs.png)

*Figura 11 — Coeficiente do apoio a Lula sobre a taxa de brancos+nulos, com controle da fração de urnas antigas. Há associação estatística; os resíduos do modelo não espacial ainda têm Moran I ≈ 0,57. O efeito em escala de proporção é pequeno; o SEM linear indica variação forte do efeito com latitude/longitude. Interpretação causal (fraude vs demografia/alfabetização) exige a calibração F4a.*

### 6.3 Próximas etapas geográficas

1. **F4a** — Aplicar o modelo espacial onde a referência intramunicipal é ≈ 0; rejeitar especificações que não reproduzem essa referência.  
2. **F4b** — GWR e SLEM (Forsberg).  
3. **F4c** — Pares cross-border.  
4. **F4d** — Poder com fraudes sintéticas no domínio sem comparação interna.

---

## 7. Indícios examinados e destino

| Indício | Distorção | Destino | Fundamento resumido |
|---------|-----------|---------|---------------------|
| I1 Agregado entre modelos | R ≈ 1,17 por estado | **Alocação** | R ≈ 1,05 no município; UE2020 nas capitais |
| I2 Dentro da zona | +1,27 pp | **Alocação** | Concentrado em SP; nulo no local |
| I3 Resíduo paulista entre prédios | +0,26 pp | **Alocação** | Nulo dentro do prédio |
| I4 Erro da calibragem por UF | 20–30%+ no N/NE | **Alocação** | Placebo T1 UE2020 capital→interior |
| I5 27 urnas AM sem Bolsonaro | Real | **Alocação / alinhamento** | Municípios só antigas; coerência com outros cargos |
| I6 PL alto / Bolsonaro baixo | Real | **Alinhamento local** | PL Senado fraco nas mesmas seções |
| I7 Mais BN nas antigas (zona) | +0,28 pp | **Alocação** | No local: −0,07 pp |
| I8 R intramunicipal RR | R = 1,77 | **A examinar** | Falta teste por local |

---

## 8. Resposta à pergunta do leitor

**“Há indício de fraude ou não?”**

Com o que esta auditoria mede: **não há prova de fraude**, e **não há indício discriminante** a favor de manipulação por modelo de urna. Há indícios de diferença entre grupos de urnas; os examinados (exceto I8) foram **atribuídos à alocação**. Isso não encerra todo mecanismo imaginável (M5 e o domínio sem comparação interna permanecem abertos), mas responde, no sentido do debate sobre “urnas novas × antigas”, que os dados **não apontam** trapaça por marca de urna.

---

## 9. Artefatos e reprodução

| Pasta / arquivo | Conteúdo |
|-----------------|----------|
| `2026/analise/relatorio_calibragem.md` | Calibragem de scores (corrigenda) |
| `2026/analise/relatorio_base_e_controles.md` | Base larga + T1/T2/T3 |
| `2026/geografia/claude_opus55_externo/docs/` | Docs 01–07 (CMH, protocolo, scores, limites, geo) |
| `2026/envio_calibragem_scores_johnrobson_2026-09-26.zip` | Pacote enviado para atualização do site |
| `2026/scripts/gerar_figuras_relatorio.py` | Figuras deste relatório |
| `2026/geografia/.../scripts/06_espacial.py`, `07_di_espacial.py` | Pipeline espacial |

Reprodução geográfica (resumo):

```bash
cd 2026/geografia/claude_opus55_externo/scripts
python3 00_baixar_dados.py
python3 06_espacial.py
python3 07_di_espacial.py
```

---

## 10. Limitações

1. O teste de mesmo local não cobre municípios só com um modelo (~44% dos votos).  
2. Coordenadas têm erro residual (mediana baixa; excluir `conf_dist_km` > 1 km em sensibilidade).  
3. GWR não tem teste nativo; SLEM depende da forma funcional.  
4. M5 é estruturalmente indeterminado com os registros públicos de 2022.  
5. Taxas calibradas não somam 1 em Bolsonaro+Lula (há “Outros”); o site, se atualizar scores, precisa decidir a renormação.

---

*Relatório gerado no projeto `PROJETO_ELEICOES_JOHNROBSON/2026`. Figuras em `relatorio/figuras/`.*
