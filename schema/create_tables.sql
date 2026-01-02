-- dim_date (populate 2025-2026)
CREATE TABLE dim_date (
    date_sk SERIAL PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    quarter INT NOT NULL,
    weekday_name VARCHAR(20) NOT NULL
);

-- Insert loop (same as Jumia, but for 2026 too)
DO $$
DECLARE
    start_date DATE := '2025-01-01';
    end_date DATE := '2026-12-31';
    current_date DATE := start_date;
BEGIN
    WHILE current_date <= end_date LOOP
        INSERT INTO dim_date (full_date, year, month, day, quarter, weekday_name)
        VALUES (
            current_date,
            EXTRACT(YEAR FROM current_date),
            EXTRACT(MONTH FROM current_date),
            EXTRACT(DAY FROM current_date),
            EXTRACT(QUARTER FROM current_date),
            TO_CHAR(current_date, 'Day')
        );
        current_date := current_date + INTERVAL '1 day';
    END LOOP;
END $$;

-- dim_category (Type 1)
CREATE TABLE dim_category (
    category_sk SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    parent_category VARCHAR(100)
);

-- dim_scrape_run
CREATE TABLE dim_scrape_run (
    scrape_run_sk SERIAL PRIMARY KEY,
    scrape_date DATE NOT NULL,
    products_scraped INT,
    status VARCHAR(20) DEFAULT 'Success'
);

-- dim_product (SCD Type 2)
CREATE TABLE dim_product (
    product_sk SERIAL PRIMARY KEY,
    product_nk VARCHAR(255) NOT NULL,  -- MD5 of link
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(100),
    category VARCHAR(100),
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    version INT NOT NULL DEFAULT 1
);

-- fact_product_snapshot
CREATE TABLE fact_product_snapshot (
    snapshot_id BIGSERIAL PRIMARY KEY,
    product_sk INT REFERENCES dim_product(product_sk),
    scrape_run_sk INT REFERENCES dim_scrape_run(scrape_run_sk),
    date_sk INT REFERENCES dim_date(date_sk),
    category_sk INT REFERENCES dim_category(category_sk),
    price_ksh DECIMAL(12, 2) NOT NULL,
    original_price_ksh DECIMAL(12, 2),
    discount_percent DECIMAL(5, 2),
    link TEXT NOT NULL,
    in_stock BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_fact_product ON fact_product_snapshot(product_sk);
CREATE INDEX idx_fact_date ON fact_product_snapshot(date_sk);
CREATE INDEX idx_product_nk ON dim_product(product_nk);
