from requests import request
import time
from .util import display_progress, write_to_excel

products = []

def scrape(phrase, page):
    global products
    base_url = 'https://www.blibli.com/backend/search/products?page=' + str(page) + '&start=0&searchTerm=' + phrase
    response = request('GET', base_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    })

    if response.status_code == 200:
        data = response.json()

        for product in data['data']['products']:
            products.append({
                'id': product['id'],
                'name': product['name'],
                'category': product["rootCategory"]["name"],
                'brand': product['brand'],
                'price': product['price']["minPrice"],
                'image_url': product['images'][0],
                'rating': product['review']['absoluteRating'],
                'url': 'https://www.blibli.com' + product['url'],
            })
    else:
        print('Failed to fetch page ' + str(page))

def scrape_blibli(max_page, phrase):
    page = 1
    
    while page <= max_page:
        scrape(phrase, page)
        display_progress(page, max_page, 100)

        page += 1

        time.sleep(0.5)
        
    write_to_excel(products, './ui_data/blibli.xlsx')

    products.clear()

    print("\nScrapping Finished Blibli!")