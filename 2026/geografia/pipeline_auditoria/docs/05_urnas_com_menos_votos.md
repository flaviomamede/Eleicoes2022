# 05 — Urnas com votação mínima de Bolsonaro

Script: `scripts/05_cauda_votos_minimos.py`. Resultados: `resultados/cauda_*.csv`.

## 1. A página do site

A página "Urnas com Menos Votos" do votoreal lista, por estado, turno e modelo de urna, as urnas em que Bolsonaro teve até dez votos, ao lado da votação estimada para a direita a partir dos scores partidários. No Amazonas, no 1º turno, o site mostra 27 urnas antigas com zero voto em Bolsonaro e 233 com até dez votos, contra 4 urnas UE2020 com até nove votos. Os testes anteriores mediram diferenças médias; a cauda exige teste próprio, porque uma fraude concentrada em poucas urnas poderia escapar a testes de média.

## 2. Amazonas

Os números do site conferem: 27 seções com urna antiga e nenhum voto em Bolsonaro, onde Lula somou 4.794 votos. Todas as 3.151 seções UE2020 do Amazonas ficam em Manaus. As 27 seções estão em 12 municípios onde 100% das urnas eram antigas (entre eles São Gabriel da Cachoeira, Atalaia do Norte, São Paulo de Olivença, Tabatinga, Santo Antônio do Içá, Parintins e Barreirinha), regiões de comunidades indígenas e ribeirinhas. No Amazonas, a comparação entre marcas é uma comparação entre Manaus e o interior.

A estimativa de 2.309 votos à direita decorre dos scores. Nessas seções, o voto para deputado federal foi sobretudo para PSD, União e Republicanos, com 1,1% do comparecimento para o PL. O site atribui a Bolsonaro 50% dos votos de PSD e União e 92% dos do Republicanos; em 2022, o PSD do Amazonas estava no palanque de Lula (o senador Omar Aziz fez campanha por Lula). Com taxas estimadas a partir dos dados do próprio estado, a expectativa cai para 814 votos, e a distância restante até zero reflete a diferença entre uma média estadual e a votação quase unânime de comunidades isoladas.

Os demais cargos registrados pelas mesmas urnas confirmam o quadro:

| Voto (% do comparecimento) | Nas 27 seções | No Amazonas |
|---|---|---|
| PL para deputado federal | 1,1 | 11,1 |
| PL para o Senado | 0,5 | 34,9 |
| PSD para o Senado (Omar Aziz) | 76,9 | 37,1 |
| MDB para governador (Eduardo Braga, aliado de Lula) | 40,6 | 19,0 |
| União para governador (Wilson Lima, aliado de Bolsonaro) | 43,8 | 38,8 |

Uma manipulação restrita ao voto presidencial não retiraria do PL os votos para senador e deputado.

## 3. Brasil

No 1º turno, 160 seções deram zero voto a Bolsonaro; 146 estão em municípios que só tinham urnas antigas. Seções com Bolsonaro até 2% dos votos válidos, por mil seções:

| Recorte | UE2020 | Urnas antigas |
|---|---|---|
| Municípios com os dois modelos | 0,22 | 0,15 |
| Locais de votação com os dois modelos | 0 | 0 |
| Municípios só com urnas antigas | — | 3,26 |
| Municípios só com UE2020 | 0,89 | — |

Há ainda 1.346 seções com Bolsonaro abaixo de 10% no 2º turno e PL acima de 20% do comparecimento para deputado federal no 1º turno, concentradas no Maranhão (606), no Ceará (443) e na Bahia (188). Nelas, o PL teve em média 38,7% para deputado e 1,8% para o Senado: são redutos de deputados locais, coerentes no voto para senador. Nos municípios com os dois modelos, esse padrão ocorre em 0,75 por mil seções UE2020 e em 0,02 por mil seções com urna antiga.

## 4. Conclusão

A concentração de votações mínimas de Bolsonaro nas urnas antigas acompanha o tipo de município, e não o modelo: dentro do mesmo município, as UE2020 registram tantas votações mínimas quanto as antigas, ou mais. Nas 27 seções do Amazonas, o voto presidencial é coerente com os demais cargos da mesma urna. Uma fraude que alterasse de forma coordenada presidente, senador, governador e deputados fica fora do alcance deste método e do método do site, que usa esses cargos como referência.
