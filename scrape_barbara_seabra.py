#!/usr/bin/env python3
"""Faz web scraping de todos os artigos da categoria da Bárbara Seabra.

O script percorre automaticamente as páginas de paginação:
- /category/artigos/barbara-seabra/
- /category/artigos/barbara-seabra/page/2/
- /page/3/ ...

E coleta metadados básicos de cada artigo.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from dataclasses import asdict, dataclass
from typing import Iterable

import requests
from bs4 import BeautifulSoup

BASE_CATEGORY_URL = "https://www.pontodevistaonline.com.br/category/artigos/barbara-seabra/"


@dataclass
class Article:
    title: str
    url: str
    date: str | None = None
    excerpt: str | None = None


def build_page_url(page: int) -> str:
    if page < 1:
        raise ValueError("O número da página deve ser maior ou igual a 1.")
    if page == 1:
        return BASE_CATEGORY_URL
    return f"{BASE_CATEGORY_URL}page/{page}/"


def fetch_html(url: str, timeout: int = 30) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_articles_from_page(html: str) -> list[Article]:
    soup = BeautifulSoup(html, "html.parser")

    # Estrutura comum em temas WordPress para listas de posts.
    article_nodes = soup.select("article")
    parsed: list[Article] = []

    for node in article_nodes:
        title_link = node.select_one("h2 a, h3 a, .entry-title a")
        if not title_link or not title_link.get("href"):
            continue

        title = " ".join(title_link.get_text(strip=True).split())
        url = title_link["href"].strip()
        if not title or not url:
            continue

        date_node = node.select_one("time")
        excerpt_node = node.select_one(".entry-summary, .entry-content, p")

        parsed.append(
            Article(
                title=title,
                url=url,
                date=(date_node.get("datetime") or date_node.get_text(strip=True))
                if date_node
                else None,
                excerpt=excerpt_node.get_text(" ", strip=True) if excerpt_node else None,
            )
        )

    # Remove duplicados mantendo ordem.
    seen: set[str] = set()
    unique: list[Article] = []
    for item in parsed:
        if item.url in seen:
            continue
        seen.add(item.url)
        unique.append(item)

    return unique


def scrape_all_articles(start_page: int = 1, delay_seconds: float = 0.5, max_pages: int | None = None) -> list[Article]:
    all_articles: list[Article] = []
    seen_urls: set[str] = set()

    page = start_page
    while True:
        if max_pages is not None and (page - start_page) >= max_pages:
            break

        page_url = build_page_url(page)
        print(f"Coletando: {page_url}")

        try:
            html = fetch_html(page_url)
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response else None
            if status == 404:
                print(f"Fim da paginação (404 na página {page}).")
                break
            raise

        page_articles = parse_articles_from_page(html)
        if not page_articles:
            print(f"Nenhum artigo encontrado na página {page}. Encerrando.")
            break

        new_count = 0
        for article in page_articles:
            if article.url in seen_urls:
                continue
            seen_urls.add(article.url)
            all_articles.append(article)
            new_count += 1

        print(f"Página {page}: {len(page_articles)} encontrados, {new_count} novos.")

        page += 1
        time.sleep(delay_seconds)

    return all_articles


def save_csv(articles: Iterable[Article], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["title", "url", "date", "excerpt"])
        writer.writeheader()
        for article in articles:
            writer.writerow(asdict(article))


def save_json(articles: Iterable[Article], output_path: str) -> None:
    payload = [asdict(a) for a in articles]
    with open(output_path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scraper de artigos da Bárbara Seabra")
    parser.add_argument("--start-page", type=int, default=1, help="Página inicial da coleta")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limite de páginas para coletar (padrão: sem limite)",
    )
    parser.add_argument("--delay", type=float, default=0.5, help="Atraso entre páginas (segundos)")
    parser.add_argument("--csv", default="barbara_seabra_artigos.csv", help="Arquivo CSV de saída")
    parser.add_argument("--json", default="barbara_seabra_artigos.json", help="Arquivo JSON de saída")

    args = parser.parse_args()

    artigos = scrape_all_articles(
        start_page=args.start_page,
        delay_seconds=args.delay,
        max_pages=args.max_pages,
    )

    save_csv(artigos, args.csv)
    save_json(artigos, args.json)

    print(f"Total de artigos únicos coletados: {len(artigos)}")
    print(f"CSV salvo em: {args.csv}")
    print(f"JSON salvo em: {args.json}")


if __name__ == "__main__":
    main()
