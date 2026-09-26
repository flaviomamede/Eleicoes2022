# Calibragem objetiva dos scores e contraste Positivo × Diebold

**Data:** 26/09/2026  
**Pasta:** `2026/`  
**Pergunta:** dá para estimar, a partir dos resultados, quanto do voto de cada partido “iria” para Bolsonaro e Lula — e essa regra é a mesma nas urnas novas (UE2020 / Positivo) e nas antigas (Diebold)?

---

## Corrigenda (mesmo dia, após leitura crítica)

1. **O que o Δ mede de fato.** A calibragem por UF, treinada nas Positivo e aplicada às Diebold, estabelece que a regra das UE2020 **não reproduz** as urnas antigas da mesma UF. Nos estados de maior Δ (PB, AL, PE, AM, CE…), capital ≈ UE2020 e interior ≈ urnas antigas: o Δ **mistura** diferença capital/interior com eventual efeito de marca e **não isola** a marca. Ver `notas/critica-opus-relatorio-calibragem.md`. Testes T1 (placebo capital→interior só com UE2020) e T2 (intramunicipal) ficam para a etapa seguinte.

2. **“Erro %” é relativo**, não pontos percentuais da proporção. Ex.: 28,1 mi reais contra 29,3 mi previstos ≈ −4,0% relativo. Onde o texto dizia “20–30 pontos percentuais”, leia-se **diferença de erro relativo da ordem de 20–30%** (ex.: Δ Bolsonaro PB ≈ −33% relativo).

3. **Hold-out 70/30** valida a regra *dentro* das Positivo; **não** valida a extrapolação às Diebold/interior.

4. **Contagens de seções** (1º turno neste relatório: 192.640 Positivo / 278.357 Diebold) divergem do VOTOS_T1E2 citado na crítica (191.317 UE2020 / 280.710 antigas). Há ~1,3 mil seções a reconciliar na base larga (provável: modelo ausente / grupo “Outro”).

5. Taxas partido a partido sem soma 1 (ex. PSOL→Bolsonaro alto) são frágeis; o contraste Positivo→Diebold por UF permanece como descrição de **desajuste de domínio**, não como prova de marca.

---

## Em uma frase

Estimamos a tabela de transferência **só nas urnas Positivo** de cada estado e a aplicamos nas Diebold. No Brasil, o erro relativo nas Diebold fica cerca de **−4%** em Bolsonaro e **+5–6%** em Lula frente ao previsto; em vários estados do Norte/Nordeste o Δ de erro relativo passa de **20–30%**.

Isso mostra desajuste entre a regra aprendida nas Positivo e o que se observa nas Diebold da mesma UF. **Não** separa, sozinho, efeito de marca e contraste capital/interior.

---

## O que foi feito (passo a passo)

1. **Dados do TSE** — Boletins de Urna Web (`bweb_*`) do 1º e 2º turno, todas as UFs + exterior (ZZ).
2. **Conversão** — cada zip → parquet compacto em `dados/buweb/` (votos por seção × partido × cargo + modelo de urna).
3. **Calibragem** — regressão ecológica restrita (taxas entre 0% e 100%), estado a estado, **apenas nas seções Positivo**.
4. **Teste** — a mesma tabela é aplicada nas seções **Diebold** daquele estado; medimos o erro (voto real − voto previsto).
5. **Validação** — em 70% das zonas Positivo treinamos; nas 30% restantes prevemos (hold-out).

Referência metodológica: Goodman (anos 1950) + desenho discutido em `notas/comentario-opus-55-calibragem.md`.

### Premissa (importante)

Usamos os votos de **deputado federal** (e, no 1º turno, também estadual e governador) como espelho do perfil político da seção. Isso só faz sentido se esses cargos forem uma referência mais estável que o presidente — ou, no mínimo, se o interesse for comparar os **dois grupos de urna** sob a mesma regra.

---

## Dados processados

| Item | Situação |
|------|----------|
| Zips TSE baixados | 56 (28 × 1º turno + 28 × 2º turno) |
| Parquets 1º turno | 28 UFs (+ ZZ) |
| Parquets 2º turno | 28 UFs (+ ZZ) |
| Seções no 1º turno | ~472 mil |
| Join BU × modelo de urna | tipicamente ~100% (ex.: AC diferença 0 nos totais presidente) |

Arquivos principais: `dados/buweb/{uf}_{1t\|2t}_*.parquet`.

---

## Resultado Brasil

Calibragem nas Positivo; aplicação nas duas marcas. Cargo de referência: **Deputado Federal**.

### 1º turno

