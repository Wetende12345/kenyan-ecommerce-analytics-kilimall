from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import hashlib
import psycopg2
from datetime import date

# Selenium setup - VISIBLE BROWSER (no headless for reliability)
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.binary_location = '/usr/bin/chromium-browser'  # System chromium

# Common path for chromedriver on Ubuntu
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.binary_location = '/usr/bin/chromium-browser'

service = Service('/usr/lib/chromium-browser/chromedriver')  # Change if your find shows different
driver = webdriver.Chrome(service=service, options=options)
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.kilimall.co.ke/new/commoditysearch?sort=0"
driver.get(url)

print("Browser opened — loading Kilimall. Wait for products...")

try:
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.goods-item, div.product-item, .listing-item"))
    )
    print("Products detected!")
except:
    print("Timeout — saving screenshot for debug")
    driver.save_screenshot('debug.png')
    driver.quit()
    exit()

# Scroll to load more
for _ in range(10):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    print("Scrolling...")
    time.sleep(4)

print("Parsing HTML...")
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

products = []
items = soup.find_all('div', class_='goods-item') + \
        soup.find_all('div', class_='product-item') + \
        soup.find_all('div', class_='listing-item') + \
        soup.find_all('article')

print(f"Found {len(items)} product containers")

for item in items[:60]:
    name = item.find('a') or item.find('h3') or item.find('div', class_='title')
    price = item.find(string=lambda text: text and 'KSh' in text)
    link = item.find('a', href=True)

    if name and price and link:
        name_text = name.text.strip() or name.get('title', '').strip()
        price_text = price.strip().replace('KSh', '').replace(',', '').strip()
        try:
            price_float = float(price_text)
        except:
            continue
        
        link_href = link['href']
        if not link_href.startswith('http'):
            link_href = 'https://www.kilimall.co.ke' + link_href
        
        products.append({
            'name': name_text[:300],
            'price': price_float,
            'link': link_href,
            'category': 'Unknown'
        })

print(f"Scraped {len(products)} products from Kilimall on {date.today()}")

# DB Connection (peer auth)
conn = psycopg2.connect(dbname="kilimall_dw", user="denwetende", host="localhost", port="5432")
cur = conn.cursor()

cur.execute("INSERT INTO dim_scrape_run (scrape_date, products_scraped) VALUES (CURRENT_DATE, %s) RETURNING scrape_run_sk", (len(products),))
scrape_run_sk = cur.fetchone()[0]

cur.execute("SELECT date_sk FROM dim_date WHERE full_date = CURRENT_DATE")
date_sk = cur.fetchone()[0]

for product in products:
    nk = hashlib.md5(product['link'].encode()).hexdigest()
    
    cur.execute("SELECT category_sk FROM dim_category WHERE category_name = %s", (product['category'],))
    row = cur.fetchone()
    if row:
        category_sk = row[0]
    else:
        cur.execute("INSERT INTO dim_category (category_name) VALUES (%s) RETURNING category_sk", (product['category'],))
        category_sk = cur.fetchone()[0]
    
    cur.execute("SELECT product_sk FROM dim_product WHERE product_nk = %s AND is_current = TRUE", (nk,))
    current = cur.fetchone()
    if not current:
        cur.execute("INSERT INTO dim_product (product_nk, name, category) VALUES (%s, %s, %s) RETURNING product_sk", (nk, product['name'], product['category']))
        product_sk = cur.fetchone()[0]
    else:
        product_sk = current[0]
    
    cur.execute("""
        INSERT INTO fact_product_snapshot (product_sk, scrape_run_sk, date_sk, category_sk, price_ksh, link)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (product_sk, scrape_run_sk, date_sk, category_sk, product['price'], product['link']))

conn.commit()
conn.close()
print("Kilimall data loaded — warehouse LIVE!")
