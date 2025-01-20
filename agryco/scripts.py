import os
import subprocess
import argparse

parse = argparse.ArgumentParser(description="Lancer un spider Scrapy.")
parse.add_argument('--output', type=str, default='jsonl')
args = parse.parse_args()

def category():
    # Changez de répertoire vers le dossier où se trouve votre projet Scrapy si necessaire
    # os.chdir('scrapy_app/spiders')
    subprocess.run(['scrapy', 'crawl', 'category', '-O', f'scrapy_app/spiders/output/category.{args.output}'])


def sub_category():
    subprocess.run(['scrapy', 'crawl', 'sub_category', '-O', f'scrapy_app/spiders/output/sub_category.{args.output}'])


def product():
    subprocess.run(['scrapy', 'crawl', 'product', '-O', f'scrapy_app/spiders/output/product.{args.output}'])
