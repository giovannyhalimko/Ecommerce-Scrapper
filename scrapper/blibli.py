from requests import request
import time
from util import display_progress, write_to_excel

page = 1
products = []

def scrape():
    global page
    global products
    global query
    base_url = 'https://www.blibli.com/backend/search/products?page=' + str(page) + '&start=0&searchTerm=' + query
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
            })
    else:
        print('Failed to fetch page ' + str(page))

    page += 1

    time.sleep(0.5)

while True:
    query = input('What do you want to search ? : ')
    if not query:
        print('Query cannot be empty')
        continue

    max_page = int(input('How many page you want to fetch ? (max 100): '))
    if max_page > 100:
        print('Max page is 100')
        continue
    break
        
while page <= max_page:
    scrape()
    display_progress(page, max_page, 100)

write_to_excel(products, '../data/blibli.xlsx')

print("\nScrapping Finished!")