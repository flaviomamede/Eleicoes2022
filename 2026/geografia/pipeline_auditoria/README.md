# Eleicoes2022_2026 — Auditoria estatística das contagens das eleições de 2022

**Autor:** Flávio Mamede Pereira Gomes · **Início:** setembro de 2026

Este repositório reúne a revisão e a extensão, em 2026, das análises estatísticas publicadas após as eleições presidenciais de 2022 sobre a contagem de votos por modelo de urna: o relatório do autor com o teste de Cochran–Mantel–Haenszel (publicado no repositório JohnRobson/Eleicoes2022) e as análises de contagem do site votoreal.org, de John Robson. O trabalho segue um protocolo de auditoria: cada distorção encontrada nos dados é tratada como indício, testada contra explicações alternativas com controles negativos e com fraudes simuladas que medem o poder de detecção, e classificada como atribuída à alocação, atribuída à fraude ou indeterminada.

## Conclusões atuais

A proporção de votos de Lula e Bolsonaro difere entre urnas anteriores a 2020 e urnas UE2020, e essa diferença é um indício real. A análise a atribui à alocação dos equipamentos: as UE2020 foram instaladas sobretudo nas capitais e cidades maiores, e as urnas antigas no interior, com distribuição por prédio de votação dentro das zonas. Nos 1.353 locais de votação do país que tiveram os dois modelos lado a lado, descontada a composição do voto a deputado de cada seção, a diferença entre modelos é de +0,01 ponto percentual (t = 0,13), com poder demonstrado para detectar a transferência de 1% dos votos de Bolsonaro nas urnas antigas de São Paulo. As votações mínimas de Bolsonaro apontadas pelo site votoreal são coerentes com os demais cargos votados nas mesmas urnas. Não há prova de fraude nos dados examinados. Permanecem em aberto os municípios que só tiveram urnas antigas (44% dos votos), objeto da análise geográfica em curso, e o conjunto de mecanismos que nenhuma análise de resultados alcança, descrito no documento 06.

## Estrutura

```text
docs/        documentos da auditoria (01 a 07)
scripts/     pipeline em Python (00 a 06) e módulo comum
resultados/  tabelas geradas pelos scripts (versionadas)
dados/       dados brutos e intermediários (não versionados; ver dados/LEIA-ME.md)
```

| Documento | Conteúdo |
|---|---|
| `docs/01_revisao_relatorio_CMH.md` | Reprodução e revisão do relatório CMH do 2º turno |
| `docs/02_rede_de_proposicoes.md` | Proposições com indicadores de 0 a 1 |
| `docs/03_protocolo_de_auditoria.md` | Terminologia (indício e prova), protocolo e classificação dos indícios |
| `docs/04_analise_scores_votoreal.md` | Calibragem dos scores partidários do votoreal; texto para leitores |
| `docs/05_urnas_com_menos_votos.md` | Cauda de votação mínima e coerência entre cargos |
| `docs/06_limites_M1_a_M5.md` | O que os dados de 2022 permitem e não permitem verificar |
| `docs/07_analise_geografica_projeto.md` | Fontes geográficas, primeiros resultados espaciais e projeto |

## Como reproduzir

Requisitos: Python 3.12 e cerca de 4 GB de memória.

```bash
pip install -r requirements.txt
```

Coloque em `dados/` a base larga por seção (`secoes_2022_t1.parquet`, `secoes_2022_t2.parquet`; o `.csv.gz` também é lido, mas não é versionado) e a planilha `VOTOS_T1E2.xlsx` com o modelo de urna por seção (ver `dados/LEIA-ME.md`). A base larga é gerada a partir dos boletins de urna do TSE (`bweb_1t_*` e `bweb_2t_*`) pelo script `2026/scripts/gerar_base_secoes.py`. Em seguida:

```bash
cd scripts
python 00_baixar_dados.py          # bases geográficas e manifesto dos dados
python 01_modelo_urna.py           # modelo de urna por seção
python 02_cmh_reproducao.py        # Tabelas 1 a 3 do relatório e decomposição
python 03_secao_zona_local.py      # seção, zona, local, controles negativos, poder (~10 min)
python 04_calibragem_scores.py     # scores do votoreal e placebos
python 05_cauda_votos_minimos.py   # votações mínimas e coerência entre cargos
python 06_espacial.py              # validação espacial, Moran, modelos espaciais
```

Os caminhos podem ser alterados pelas variáveis de ambiente `ELEICOES_DADOS` e `ELEICOES_RESULTADOS`.

## Fontes e créditos

Tribunal Superior Eleitoral: boletins de urna de 2022 (portal de dados abertos). John Robson, repositório [JohnRobson/Eleicoes2022](https://github.com/JohnRobson/Eleicoes2022) (licença BSD 3-Clause, Copyright (c) 2022 John Robson): banco com o modelo de urna de cada seção, extraído dos logs publicados pelo TSE, do qual deriva a planilha `VOTOS_T1E2.xlsx`. F. Daniel Hidalgo e colaboradores, [geocode_br_polling_stations](https://github.com/fdhidalgo/geocode_br_polling_stations), versão 0.16: coordenadas dos locais de votação. IPEA, [geobr](https://github.com/ipeaGIT/geobr): polígonos municipais, locais de votação e manchas urbanas de 2022. Referência metodológica: Ole J. Forsberg, *Understanding Elections through Statistics: Polling, Prediction, and Testing* (Chapman & Hall/CRC, 2021), capítulos 6 a 8.

## Licença

Código (`scripts/`): MIT (`LICENSE`). Textos (`docs/` e demais documentos): CC BY 4.0 (`LICENSE-docs.md`). Os dados de terceiros seguem as licenças das respectivas fontes.