| Marca | Urnas | Bolsonaro real | Bolsonaro previsto | Erro % | Lula real | Lula previsto | Erro % |
|-------|------:|---------------:|-------------------:|-------:|----------:|--------------:|-------:|
| Positivo | 192.640 | 22,8 mi | 22,8 mi | **+0,1%** | 23,5 mi | 23,6 mi | **−0,4%** |
| Diebold | 278.357 | 28,1 mi | 29,3 mi | **−4,0%** | 33,6 mi | 31,7 mi | **+5,9%** |

Leitura: nas Positivo o modelo acerta (foi treinado nelas). Nas Diebold, Bolsonaro fica **abaixo** do previsto e Lula **acima**.

### 2º turno

(Aqui os partidos vêm do **1º turno** na mesma seção; o presidente é o do **2º**.)

| Marca | Urnas | Erro % Bolsonaro | Erro % Lula |
|-------|------:|-----------------:|------------:|
| Positivo | 192.691 | **+0,4%** | **−0,1%** |
| Diebold | 278.314 | **−4,0%** | **+4,9%** |

O padrão nacional se repete no 2º turno.

---

## Por estado: quanto muda ao trocar Positivo → Diebold

**Δ** = erro% nas Diebold **menos** erro% nas Positivo.  
Negativo em Bolsonaro = Diebold com menos Bolsonaro do que a regra Positivo esperava.  
Positivo em Lula = Diebold com mais Lula do que o esperado.

| UF | Δ Bolsonaro 1º | Δ Lula 1º | Δ Bolsonaro 2º | Δ Lula 2º |
|----|---------------:|----------:|---------------:|----------:|
| PB | −32,8 | +16,9 | −32,4 | +16,5 |
| AL | −31,2 | +28,4 | −30,7 | +30,2 |
| PE | −29,0 | +16,8 | −28,6 | +17,2 |
| AM | −28,0 | +31,3 | −29,2 | +35,9 |
| RN | −21,8 | +11,7 | −21,1 | +11,1 |
| SE | −21,4 | +13,7 | −23,3 | +11,9 |
| MA | −20,8 | +10,1 | −22,3 | +8,2 |
| CE | −20,6 | +9,0 | −21,0 | +8,9 |
| GO | −15,5 | +36,0 | −15,6 | +30,6 |
| BA | −10,6 | +6,4 | −11,2 | +5,8 |
| AP | −10,5 | +18,3 | −14,6 | +9,6 |
| RR | −10,0 | +26,0 | −16,9 | +17,4 |
| AC | −5,9 | +23,1 | −14,0 | +5,9 |
| RS | −5,7 | +11,4 | −5,2 | +8,1 |
| TO | −4,8 | +4,7 | −4,9 | +3,1 |
| DF | −1,1 | +1,5 | −0,9 | +1,1 |
| PI | −1,1 | +0,7 | −2,3 | +0,8 |
| SP | −1,0 | +2,1 | −0,9 | +1,7 |
| RJ | +0,5 | +5,3 | −0,1 | +1,5 |
| ES | +1,2 | −0,9 | +1,0 | −1,6 |
| MG | +1,3 | +1,0 | −0,1 | +1,0 |
| MS | +2,7 | +7,0 | −0,4 | +1,1 |
| SC | +3,0 | +0,3 | +2,6 | −3,6 |
| PR | +4,1 | +0,1 | +3,7 | −3,0 |
| RO | +4,6 | −4,4 | +4,0 | −4,3 |
| PA | +14,0 | −7,2 | +14,0 | −9,3 |
| MT | +14,1 | −18,0 | +15,2 | −16,7 |

Estados com Δ perto de zero (SP, MG, DF, PI…): a regra Positivo descreve bem as duas marcas.  
Estados com Δ grande e no mesmo sentido nos dois turnos (PB, AL, PE, AM, CE…): o contraste é **estável**.

Figuras:  
- `figuras/contraste_partido_1t_deputado_federal.png`  
- `figuras/contraste_partido_2t_dep_federal_1t.png`

---

## A regra acerta dentro das Positivo? (hold-out)

Em cada UF, treinamos em 70% das zonas Positivo e prevemos as outras 30%.

| Turno | Erro % médio Bolsonaro (teste) | Erro % médio Lula (teste) |
|-------|-------------------------------:|--------------------------:|
| 1º | ~0,0 | ~−1,5 |
| 2º | ~0,4 | ~−0,8 |

Na média o hold-out fica perto de zero (bom sinal). Há UFs com erro maior — a qualidade do ajuste **varia por estado**; por isso a calibragem é por UF, não nacional.

