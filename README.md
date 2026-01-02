# Kenyan E-commerce Analytics Warehouse — Kilimall Edition

A complete data warehouse for analyzing Kilimall Kenya product data (prices, categories, trends).

## Features
- Daily web scraping with Selenium (handles JavaScript-heavy site)
- Star schema with SCD Type 2 for product history (track price/name changes)
- PostgreSQL database
- Ready for Airflow orchestration
- Analytics queries for price trends, category insights

## Setup
1. Clone repo
2. Create virtual env: `python3 -m venv venv && source venv/bin/activate`
3. Install deps: `pip install selenium beautifulsoup4 psycopg2-binary`
4. Install Chromium: `sudo apt install chromium-browser chromium-chromedriver`
5. Run scraper: `python etl/scrape_and_load.py`
6. Query in psql: `sudo -u postgres psql -d kilimall_dw`

## Project Structure
- `schema/` — CREATE TABLE SQL
- `etl/` — Scraper + loader
- `queries/` — Analytics SQL

Built by Eden Wetende — January 2026

GitHub: https://github.com/Wetende12345/kenyan-ecommerce-analytics-kilimall
