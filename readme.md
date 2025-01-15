# READ-ME

## Install project use this command :

```bash
poetry install
```
## Install scrapy use this command :

```bash
poetry run scrapy startproject <project_scrapy_name> .
```

## Run containers docker use this command :

```bash
docker compose up -d
```

and close with :
```bash
docker compose down
```

## Generate jsonl file use this command :

```bash
poetry run scrapy crawl category -O <project_scrapy_name>/spiders/output/category.jsonl
```

```bash
poetry run scrapy crawl sub_category -O <project_scrapy_name>/spiders/output/sub_category.jsonl
```

```bash
poetry run scrapy crawl product -O <project_scrapy_name>/spiders/output/product.jsonl
```