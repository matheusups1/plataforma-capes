# Plataforma CAPES — Base de Conhecimento

Base de conhecimento minimalista sobre a pós-graduação stricto sensu brasileira,
construída a partir dos [Dados Abertos da CAPES](https://dadosabertos.capes.gov.br),
organizada em módulos (conceitos → EDA → insights → indicadores documentados).

## Arquitetura

```
CKAN API ──ingest──▶ data/raw (CSV cp1252) ──bronze──▶ data/bronze (Parquet, VARCHAR)──dbt-duckdb──▶ staging/marts ──export──▶ data/capes_kb.sqlite ──Quarto──▶ site estático
```

- **raw**: CSVs originais, nunca editados. Checksums em `data/manifest/raw.json`.
- **bronze**: Parquet 1:1 com a fonte (todas as colunas texto + `_ano`, `_resource_id`),
  particionado em `data/bronze/<dataset>/ano=<AAAA>/`. Registro em `data/manifest/bronze.json`.
- **staging** (`transform/models/staging`, views dbt): tipagem, harmonização entre períodos,
  deduplicação e remoção de dados pessoais.
- **marts** (`transform/models/marts`, tabelas localizadas no database `data/capes.duckdb`): dimensões e fatos.
  Testes de qualidade e de coerência entre fontes rodam no `dbt build`.
- **indicadores**: catálogo em [indicators/indicadores.yml](indicators/indicadores.yml)
  (fonte única da documentação) → `mart_indicador_valor` (indicador × ano × recorte).
- **publicação**: `data/capes_kb.sqlite` só com agregados e o catálogo; lido pelo site
  Quarto em `site/` (saída em `site/_site`).

Os dados (`data/raw`, `data/bronze`, `*.duckdb`, `*.sqlite`) não são versionados; os manifests são.

## Uso

Requer [uv](https://docs.astral.sh/uv/). Python 3.12.

```bash
uv sync
uv run capes all programas        # baixa, converte e mostra o perfil
uv run capes ingest               # todos os datasets de config/datasets.yml
uv run capes perfil discentes     # registros por ano e colunas que mudam entre anos
uv run capes transform            # dbt build: modelos + testes
uv run capes transform -- docs generate   # qualquer comando dbt após --
uv run capes export               # marts → data/capes_kb.sqlite
uv run capes site                 # renderiza o site (Quarto instalado via uv, no .venv)
uv run capes site -- preview      # servidor local com recarga
uv run pytest                     # testes unitários (offline)
```

Datasets e períodos ficam em [config/datasets.yml](config/datasets.yml).

## Publicação (GitHub Actions + Pages)

| Workflow | Quando roda | O que faz |
|---|---|---|
| [`ci.yml`](.github/workflows/ci.yml) | cada PR e push em `main` | testes (pytest) e `dbt parse` — sem baixar dados |
| [`publicar.yml`](.github/workflows/publicar.yml) | dia 5 de cada mês e sob demanda | pipeline completo (~7 GB do portal), `dbt build`, export, Quarto e deploy no GitHub Pages |

O SQLite publicado e os manifests de cada execução ficam como artefatos do workflow (90 dias).
No runner, os CSVs de cada dataset são apagados logo após virar Parquet (`capes all --limpar-raw`).

