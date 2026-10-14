# Plataforma CAPES — Base de Conhecimento

Base de conhecimento minimalista sobre a pós-graduação stricto sensu brasileira,
construída a partir dos [dados abertos da CAPES](https://dadosabertos.capes.gov.br),
organizada em módulos (conceitos → EDA → insights → indicadores documentados).

## Arquitetura

```
CKAN API ──ingest──▶ data/raw (CSV cp1252) ──bronze──▶ data/bronze (Parquet, VARCHAR)
        ──dbt-duckdb──▶ staging/marts ──export──▶ data/capes_kb.sqlite ──Quarto──▶ site estático
```

- **raw**: CSVs originais, nunca editados. Checksums em `data/manifest/raw.json`.
- **bronze**: Parquet 1:1 com a fonte (todas as colunas texto + `_ano`, `_resource_id`),
  particionado em `data/bronze/<dataset>/ano=<AAAA>/`. Registro em `data/manifest/bronze.json`.
- **staging/marts** (próxima fase): tipagem, harmonização entre períodos e indicadores via dbt.

Os dados (`data/raw`, `data/bronze`) não são versionados; os manifests são.

## Uso

Requer [uv](https://docs.astral.sh/uv/). Python 3.12 (dbt ainda não suporta 3.14).

```bash
uv sync
uv run capes all programas        # baixa, converte e mostra o perfil
uv run capes ingest               # todos os datasets de config/datasets.yml
uv run capes perfil discentes     # registros por ano e colunas que mudam entre anos
uv run pytest                     # testes unitários (offline)
```

Datasets e períodos ficam em [config/datasets.yml](config/datasets.yml).
