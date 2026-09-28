# Forsberg (2021) — notas Caps. 6–8

**Livro:** Ole J. Forsberg, *Understanding Elections through Statistics* (CRC, 2021). O PDF e os extratos integrais não ficam neste repositório.

Contexto do livro (Parte II): testar *unfairness* eleitoral com dados oficiais. Cap. 5 = só contagens (Benford). Cap. 6 = + votos nulos/invalidação. Cap. 7 = + geografia. Cap. 8 = aplicação Sri Lanka.

---

## Cap. 6 — Differential Invalidation (pp. 125–148)

**Ideia:** sob hipótese “livre e justa”, a taxa de invalidação deve ser **independente** do apoio ao candidato. Relação significativa entre `pInv` e `pSup` (por divisão eleitoral) = evidência de *differential invalidation* (ou viés sistêmico equivalente — não prova fraude sozinha).

**Dados por divisão:** votos do candidato, nulos/invalidos, total de votantes.

**Quatro regressões** (mesma pergunta H0: β₁ = 0):

| Método | Função R (essência) | Observação |
|--------|---------------------|------------|
| OLS | `lm(pInv ~ pSup)` | simples; residual normal + homocedasticidade frágeis |
| WLS | `lm(..., weights = turnout)` | corrige heteroscedasticidade π(1−π)/N |
| Quasi-binomial GLM | `glm(cbind(inv,val) ~ pSup, quasibinomial)` | conta + overdispersion |
| Beta-binomial VGLM | `vglm(..., family=betabinomial)` (VGAM) | preferido no livro |

**Tom:** p-valor = evidência contra independência; **não** concluir “fraude” (ballot design, alfabetização, demografia também geram inclinação). Exemplo Côte d’Ivoire 2010 (CEI): curvas planas → sem evidência de DI nos dados oficiais.

---

## Cap. 7 — Considering Geography (pp. 149–176) ← **reproduzir**

**Caso de trabalho:** referendo constitucional Egito 2011, **n = 27 governorates**.  
Y = taxa de invalidação; X = apoio ao “Sim”; coordenadas das capitais; pesos por **distância** (não rook/queen — aumenta N efetivo e evita ilhas).

### 7.1 Correlação espacial
- Matriz de vizinhança **W** (contiguity ou 1/distância; diagonal 0).
- **Moran’s local Iᵢ** em Y, em X e nos **resíduos** do Cap. 6.
- Se resíduos têm Moran significativo → OLS/GLM do Cap. 6 **violam independência**.

Egito: poucos hotspots em suporte/invalidação; após quasi-binomial, resíduos com correlação espacial forte no delta (+) e Cairo/Giza (−). Conclusão Cap. 6 frágil sem geografia.

### Quatro modelos espaciais

1. **Spatial Lag Model (SLM)**  
   `Y = ρ W* Y + Xβ + ε`  
   `W*` = W com linhas normalizadas; `contagion = W* %*% y`.  
   Egito: contagion e suporte **não** significativos; reduz um pouco a estrutura espacial, mas assume efeitos **constantes** no mapa.

2. **Casetti Spatial Expansion (SEM)**  
   `β₀(u,v)`, `β₁(u,v)` polinomiais em lat/long.  
   Egito: quadrático overfit; linear em north/west → efeito norte–sul estatisticamente detectável, **praticamente** pequeno (~0,5 pp de base).

3. **Geographically Weighted Regression (GWR)**  
   Kernel (Gaussiano) + bandwidth (AIC → 203 km no exemplo); `spgwr`.  
   Efeitos locais por ponto; mapas bonitos; **sem** testes nativos de hipótese (df indefinidos). Exploratório.

4. **Spatial Lagged Expansion (SLEM)** — favorito do autor  
   `yi = ρ(u,v) y(i) + β₀(u,v) + β₁(u,v) xi + εi`  
   Combina lag + expansão; ainda cabe em lm/glm/vglm → **testes** possíveis.  
   Egito: AIC melhor que OLS/SEM/GWR; mapas de efeito base / contagion / suporte; sugere processo diferente em Matruh (noroeste) e Mar Vermelho.

**Ordem prática sugerida pelo livro:** Moran nos resíduos → SLM/SEM → SLEM (teste) → GWR (mapa exploratório).

---

## Cap. 8 — Sri Lanka 1994–2019 (pp. 177–194)

Aplicação Cap. 6 (beta-binomial), geografia sobretudo ilustrativa.  
n ≈ 160 divisões; remove norte Tamil + postal/deslocados para isolar DI “além” do viés étnico.  
Resultado: efeito negativo do apoio ao candidato do governo sobre invalidação em quase todas as eleições (2015 limítrofe sem norte; significativo com Jaffna/Vanni). Interpretação: unfairness persistente beneficiante o governo — **não** reconstrução do placar “verdadeiro”.

---

## O que precisamos para reproduzir o Cap. 7 (Brasil / 2022)

O Cap. 7 **não** é sobre modelo de urna; é invalidação × apoio + espaço. Adaptável:

| Ingrediente Forsberg | Análogo BR 2022 |
|----------------------|-----------------|
| Divisão eleitoral | município, zona ou seção (agregar) |
| Invalidação | brancos+nulos (ou só nulos) / comparecimento |
| Apoio | Lula ou Bolsonaro / votos válidos |
| (u,v) | centroide município / sede |
| W | 1/distância entre centroides (UF ou Brasil) |
| Shapefile | IBGE / GADM (livro cita GADM) |

**Pipeline mínimo Cap. 7:**
1. Agregar `base_secoes` → município (ou zona).
2. `pInv`, `pSup`, lat/lon.
3. Moran local nos resíduos de `quasibinomial(inv ~ pSup)`.
4. SLM → SEM linear → SLEM; GWR opcional para mapa.
5. Relatar: evidência de DI espacialmente estruturada? efeitos constantes?

**Pacotes R citados:** `VGAM`, `spgwr`; equivalente Python: `statsmodels` GLM + `libpysal`/`esda` (Moran) + `spreg` / GWR via `mgwr`.

**Dados do livro (Egito):** não vêm no PDF; referências [130] etc. Para *reproduzir o método*, BR com nossa base basta; para *reproduzir o exemplo Egito*, falta baixar os CSV/shapefiles das refs.
