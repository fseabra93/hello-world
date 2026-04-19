# hello-world
Repositório teste de Flávio Seabra
Apenas tentando aprender a usar isso

## Web scraping de artigos da Bárbara Seabra

Criei o script `scrape_barbara_seabra.py` para coletar **todos** os artigos da categoria:

- `https://www.pontodevistaonline.com.br/category/artigos/barbara-seabra/`
- `.../page/2/`, `.../page/3/`, e assim por diante

O script avança automaticamente pelas páginas até não haver mais resultados (ou até receber 404) e salva os dados em CSV e JSON.

### Requisitos

```bash
pip install requests beautifulsoup4
```

### Como executar

```bash
python3 scrape_barbara_seabra.py
```

Saídas padrão:

- `barbara_seabra_artigos.csv`
- `barbara_seabra_artigos.json`

### Opções úteis

```bash
python3 scrape_barbara_seabra.py --start-page 1 --delay 0.5
python3 scrape_barbara_seabra.py --max-pages 3
python3 scrape_barbara_seabra.py --csv meus_artigos.csv --json meus_artigos.json
```