---

## Scores do John Robson × taxas calibradas

A tabela do site é **hipótese subjetiva**. A calibragem **extrai** taxas da variação entre seções Positivo (média entre UFs, 1º turno, Dep. Federal).

| Partido | Score JR → Bolsonaro | Taxa calibrada | Diferença | Score JR → Lula | Taxa calibrada | Diferença |
|---------|---------------------:|---------------:|----------:|----------------:|---------------:|----------:|
| PL | 100% | 82% | −18 | 0% | 14% | +14 |
| PP | 92% | 50% | −41 | 8% | 40% | +31 |
| REPUBLICANOS | 92% | 43% | −48 | 8% | 47% | +38 |
| PSC | 90% | 70% | −20 | 10% | 23% | +13 |
| PTB | 85% | 79% | −6 | 15% | 15% | 0 |
| NOVO | 58% | 85% | +27 | 42% | ~0% | −42 |
| MDB | 50% | 42% | −8 | 50% | 44% | −6 |
| PDT | 50% | 30% | −20 | 50% | 48% | −2 |
| UNIÃO | 50% | 53% | +3 | 50% | 34% | −16 |
| PT | 0% | 9% | +9 | 100% | 86% | −14 |
| PSOL | 8% | 49% | +40 | 92% | 39% | −53 |

### Como ler isso com cuidado

- Nos extremos (PL, PT) a calibragem e o JR apontam o mesmo lado.
- Em partidos médios/pequenos (PSOL, NOVO, REPUBLICANOS…) a regressão ecológica **mistura** o efeito do partido com o do “vizinho” na mesma urna. Taxas individuais podem ficar estranhas; o teste **Positivo → Diebold** continua válido porque usa a **mesma** tabela nos dois grupos.
- O JR força Bolsonaro+Lula=100% e zera Ciro/Tebet no 1º turno; a calibragem tem coluna “Outros” e não exige que as taxas somem 1 (ajuste coluna a coluna). Versões futuras podem impor soma 1 por linha.

CSV: `analise/comparacao_scores_jr_vs_calibrado_1t_df.csv`.

---

## Outros cargos (1º turno)

O mesmo exercício com **Deputado Estadual** e **Governador** dá o mesmo padrão nacional: Positivo ~0% de erro; Diebold cerca de −3 a −4% Bolsonaro e +5 a +6% Lula. O sinal não depende de um único cargo.

---

## O que isto responde — e o que não responde

**Responde**

- Dá para calibrar scores de forma objetiva (por UF).
- A regra das Positivo, por UF, não reproduz as Diebold da mesma UF (erro relativo estável 1º↔2º turno nos estados de maior Δ).
- A tabela subjetiva do JR se afasta da calibrada sobretudo em PP/Republicanos.

**Não responde sozinho**

- Se o Δ é efeito de **marca** ou de **capital/interior** (domínios quase disjuntos nos estados líderes) — exige T1 e T2.
- Se a causa é fraude ou outro mecanismo.
- Qual seria o placar se todas as urnas fossem UE2020.

---

## Onde estão os artefatos

| Caminho | Conteúdo |
|---------|----------|
| `dados/buweb/` | Parquets por UF e turno |
| `dados/bweb_*.zip` | Zips originais TSE |
| `analise/residuos_brasil_partido_*.csv` | Totais Brasil |
| `analise/contraste_partido_*.csv` | Δ por UF |
| `analise/taxas_partido_*.csv` | Taxas por partido × UF |
| `analise/holdout_partido_*.csv` | Validação fora da amostra (domínio Positivo) |
| `figuras/contraste_partido_*.png` | Gráficos UF |
| `notas/critica-opus-relatorio-calibragem.md` | Crítica e especificação T1–T3 |
| `scripts/processar_bweb.py` | Zip → parquet |
| `scripts/calibragem_partido_pres.py` | Calibragem 1º turno |
| `scripts/calibragem_2t_via_1t.py` | Calibragem 2º turno |

---

## Próximos passos (ajustados)

1. **Base larga por seção** (`dados/base_secoes/`) — entrega principal.  
2. Calibragem com **blocos** partidários e soma 1.  
3. Controles **T1** (UE2020 capital→interior), **T2** (intramunicipal), **T3** (antiga→UE2020).  
4. Reconciliar contagem Positivo/Diebold com VOTOS_T1E2.

---

*Processamento e contas gerados nesta pasta `2026/` a partir dos Boletins de Urna do TSE e da base de modelo de urna do projeto John Robson.*
